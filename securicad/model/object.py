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

from typing import TYPE_CHECKING, Any, Optional

from . import utility
from .association import Field
from .attackstep import AttackStep
from .base import Base
from .defense import Defense

if TYPE_CHECKING:  # pragma: no cover
    from .attacker import Attacker
    from .model import Model


class Object(Base):
    def __init__(
        self,
        meta: dict[str, Any],
        model: Model,
        id: int,
        asset_type: str,
        name: str,
    ) -> None:
        super().__init__(meta)
        self._model = model
        self._id = id
        self.name = name
        self._asset_type = asset_type
        self._associations: dict[str, Field] = {}
        self._attack_steps: dict[str, AttackStep] = {}
        self._defenses: dict[str, Defense] = {}
        self._attackers: set[Attacker] = set()

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, asset='{self.asset_type}', name='{self.name}'>"

    @property
    def asset_type(self) -> str:
        return self._asset_type

    @property
    def id(self) -> int:
        return self._id

    def field(self, name: str) -> Field:
        self._model._validator.validate_field(self, name)
        if name not in self._associations:
            self._associations[name] = Field(self, name)
        return self._associations[name]

    def connected_objects(
        self, *, field: Optional[str] = None, asset_type: Optional[str] = None
    ) -> list[Object]:
        if field:
            collection = self._associations[field].targets
        else:
            collection = [
                target
                for field in self._associations.values()
                for target in field.targets
            ]
        if self._model._lang and asset_type:
            return [
                target.target.field.object
                for target in collection
                if self._model._lang.assets[target.target.field.object.asset_type]
                <= self._model._lang.assets[asset_type]
            ]
        else:
            return utility.iterable_filter(
                (target.target.field.object for target in collection),
                asset_type=asset_type,
            )

    def delete(self) -> None:
        self._model._delete_object(self.id)

    def attack_step(self, name: str) -> AttackStep:
        if name in self._attack_steps:
            return self._attack_steps[name]
        attack_step = AttackStep({}, self, name, None)
        self._model._validator.validate_attack_step(attack_step)
        self._attack_steps[name] = attack_step
        return attack_step

    def defense(self, name: str) -> Defense:
        if name in self._defenses:
            return self._defenses[name]
        defense = Defense({}, self, name, None)
        self._model._validator.validate_defense(defense)
        self._defenses[name] = defense
        return defense
