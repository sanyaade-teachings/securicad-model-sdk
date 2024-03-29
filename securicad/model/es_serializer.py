# Copyright 2021-2022 Foreseeti AB <https://foreseeti.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json
import random
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional

from securicad.langspec import AttackStepType, TtcDistribution, TtcFunction

from . import utility
from .attacker import Attacker
from .exceptions import LangException
from .meta import meta_validator

if TYPE_CHECKING:  # pragma: no cover
    from securicad.langspec import Lang

    from .association import Association
    from .attackstep import AttackStep
    from .model import Model
    from .visual.container import Container
    from .visual.group import Group
    from .visual.viewobject import ViewObject

PARAMETERS: dict[TtcDistribution, Callable[[list[float]], list[float]]] = {
    TtcDistribution.EXPONENTIAL: lambda parameters: [1 / parameters[0]],
    TtcDistribution.TRUNCATED_NORMAL: lambda parameters: [parameters[1], parameters[0]],
    TtcDistribution.GAMMA: lambda parameters: [parameters[0], parameters[1]],
    TtcDistribution.LOG_NORMAL: lambda parameters: [parameters[1], parameters[0]],
    TtcDistribution.PARETO: lambda parameters: [parameters[1], parameters[0]],
    TtcDistribution.BINOMIAL: lambda parameters: [parameters[0], parameters[1]],
    TtcDistribution.BERNOULLI: lambda parameters: [parameters[0]],
    TtcDistribution.INFINITY: lambda parameters: [],
}


def serialize_attack_step(attack_step: AttackStep):
    data = {
        "name": utility.uc_first(attack_step.name),
        "consequence": attack_step.meta.get("consequence", 0) or None,
        "uppercost": attack_step.meta.get("costUpperLimit", 0) or None,
        "lowercost": attack_step.meta.get("costLowerLimit", 0) or None,
    }
    if attack_step.ttc is not None:
        assert isinstance(attack_step.ttc, TtcFunction)
        data["distribution"] = ",".join(
            [attack_step.ttc.distribution.value]
            + [
                format(Decimal(str(parameter)), "f")
                for parameter in PARAMETERS[attack_step.ttc.distribution](
                    attack_step.ttc.arguments
                )
            ]
        )
    else:
        data["distribution"] = None
    return data


def serialize_link(model: Model, association: Association) -> str | None:
    if not model._lang:
        return None
    if association.source_object.asset_type == "Attacker":
        return None
    return (
        model._lang.assets[association.source_object.asset_type]
        .fields[association.source_field]
        .association.name
    )


def serialize_nodes(nodes: Iterable[ViewObject | Group]):
    return {
        str(utility.id_pad(node.id)): {"x": int(node.x), "y": int(node.y)}
        for node in nodes
    }


def serialize_model(model: Model, *, sort: bool = False) -> dict[str, Any]:
    def sort_dict_list(associations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(associations, key=json.dumps) if sort else associations

    def get_metadata() -> dict[str, str]:
        meta = {
            "scadVersion": "1.0.0",
            "info": "Created in securiCAD model SDK",
            "langVersion": model.meta["langVersion"],
            "langID": model.meta["langId"],
        }
        if model.meta["langId"] != "com.foreseeti.securilang":
            meta["malVersion"] = "0.1.0-SNAPSHOT"
        return meta

    meta_validator.validate_model(model)
    return {
        "formatversion": 1,
        "mid": model.meta.get("mid", str(random.randint(10**9, 10**25 - 1))),
        "name": model.name,
        "samples": model.meta.get("samples", 1000),
        "threshold": model.meta.get("warningThreshold", 100),
        "default": {},
        "metadata": get_metadata(),
        "tags": model.meta.get("tags", {}),
        "objects": {
            str(utility.id_pad(obj.id)): {
                "name": obj.name,
                "metaconcept": obj.asset_type,
                "eid": obj.id,
                "tags": obj.meta.get("tags", {}),
                "attacksteps": [
                    serialize_attack_step(attack_step)
                    for attack_step in obj._attack_steps.values()
                    if not attack_step.is_default
                ],
                "defenses": [
                    {
                        "name": utility.uc_first(defense.name),
                        "probability": defense.probability,
                    }
                    for defense in obj._defenses.values()
                    if not defense.is_default
                ],
            }
            for obj in model._objects.values()
        },
        "associations": sort_dict_list(
            [
                {  # in ES the id1.type2 is connected to id2.type1
                    "id1": str(utility.id_pad(association.source_object.id)),
                    "id2": str(utility.id_pad(association.target_object.id)),
                    "link": serialize_link(model, association),
                    "type2": association.source_field,
                    "type1": association.target_field,
                }
                for association in model._associations
            ]
        ),
        "groups": {
            str(utility.id_pad(group.id)): {
                "name": group.name,
                "description": group.meta.get("description", ""),
                "icon": group.icon,
                "color": group.meta.get("color", ""),
                "expand": group.meta.get("expand", False),
                "tags": group.meta.get("tags", {}),
                "objects": serialize_nodes(
                    [*group._objects.values(), *group._groups.values()]
                ),
            }
            for view in model._views.values()
            for group in view.groups()
        },
        "views": [
            {
                "name": view.name,
                "objects": serialize_nodes(view._objects.values()),
                "groups": serialize_nodes(view._groups.values()),
                "load_on_start": view.meta.get("loadOnStart", True),
            }
            for view in model._views.values()
        ],
    }


def deserialize_model(
    data: dict[str, Any],
    *,
    lang: Optional[Lang] = None,
    lowercase_attack_step: bool = True,
    validate_icons: bool = True,
) -> Model:
    from .model import Model

    if lang:
        utility.verify_lang(
            lang=lang,
            lang_id=data["metadata"]["langID"],
            lang_version=data["metadata"]["langVersion"],
        )

    model = Model(
        data["name"] or "unnamed",
        lang=lang,
        lang_id=data["metadata"]["langID"],
        lang_version=data["metadata"]["langVersion"],
        validate_icons=validate_icons,
    )

    model.meta = {
        **model.meta,
        "samples": data["samples"],
        "warningThreshold": data["threshold"],
        "tags": data["tags"],
    }

    if "mid" in data:
        model.meta["mid"] = data["mid"]

    id_exported_id: dict[str, int] = {}
    for object_id, object_data in data["objects"].items():
        if (
            lang
            and lang.defines["id"] == "com.foreseeti.securilang"
            and object_data["metaconcept"] == "Container"
        ):
            continue
        id_exported_id[object_id] = object_data["eid"]
        if object_data["metaconcept"] == "Attacker":
            obj = model.create_attacker(
                object_data["name"],
                id=object_data["eid"],
                meta={"tags": object_data["tags"]},
            )
        else:
            obj = model.create_object(
                object_data["metaconcept"],
                object_data["name"],
                id=object_data["eid"],
                meta={"tags": object_data["tags"]},
            )

            attack_lookup = utility.attack_step_lookup(
                object_data["metaconcept"],
                lang,
                lowercase_attack_step,
                (AttackStepType.AND, AttackStepType.OR),
            )
            defense_lookup = utility.attack_step_lookup(
                object_data["metaconcept"],
                lang,
                lowercase_attack_step,
                (AttackStepType.DEFENSE,),
            )

            for attack_step_data in object_data["attacksteps"]:
                attack_step = obj.attack_step(attack_lookup(attack_step_data["name"]))
                attack_step.meta = {
                    "costUpperLimit": attack_step_data.get("uppercost") or 0,
                    "costLowerLimit": attack_step_data.get("lowercost") or 0,
                    "consequence": attack_step_data.get("consequence") or 0,
                }
                if attack_step_data["distribution"] is not None:
                    name, *parameters = attack_step_data["distribution"].split(",")
                    attack_step.ttc = TtcFunction(
                        TtcDistribution(name),
                        PARAMETERS[TtcDistribution(name)](
                            [float(parameter) for parameter in parameters]
                        ),
                    )

            for defense_data in object_data["defenses"]:
                defense = obj.defense(defense_lookup(defense_data["name"]))
                defense.probability = defense_data["probability"]

    # FIXME: Clean this up when securilang is retired
    queue: list[dict[str, Any]] = list(data["associations"])
    assoc_was_added = True
    while queue and assoc_was_added:
        last_exc: Optional[LangException] = None
        assoc_was_added = False
        assocs_added: list[dict[str, Any]] = []

        # first try to create any remaining to-be-created-assoc
        for que_obj in queue:
            try:
                # in ES the id1.type2 is connected to id2.type1
                source_object = model.object(id_exported_id[que_obj["id1"]])
                target_object = model.object(id_exported_id[que_obj["id2"]])
                if isinstance(source_object, Attacker):
                    step = que_obj["type1"].split(".")[0]
                    source_object.connect(target_object.attack_step(step))
                elif isinstance(target_object, Attacker):
                    step = que_obj["type2"].split(".")[0]
                    target_object.connect(source_object.attack_step(step))
                else:
                    source_object.field(que_obj["type2"]).connect(
                        target_object.field(que_obj["type1"])
                    )
                assoc_was_added = True
                assocs_added.append(que_obj)
            except LangException as ex:
                last_exc = ex  # try next assoc

        # then raise if we can't add any
        if not assoc_was_added:
            # no new association added, raise last exc which probably is relevant
            assert last_exc is not None
            raise last_exc

        # last remove the created ones from the attempt queue
        for assoc in assocs_added:
            queue.remove(assoc)

    def create_group(container: Container, group_id: int, x: float, y: float):
        group_data = data["groups"][str(group_id)]
        group = container.create_group(
            group_data["name"],
            group_data["icon"] or "Icon",
            x,
            y,
            id=int(group_id),
        )
        group.meta = {
            "description": group_data["description"],
            "expand": group_data["expand"],
            "tags": group_data["tags"],
        }
        if group_data["color"]:
            group.meta["color"] = group_data["color"]
        for object_id, node_data in group_data["objects"].items():
            if object_id in id_exported_id:
                group.add_object(
                    model.object(id_exported_id[object_id]),
                    node_data["x"],
                    node_data["y"],
                )
            else:
                create_group(group, int(object_id), node_data["x"], node_data["y"])

    for view_data in data["views"]:
        view = model.create_view(view_data["name"])
        view.meta = {"loadOnStart": view_data.get("load_on_start", True)}
        for object_id, node_data in view_data["objects"].items():
            if object_id not in id_exported_id:
                continue
            view.add_object(
                model.object(id_exported_id[object_id]),
                node_data["x"],
                node_data["y"],
            )
        for group_id, node_data in view_data["groups"].items():
            create_group(view, int(group_id), node_data["x"], node_data["y"])

    return model
