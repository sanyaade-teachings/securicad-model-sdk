# Copyright 2021 Foreseeti AB <https://foreseeti.com>
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

import base64
import importlib.resources
import json
import typing
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Optional, Type

import jsonschema

from securicad.langspec import (
    Lang,
    TtcAddition,
    TtcBinaryOperation,
    TtcDistribution,
    TtcDivision,
    TtcExponentiation,
    TtcExpression,
    TtcFunction,
    TtcMultiplication,
    TtcNumber,
    TtcSubtraction,
)

from .attacker import Attacker
from .visual.container import Container

if TYPE_CHECKING:  # pragma: no cover
    from .model import Model


@lru_cache(1)
def read_schema() -> dict[str, Any]:
    with importlib.resources.open_binary("securicad.model", "model.schema.json") as fp:
        return json.load(fp)


def validate_model_data(data: dict[str, Any]):
    jsonschema.validate(data, read_schema())


def serialize_container(container: Container) -> dict[str, Any]:
    return {
        "meta": container.meta,
        "id": container.id,
        "name": container.name,
        "items": typing.cast(
            "list[Any]",
            [
                {
                    "meta": obj.meta,
                    "id": obj.id,
                    "x": obj.x,
                    "y": obj.y,
                    "type": "object",
                }
                for obj in container._objects.values()
            ],
        )
        + typing.cast(
            "list[Any]",
            [
                {
                    **serialize_container(group),
                    "x": group.x,
                    "y": group.y,
                    "icon": group.icon,
                    "type": "group",
                }
                for group in container._groups.values()
            ],
        ),
    }


def deserialize_items(
    model: Model, container: Container, items: list[dict[str, Any]]
) -> None:
    for item in items:
        if item["type"] == "object":
            obj = container.add_object(model.object(item["id"]), item["x"], item["y"])
            obj.meta = item["meta"]
        elif item["type"] == "group":
            group = container.create_group(
                item["name"], item["icon"], item["x"], item["y"], id=item["id"]
            )
            group.meta = item["meta"]
            deserialize_items(model, group, item["items"])
        else:  # pragma: no cover
            raise RuntimeError(f"invalid item type {item['type']}")


def serialize_ttc(ttc: TtcExpression) -> dict[str, Any]:
    if isinstance(ttc, TtcBinaryOperation):
        return {
            "type": ttc.__class__.__name__.lower()[3:],
            "lhs": serialize_ttc(ttc.lhs),
            "rhs": serialize_ttc(ttc.rhs),
        }
    elif isinstance(ttc, TtcNumber):
        return {"type": "number", "value": ttc.value}
    elif isinstance(ttc, TtcFunction):
        return {
            "type": "function",
            "name": ttc.distribution.value,
            "arguments": ttc.arguments,
        }
    raise RuntimeError(f"{ttc} couldn't be serialized")


def deserialize_ttc(data: dict[str, Any]) -> TtcExpression:
    binary_expressions: dict[str, Type[TtcBinaryOperation]] = {
        "subtraction": TtcSubtraction,
        "addition": TtcAddition,
        "multiplication": TtcMultiplication,
        "exponentiation": TtcExponentiation,
        "division": TtcDivision,
    }
    if data["type"] in binary_expressions:
        return binary_expressions[data["type"]](
            deserialize_ttc(data["lhs"]), deserialize_ttc(data["rhs"])
        )
    elif data["type"] == "number":
        return TtcNumber(data["value"])
    elif data["type"] == "function":
        return TtcFunction(TtcDistribution(data["name"]), data["arguments"])
    else:  # pragma: no cover
        raise RuntimeError(f"{data} couldn't be deserialized")


def serialize_model(model: Model, *, sort: bool = False) -> dict[str, Any]:
    def sort_dict_list(associations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(associations, key=json.dumps) if sort else associations

    data = {
        "name": model.name,
        "meta": model.meta,
        "objects": [
            {
                "meta": obj.meta,
                "id": obj.id,
                "name": obj.name,
                "asset_type": obj.asset_type,
                "attack_steps": [
                    {
                        "meta": attack_step.meta,
                        "name": attack_step.name,
                        "ttc": None
                        if attack_step.ttc is None
                        else serialize_ttc(attack_step.ttc),
                    }
                    for attack_step in obj._attack_steps.values()
                    if not attack_step.is_default
                ],
                "defenses": [
                    {
                        "meta": defense.meta,
                        "name": defense.name,
                        "probability": None
                        if defense.probability is None
                        else defense.probability,
                    }
                    for defense in obj._defenses.values()
                    if not defense.is_default
                ],
            }
            for obj in model._objects.values()
        ],
        "associations": sort_dict_list(
            [
                {
                    "meta": association.meta,
                    "source_object_id": association.source_object.id,
                    "source_field": association.source_field,
                    "target_object_id": association.target_object.id,
                    "target_field": association.target_field,
                }
                for association in model._associations
            ]
        ),
        "views": [serialize_container(view) for view in model._views.values()],
        "icons": [
            {
                "name": icon.name,
                "license": icon.license,
                "data": base64.b64encode(icon.data).decode("utf-8"),
                "format": icon.format,
                "meta": icon.meta,
            }
            for icon in model._icons.values()
        ],
    }
    validate_model_data(data)
    return data


def deserialize_model(
    data: dict[str, Any], *, lang: Optional[Lang] = None, validate_icons: bool = True
) -> Model:
    from .model import Model

    validate_model_data(data)
    model = Model(
        data["name"],
        lang=lang,
        lang_id=data["meta"]["langId"],
        lang_version=data["meta"]["langVersion"],
        validate_icons=validate_icons,
    )
    model.meta = data["meta"]

    for o_data in data["objects"]:
        if o_data["asset_type"] == "Attacker":
            model.create_attacker(o_data["name"], id=o_data["id"], meta=o_data["meta"])
        else:
            obj = model.create_object(
                o_data["asset_type"],
                o_data["name"],
                id=o_data["id"],
                meta=o_data["meta"],
            )
            for a_data in o_data["attack_steps"]:
                attack_step = obj.attack_step(a_data["name"])
                attack_step.meta = a_data["meta"]
                if a_data["ttc"] is not None:
                    attack_step.ttc = deserialize_ttc(a_data["ttc"])
            for d_data in o_data["defenses"]:
                defense = obj.defense(d_data["name"])
                defense.meta = d_data["meta"]
                defense.probability = d_data["probability"]

    for i_data in data["icons"]:
        icon = model.create_icon(
            i_data["name"],
            i_data["format"],
            base64.b64decode(i_data["data"]),
            i_data["license"],
        )
        icon.meta = i_data["meta"]

    for v_data in data["views"]:
        view = model.create_view(v_data["name"], id=v_data["id"])
        view.meta = v_data["meta"]
        deserialize_items(model, view, v_data["items"])

    for a_data in data["associations"]:
        source_object = model.object(a_data["source_object_id"])
        target_object = model.object(a_data["target_object_id"])
        if isinstance(source_object, Attacker):
            step = a_data["target_field"].split(".")[0]
            source_object.connect(target_object.attack_step(step))
        elif isinstance(target_object, Attacker):
            step = a_data["source_field"].split(".")[0]
            target_object.connect(source_object.attack_step(step))
        else:
            source_object.field(a_data["source_field"]).connect(
                target_object.field(a_data["target_field"])
            )

    return model
