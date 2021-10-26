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

import collections
from typing import TYPE_CHECKING, Any, DefaultDict

from .exceptions import MissingAttackStepException
from .object import Object

if TYPE_CHECKING:  # pragma: no cover
    from .association import Association
    from .attackstep import AttackStep
    from .model import Model


class Attacker(Object):
    def __init__(self, meta: dict[str, Any], model: Model, id: int, name: str) -> None:
        super().__init__(meta, model, id, "Attacker", name)
        self._first_steps: DefaultDict[
            Object, dict[str, Association]
        ] = collections.defaultdict(dict)

    def connect(self, attack_step: AttackStep) -> None:
        self._model._check_connection(self, attack_step._object, attack_step)
        self._model._validator.validate_attack_step(attack_step)
        self._model._add_connection(self, attack_step._object, attack_step.name)

    def disconnect(self, attack_step: AttackStep) -> None:
        if not attack_step.name in self._first_steps[attack_step._object]:
            raise MissingAttackStepException(self, attack_step)
        association = self._first_steps[attack_step._object][attack_step.name]
        self._model._associations.remove(association)
        del self._first_steps[attack_step._object][attack_step.name]
        if not self._first_steps[attack_step._object]:
            attack_step._object._attackers.remove(self)
