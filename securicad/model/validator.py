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

from typing import TYPE_CHECKING

from securicad.langspec import AttackStepType

from .attacker import Attacker
from .exception import (
    InvalidAssetException,
    InvalidAssociationException,
    InvalidAttackStepException,
    InvalidDefenseException,
    InvalidFieldException,
    InvalidIconException,
    MultiplicityException,
)
from .object import Object

if TYPE_CHECKING:  # pragma: no cover
    from .association import Association
    from .attackstep import AttackStep
    from .defense import Defense
    from .model import Model


class Validator:
    def __init__(self, model: Model) -> None:
        self.model = model
        self.lang = model._lang

    def validate_icon(self, name: str) -> None:
        if not self.lang:
            return
        in_model = name in self.model._icons
        in_lang = name in self.lang.assets and (
            self.lang.assets[name].png_icon or self.lang.assets[name].svg_icon
        )
        if not in_model and not in_lang:
            raise InvalidIconException(f"{name} doesn't exist")

    def validate_object(self, obj: Object) -> None:
        if not self.lang:
            return
        if (
            obj.asset_type not in self.lang.assets
            or self.lang.assets[obj.asset_type].is_abstract
        ):
            raise InvalidAssetException(f"{obj.asset_type} doesn't exist")

    def validate_attack_step(self, attack_step: AttackStep) -> None:
        if not self.lang:
            return
        asset = self.lang.assets[attack_step._object.asset_type]
        if attack_step.name not in asset.attack_steps or asset.attack_steps[
            attack_step.name
        ].type not in {AttackStepType.AND, AttackStepType.OR}:
            raise InvalidAttackStepException(f"{attack_step.name} doesn't exist")

    def validate_field(self, obj: Object, field: str) -> None:
        if not self.lang:
            return
        asset = self.lang.assets[obj.asset_type]
        if field not in asset.fields:
            raise InvalidFieldException(f"{field} doesn't exist")

    def validate_defense(self, defense: Defense) -> None:
        if not self.lang:
            return
        asset = self.lang.assets[defense._object.asset_type]
        if (
            defense.name not in asset.attack_steps
            or asset.attack_steps[defense.name].type is not AttackStepType.DEFENSE
        ):
            raise InvalidDefenseException(f"{defense.name} doesn't exist")

    def validate_association(self, association: Association) -> None:
        if not self.lang:
            return
        source_object = self.model._objects[association.source_object_id]
        target_object = self.model._objects[association.target_object_id]

        source_asset = self.lang.assets[source_object.asset_type]
        target_asset = self.lang.assets[target_object.asset_type]

        source_field = source_asset.fields[association.source_field]
        target_field = target_asset.fields[association.target_field]

        if (
            source_field == target_field
            or source_field.association != target_field.association
        ):
            raise InvalidAssociationException(f"{association} doesn't exist")

    def validate_attackers(self) -> list[str]:
        if not any(
            connections
            for attacker in self.model._attackers.values()
            for connections in attacker._first_steps.values()
        ):
            return ["Model must have at least 1 connected attacker"]
        return []

    def validate_max_multiplicity(self, obj: Object, field: str) -> None:
        """Raise exception if object is already at max capacity for one field."""
        if not self.lang:
            return

        maximum = self.lang.assets[obj.asset_type].fields[field].multiplicity.max
        target = "object" if maximum == 1 else "objects"
        if len(obj.field(field).objects()) >= maximum:
            raise MultiplicityException(
                f'field "{field}" must connect to at most {maximum} {target}'
            )

    def validate_multiplicity(self, obj: Object) -> None:
        self.model._multiplicity_errors[obj].clear()

        if isinstance(obj, Attacker):
            return
        if not self.lang:
            return

        for name, field in self.lang.assets[obj.asset_type].fields.items():
            count = len(obj.field(name).objects())
            if count < field.multiplicity.min:
                target = "object" if field.multiplicity.min == 1 else "objects"
                self.model._multiplicity_errors[obj].append(
                    f'field "{name}" must connect to at least {field.multiplicity.min} {target}'
                )