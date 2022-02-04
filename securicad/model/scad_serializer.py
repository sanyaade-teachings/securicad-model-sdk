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
from io import BytesIO
from os import PathLike
from typing import IO, TYPE_CHECKING, Any, Callable, Generator, Optional
from zipfile import ZIP_DEFLATED, ZipFile

from pyecore.ecore import Core, EAttribute, EObject, EString
from pyecore.resources.resource import URI, ResourceSet
from pyecore.resources.xmi import XMIResource

from securicad.langspec import AttackStepType, Lang, TtcDistribution, TtcFunction

from . import ModelViewsPackage, ObjectModelPackage, utility
from .attacker import Attacker
from .meta import meta_validator

if TYPE_CHECKING:  # pragma: no cover
    from .attackstep import AttackStep
    from .base import Base
    from .defense import Defense
    from .model import Model
    from .object import Object
    from .visual.container import Container
    from .visual.group import Group


PARAMETERS_TO_SCAD: dict[TtcDistribution, Callable[[list[float]], dict[str, float]]] = {
    TtcDistribution.EXPONENTIAL: lambda parameters: {"mean": 1 / parameters[0]},
    TtcDistribution.TRUNCATED_NORMAL: lambda parameters: {
        "mean": parameters[0],
        "sd": parameters[1],
    },
    TtcDistribution.GAMMA: lambda parameters: {
        "shape": parameters[0],
        "scale": parameters[1],
    },
    TtcDistribution.LOG_NORMAL: lambda parameters: {
        "shape": parameters[1],
        "scale": parameters[0],
    },
    TtcDistribution.PARETO: lambda parameters: {
        "shape": parameters[1],
        "scale": parameters[0],
    },
    TtcDistribution.BINOMIAL: lambda parameters: {
        "trials": parameters[0],
        "p": parameters[1],
    },
    TtcDistribution.BERNOULLI: lambda parameters: {"probability": parameters[0]},
    TtcDistribution.INFINITY: lambda parameters: {},
}
PARAMETERS_FROM_SCAD: dict[
    TtcDistribution, Callable[[dict[str, float]], list[float]]
] = {
    TtcDistribution.EXPONENTIAL: lambda parameters: [1 / parameters["mean"]],
    TtcDistribution.TRUNCATED_NORMAL: lambda parameters: [
        parameters["mean"],
        parameters["sd"],
    ],
    TtcDistribution.GAMMA: lambda parameters: [
        parameters["shape"],
        parameters["scale"],
    ],
    TtcDistribution.LOG_NORMAL: lambda parameters: [
        parameters["scale"],
        parameters["shape"],
    ],
    TtcDistribution.PARETO: lambda parameters: [
        parameters["scale"],
        parameters["shape"],
    ],
    TtcDistribution.BINOMIAL: lambda parameters: [
        parameters["trials"],
        parameters["p"],
    ],
    TtcDistribution.BERNOULLI: lambda parameters: [parameters["probability"]],
    TtcDistribution.INFINITY: lambda parameters: [],
}

SECURILANG = "com.foreseeti.securilang"


# Dynamically changing generated classes is poorly documented. `register_classifier` is
# automatically called by the class' metaclass upon definition. This must be called manually to
# propagate any changes when later registering the eClass in a metamodel registry.
ObjectModelPackage.XMIObjectModel.xLang = EAttribute("xLang", EString)  # type: ignore
Core.register_classifier(ObjectModelPackage.XMIObjectModel, promote=True)  # type: ignore


class BytesURI(URI):
    def __init__(self, uri: str, data: Optional[bytes] = None):
        super().__init__(uri)  # type: ignore
        if data is not None:
            self.__stream = BytesIO(data)

    def getvalue(self):
        return self.__stream.getvalue()

    def create_instream(self):
        return self.__stream

    def create_outstream(self):
        self.__stream = BytesIO()
        return self.__stream


def serialize_ecore(instance: object) -> bytes:
    uri = BytesURI("instance")
    resource = XMIResource(uri)
    resource.append(instance)  # type: ignore
    resource.save()  # type:ignore
    return uri.getvalue()


def extract_attributes(base: Base, instance: EObject, attributes: set[str]):
    """Write non-default attributes to metadata"""
    for name in attributes:
        value = getattr(instance, name)
        definition = getattr(instance.__class__, name)
        if value != definition.get_default_value():  # type: ignore
            base.meta[name] = value


def is_default_attribute(instance: type, attribute: str) -> bool:
    value = getattr(instance, attribute)
    definition = getattr(instance.__class__, attribute)
    return value == definition.get_default_value()


def deserialize_model(
    file: str | PathLike[Any] | IO[bytes],
    *,
    lang: Optional[Lang] = None,
    lowercase_attack_step: bool = True,
    validate_icons: bool = True,
) -> Model:
    from .model import Model

    resources = ResourceSet()
    resources.metamodel_registry[ObjectModelPackage.eClass.nsURI] = ObjectModelPackage.eClass  # type: ignore
    resources.metamodel_registry[ModelViewsPackage.eClass.nsURI] = ModelViewsPackage.eClass  # type: ignore

    with ZipFile(file, "r") as zf:
        names = [zi.filename for zi in zf.infolist() if not zi.is_dir()]

        eom_file = next(
            name for name in names if name.endswith(".eom")
        )  # pragma: no cover
        with zf.open(eom_file) as f:
            eom: Any = resources.get_resource(  # type: ignore
                BytesURI("eom", f.read())
            ).contents[0]

        canvas_file = next(
            name for name in names if name.endswith(".cmxCanvas")
        )  # pragma: no cover
        with zf.open(canvas_file) as f:
            canvas: Any = resources.get_resource(  # type: ignore
                BytesURI("canvas", f.read())
            ).contents[0]

        try:
            with zf.open(next(name for name in names if name.endswith(".json"))) as f:
                meta = json.load(f)
            assert meta["scadVersion"] == "1.0.0"
            if lang:
                assert meta["langID"] == lang.defines["id"], (
                    meta["langID"] + "," + lang.defines["id"]
                )
                assert meta["langVersion"] == lang.defines["version"]

            model = Model(
                lang=lang,
                lang_id=meta["langID"],
                lang_version=meta["langVersion"],
                validate_icons=validate_icons,
            )
        except StopIteration:
            if lang and lang.defines["id"] != SECURILANG:  # pragma: no cover
                raise RuntimeError("MAL languages must have meta.json defined")
            model = Model(
                lang_id=SECURILANG,
                lang_version=eom.xLang,
                validate_icons=validate_icons,
            )

    extract_attributes(model, eom, {"samples", "warningThreshold"})

    id_exported_id: dict[str, int] = {}
    for xmi_object in eom.objects:
        id_exported_id[xmi_object.id] = xmi_object.exportedId
        if xmi_object.metaConcept == "Attacker":
            obj = model.create_attacker(xmi_object.name, id=xmi_object.exportedId)
        else:
            obj = model.create_object(
                xmi_object.metaConcept, xmi_object.name, id=xmi_object.exportedId
            )
        if not is_default_attribute(xmi_object, "attributesJsonString"):
            obj.meta["tags"] = json.loads(xmi_object.attributesJsonString)
        extract_attributes(obj, xmi_object, {"description", "capex", "opex"})

        if (xmi_distribution := xmi_object.existence) is not None:
            assert xmi_distribution.type in {"Bernoulli", "FixedBoolean"}
            assert len(xmi_distribution.parameters) == 1  # only probability, or fixed
            obj.meta["existence"] = xmi_distribution.parameters[0].value

        if xmi_object.metaConcept == "Attacker":
            continue

        attack_lookup = utility.attack_step_lookup(
            xmi_object.metaConcept,
            lang,
            lowercase_attack_step,
            (AttackStepType.AND, AttackStepType.OR),
        )
        defense_lookup = utility.attack_step_lookup(
            xmi_object.metaConcept,
            lang,
            lowercase_attack_step,
            (AttackStepType.DEFENSE,),
        )
        for xmi_attribute in xmi_object.evidenceAttributes:
            if (xmi_distribution := xmi_attribute.evidenceDistribution) is not None:
                assert xmi_distribution.type in {"Bernoulli", "FixedBoolean"}
                assert (
                    len(xmi_distribution.parameters) == 1
                )  # only probability, or fixed
                defense = obj.defense(defense_lookup(xmi_attribute.metaConcept))
                defense.probability = xmi_distribution.parameters[0].value
                continue

            if (xmi_distribution := xmi_attribute.localTtcDistribution) is not None:
                attack_step = obj.attack_step(attack_lookup(xmi_attribute.metaConcept))
                attack_step.ttc = TtcFunction(
                    TtcDistribution(xmi_distribution.type),
                    PARAMETERS_FROM_SCAD[TtcDistribution(xmi_distribution.type)](
                        {
                            xmi_distribution_parameter.name: xmi_distribution_parameter.value
                            for xmi_distribution_parameter in xmi_distribution.parameters
                        }
                    ),
                )

            # xmi_attribute can be without any distribution, e.g. when only setting consequence
            if (
                not is_default_attribute(xmi_attribute, "consequence")
                or not is_default_attribute(xmi_attribute, "costLowerLimit")
                or not is_default_attribute(xmi_attribute, "costUpperLimit")
                or not is_default_attribute(xmi_attribute, "description")
            ):
                attack_step = obj.attack_step(attack_lookup(xmi_attribute.metaConcept))
                extract_attributes(
                    attack_step,
                    xmi_attribute,
                    {"costLowerLimit", "costUpperLimit", "consequence", "description"},
                )

    for xmi_association in eom.associations:
        source_object = model.object(id_exported_id[xmi_association.sourceObject])
        target_object = model.object(id_exported_id[xmi_association.targetObject])
        if isinstance(source_object, Attacker):
            step = xmi_association.targetProperty.split(".")[0]
            source_object.connect(target_object.attack_step(step))
        elif isinstance(target_object, Attacker):
            step = xmi_association.sourceProperty.split(".")[0]
            target_object.connect(source_object.attack_step(step))
        else:
            source_object.field(xmi_association.sourceProperty).connect(
                target_object.field(xmi_association.targetProperty)
            )

    for xmi_view in canvas.view:
        if isinstance(xmi_view, ModelViewsPackage.ObjectView):
            continue
        view = model.create_view(xmi_view.name)
        extract_attributes(view, xmi_view, {"loadOnStart"})
        for xmi_view_node in xmi_view.viewItem:  # ViewNode -> ViewItem
            if isinstance(xmi_view_node, ModelViewsPackage.ViewTextNode):
                continue
            xmi_location = xmi_view_node.location  # Location -> XYPoint
            view.add_object(
                model.object(id_exported_id[str(xmi_view_node.id)]),
                xmi_location.x,
                xmi_location.y,
            )

        def create_group(container: Container, id: int, x: float, y: float):
            xmi_object_group = next(  # pragma: no cover
                xmi_group for xmi_group in eom.groups if xmi_group.id == str(id)
            )
            xmi_group_layout = next(  # pragma: no cover
                xmi_group_layout
                for xmi_group_layout in canvas.grouplayout
                if xmi_group_layout.id == id
            )
            group = container.create_group(
                xmi_object_group.name, xmi_group_layout.icon, x, y, id=abs(id)
            )
            if xmi_group_layout.color:
                group.meta["color"] = xmi_group_layout.color
            group.meta["expand"] = xmi_object_group.expand
            if not is_default_attribute(xmi_object_group, "attributesJsonString"):
                group.meta["tags"] = json.loads(xmi_object_group.attributesJsonString)
            extract_attributes(group, xmi_object_group, {"description"})

            for xmi_group_item in xmi_group_layout.groupitem:  # GroupItem -> XYPoint
                if str(xmi_group_item.id) in id_exported_id:
                    group.add_object(
                        model.object(id_exported_id[str(xmi_group_item.id)]),
                        xmi_group_item.x,
                        xmi_group_item.y,
                    )
                else:
                    create_group(
                        group, xmi_group_item.id, xmi_group_item.x, xmi_group_item.y
                    )

        for xmi_group_node in xmi_view.groupNode:  # GroupNode -> ViewNode
            xmi_location = xmi_group_node.location
            create_group(view, xmi_group_node.id, xmi_location.x, xmi_location.y)

    return model


# serialize


def serialize_attack_step(attack_step: AttackStep) -> ObjectModelPackage.XMIAttribute:
    costUpperLimit = attack_step.meta.get("costUpperLimit", None)
    if costUpperLimit is not None:
        costUpperLimit = float(costUpperLimit)

    costLowerLimit = attack_step.meta.get("costLowerLimit", None)
    if costLowerLimit is not None:
        costLowerLimit = float(costLowerLimit)

    xmi_attribute = ObjectModelPackage.XMIAttribute(
        metaConcept=utility.uc_first(attack_step.name),
        consequence=attack_step.meta.get("consequence", None),
        costUpperLimit=costUpperLimit,
        costLowerLimit=costLowerLimit,
    )
    xmi_attribute.description = attack_step.meta.get("description", None)
    if attack_step.ttc is not None:
        assert isinstance(attack_step.ttc, TtcFunction)
        xmi_attribute.localTtcDistribution = ObjectModelPackage.XMIDistribution(
            type=attack_step.ttc.distribution.value,
            parameters=[
                ObjectModelPackage.XMIDistributionParameter(
                    name=name, value=float(value)
                )
                for name, value in PARAMETERS_TO_SCAD[attack_step.ttc.distribution](
                    attack_step.ttc.arguments
                ).items()
            ],
        )
    return xmi_attribute


def serialize_defense(defense: Defense) -> ObjectModelPackage.XMIAttribute:
    xmi_attribute = ObjectModelPackage.XMIAttribute(
        metaConcept=utility.uc_first(defense.name)
    )
    if defense.probability is not None:
        xmi_attribute.evidenceDistribution = ObjectModelPackage.XMIDistribution(
            type="Bernoulli",
            parameters=[
                ObjectModelPackage.XMIDistributionParameter(
                    name="probability",
                    value=defense.probability,
                )
            ],
        )
    return xmi_attribute


def serialize_object(obj: Object) -> ObjectModelPackage.XMIObject:
    capex = obj.meta.get("capex", None)
    if capex is not None:
        capex = float(capex)
    opex = obj.meta.get("opex", None)
    if opex is not None:
        opex = float(opex)

    xmi_object = ObjectModelPackage.XMIObject(
        id=str(utility.id_pad(obj.id)),
        exportedId=obj.id,
        metaConcept=obj.asset_type,
        name=obj.name if obj.name else obj.asset_type,
        attributesJsonString=json.dumps(obj.meta.get("tags", {})),
        capex=capex,
        opex=opex,
    )
    xmi_object.description = obj.meta.get("description", None)

    xmi_object.existence = ObjectModelPackage.XMIDistribution(
        type="Bernoulli",
        parameters=[
            ObjectModelPackage.XMIDistributionParameter(
                name="probability", value=float(obj.meta.get("existence", 1))
            )
        ],
    )

    xmi_object.evidenceAttributes.extend(  # type: ignore
        serialize_attack_step(attack_step) for attack_step in obj._attack_steps.values()
    )

    xmi_object.evidenceAttributes.extend(  # type: ignore
        serialize_defense(defense) for defense in obj._defenses.values()
    )

    return xmi_object


def serialize_group(
    group: Group,
) -> Generator[
    tuple[ObjectModelPackage.XMIObjectGroup, ModelViewsPackage.GroupLayout], None, None
]:
    xmi_object_group = ObjectModelPackage.XMIObjectGroup(
        id=str(utility.id_pad(group.id)),
        name=group.name,
        expand=group.meta.get("expand", False),
        attributesJsonString=json.dumps(group.meta.get("tags", {})),
    )
    xmi_object_group.description = group.meta.get("description", None)

    xmi_group_layout = ModelViewsPackage.GroupLayout(
        id=utility.id_pad(group.id),
        icon=group.icon,
        color=group.meta.get("color", None),
    )

    yield xmi_object_group, xmi_group_layout

    for obj in group._objects.values():
        xmi_group_item = ModelViewsPackage.GroupItem(
            id=utility.id_pad(obj.id), x=int(obj.x), y=int(obj.y)
        )
        xmi_group_layout.groupitem.append(xmi_group_item)  # type: ignore
        xmi_object_group.items.append(  # type: ignore
            ObjectModelPackage.XMIObjectGroupItem(id=str(utility.id_pad(obj.id)))
        )

    for sub_group in group._groups.values():
        xmi_group_item = ModelViewsPackage.GroupItem(
            id=utility.id_pad(sub_group.id),
            x=int(sub_group.x),
            y=int(sub_group.y),
        )
        xmi_group_layout.groupitem.append(xmi_group_item)  # type: ignore
        xmi_object_group.items.append(  # type: ignore
            ObjectModelPackage.XMIObjectGroupItem(id=str(utility.id_pad(group.id)))
        )
        for object_group, group_layout in serialize_group(sub_group):
            yield object_group, group_layout


def write_scad(
    model: Model,
    file: str | PathLike[Any] | IO[bytes],
    eom: ObjectModelPackage.XMIObjectModel,
    canvas: ModelViewsPackage.ModelViews,
):
    with ZipFile(file, "w", compression=ZIP_DEFLATED) as zf:
        with zf.open(f"{model.name}.eom", "w") as f:
            f.write(serialize_ecore(eom))

        with zf.open(f"{model.name}.cmxCanvas", "w") as f:
            f.write(serialize_ecore(canvas))

        with zf.open("meta.json", "w") as f:
            meta = {
                "scadVersion": "1.0.0",
                "info": "Created in securiCAD model SDK",
                "langVersion": model.meta["langVersion"],
                "langID": model.meta["langId"],
            }
            if model.meta["langId"] != "com.foreseeti.securilang":
                meta["malVersion"] = "0.1.0-SNAPSHOT"
            f.write(json.dumps(meta).encode())


def serialize_model(model: Model, file: str | PathLike[Any] | IO[bytes]) -> None:
    meta_validator.validate_model(model)
    eom = ObjectModelPackage.XMIObjectModel(
        samples=model.meta.get("samples", None),
        warningThreshold=model.meta.get("warningThreshold", None),
    )

    eom.objects.extend(  # type: ignore
        serialize_object(obj) for obj in model._objects.values()
    )

    for association in model._associations:
        eom.associations.append(  # type: ignore
            ObjectModelPackage.XMIAssociation(
                sourceObject=str(utility.id_pad(association.source_object.id)),
                sourceProperty=association.source_field,
                targetObject=str(utility.id_pad(association.target_object.id)),
                targetProperty=association.target_field,
            )
        )

    canvas = ModelViewsPackage.ModelViews()
    for view in model._views.values():
        xmi_view = ModelViewsPackage.View(
            name=view.name, loadOnStart=view.meta.get("loadOnStart", True)
        )
        canvas.view.append(xmi_view)  # type: ignore
        for obj in view._objects.values():
            xmi_view.viewItem.append(  # type: ignore
                ModelViewsPackage.ViewNode(
                    location=ModelViewsPackage.Location(x=int(obj.x), y=int(obj.y)),
                    id=utility.id_pad(obj.id),
                )
            )

        for group in view._groups.values():
            xmi_group_node = ModelViewsPackage.GroupNode(
                location=ModelViewsPackage.Location(x=int(group.x), y=int(group.y)),
                id=utility.id_pad(group.id),
            )
            xmi_view.groupNode.append(xmi_group_node)  # type: ignore
            for object_group, group_layout in serialize_group(group):
                eom.groups.append(object_group)  # type: ignore
                canvas.grouplayout.append(group_layout)  # type: ignore

    write_scad(model, file, eom, canvas)
