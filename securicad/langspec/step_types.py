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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lang_types import Asset, AttackStep, Field, Variable


@dataclass(frozen=True)
class StepExpression(ABC):
    source_asset: Asset
    target_asset: Asset

    @staticmethod
    @abstractmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepBinaryOperation(StepExpression):
    lhs: StepExpression
    rhs: StepExpression


@dataclass(frozen=True)
class StepUnion(StepBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepIntersection(StepBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepDifference(StepBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepCollect(StepBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepTransitive(StepExpression):
    step_expression: StepExpression

    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepSubType(StepExpression):
    sub_type: Asset
    step_expression: StepExpression

    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepReference(StepExpression):
    pass


@dataclass(frozen=True)
class StepField(StepReference):
    field: Field

    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepAttackStep(StepReference):
    attack_step: AttackStep

    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class StepVariable(StepReference):
    variable: Variable

    @staticmethod
    def _abstract() -> None:
        pass
