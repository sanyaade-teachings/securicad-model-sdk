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

from typing import TYPE_CHECKING

from . import utility
from .object import Object
from .visual.exceptions import (
    DuplicateGroupException,
    DuplicateViewException,
    DuplicateViewObjectException,
    MissingGroupException,
    MissingViewException,
    MissingViewObjectException,
    VisualException,
)

if TYPE_CHECKING:  # pragma: no cover
    from .association import Association
    from .attacker import Attacker
    from .attackstep import AttackStep
    from .defense import Defense


class ModelException(Exception):
    pass


class DuplicateObjectException(ModelException):
    def __init__(self, obj: Object) -> None:
        self.object = obj
        super().__init__(f"{obj} is in the model.")


class MissingObjectException(ModelException):
    def __init__(self, subject: Object | int) -> None:
        self.subject = subject
        super().__init__(
            f"{utility.named_id_type(Object, subject)} isn't in the model."
        )


class DuplicateIconException(ModelException):
    def __init__(self, icon: str) -> None:
        self.icon = icon
        super().__init__(f"Icon '{icon}' is in the model.")


class MissingIconException(ModelException):
    def __init__(self, icon: str) -> None:
        self.icon = icon
        super().__init__(f"Icon '{icon}' isn't the model.")


class DuplicateAssociationException(ModelException):
    def __init__(self, association: Association) -> None:
        self.association = association
        super().__init__(f"{association} is in the model.")


class DuplicateAttackStepException(ModelException):
    def __init__(self, attacker: Attacker, attack_step: AttackStep) -> None:
        self.attacker = attacker
        self.attack_step = attack_step
        super().__init__(f"{attack_step} is connected to {attacker}.")


class MissingAssociationException(ModelException):
    def __init__(
        self, source_object: Object, source_field: str, target_object: Object
    ) -> None:
        self.source_object = source_object
        self.source_field = source_field
        self.target_object = target_object
        super().__init__(
            f"Association from field '{source_field}' of '{source_object}' to '{target_object}' isn't in the model."
        )


class MissingAttackStepException(ModelException):
    def __init__(self, attacker: Attacker, attack_step: AttackStep) -> None:
        self.attacker = attacker
        self.attack_step = attack_step
        super().__init__(f"{attack_step} isn't connected to {attacker}.")


class InvalidModelException(ModelException):
    def __init__(self, errors) -> None:
        self.errors = errors
        super().__init__(f"Invalid model: {errors}")


# LANG


class LangException(Exception):
    pass


class InvalidAssetException(LangException):
    def __init__(self, asset: str) -> None:
        self.asset = asset
        super().__init__(f"Asset '{asset}' isn't in the language.")


class InvalidFieldException(LangException):
    def __init__(self, asset: str, field: str) -> None:
        self.asset = asset
        self.field = field
        super().__init__(
            f"Asset '{asset}' doesn't have field '{field}' in the language."
        )


class MultiplicityException(LangException):
    def __init__(self, obj: Object, field: str, maximum: float) -> None:
        super().__init__(
            f"Field '{field}' of {obj} can be connected to at most {maximum} object{'' if maximum == 1 else 's'}."
        )


class InvalidAttackStepException(LangException):
    def __init__(self, attack_step: AttackStep) -> None:
        self.attack_step = attack_step
        super().__init__(f"{attack_step} isn't in the language.")


class InvalidDefenseException(LangException):
    def __init__(self, defense: Defense) -> None:
        self.defense = defense
        super().__init__(f"{defense} isn't in the language.")


class InvalidAssociationException(LangException):
    def __init__(self, association: Association) -> None:
        self.association = association
        super().__init__(f"{association} isn't in the language.")


# BOTH


class InvalidIconException(ModelException, LangException):
    def __init__(self, icon: str) -> None:
        self.icon = icon
        super().__init__(f"Icon '{icon}' isn't in the model or language.")
