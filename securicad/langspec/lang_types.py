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

import math
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from .step_types import StepExpression
    from .ttc_types import TtcExpression


@dataclass(frozen=True)
class Category:
    name: str
    meta: Dict[str, Any]
    assets: Dict[str, Asset] = field(default_factory=dict, init=False, repr=False)


@dataclass
class Asset:
    name: str
    meta: Dict[str, str]
    category: Category
    is_abstract: bool
    super_asset: Optional[Asset] = field(default=None, init=False, repr=False)
    _fields: Dict[str, Field] = field(default_factory=dict, init=False, repr=False)
    _variables: Dict[str, Variable] = field(
        default_factory=dict, init=False, repr=False
    )
    _attack_steps: Dict[str, AttackStep] = field(
        default_factory=dict, init=False, repr=False
    )
    svg_icon: Optional[bytes]
    png_icon: Optional[bytes]

    @property
    def fields(self) -> Dict[str, Field]:
        if not self.super_asset:
            return self._fields
        return {**self.super_asset.fields, **self._fields}

    @property
    def variables(self) -> Dict[str, Variable]:
        if not self.super_asset:
            return self._variables
        return {**self.super_asset.variables, **self._variables}

    @property
    def attack_steps(self) -> Dict[str, AttackStep]:
        if not self.super_asset:
            return self._attack_steps
        return {**self.super_asset.attack_steps, **self._attack_steps}

    def is_sub_type_of(self, other: Asset) -> bool:
        if self is other:
            return True
        if not self.super_asset:
            return False
        return self.super_asset.is_sub_type_of(other)

    def __lt__(self, other: Asset) -> bool:
        return self.is_sub_type_of(other) and self is not other

    def __le__(self, other: Asset) -> bool:
        return self.is_sub_type_of(other)

    def __gt__(self, other: Asset) -> bool:
        return other.is_sub_type_of(self) and other is not self

    def __ge__(self, other: Asset) -> bool:
        return other.is_sub_type_of(self)

    @staticmethod
    def least_upper_bound(asset1: Asset, asset2: Asset) -> Optional[Asset]:
        if asset1 <= asset2:
            return asset2
        if asset1 >= asset2:
            return asset1
        if not asset1.super_asset or not asset2.super_asset:
            return None
        return Asset.least_upper_bound(asset1.super_asset, asset2.super_asset)

    def __or__(self, other: Asset) -> Optional[Asset]:
        return Asset.least_upper_bound(self, other)

    def __ror__(self, other: Asset) -> Optional[Asset]:
        return Asset.least_upper_bound(self, other)


@dataclass
class Field:
    name: str
    asset: Asset
    multiplicity: Multiplicity
    target: Field = field(init=False, repr=False)
    association: Association = field(init=False, repr=False)


@dataclass
class Variable:
    name: str
    asset: Asset
    step_expression: StepExpression = field(init=False, repr=False)

    @property
    def super_variable(self) -> Optional[Variable]:
        if not self.asset.super_asset:
            return None
        return self.asset.super_asset.variables.get(self.name)


@dataclass(frozen=True)
class AttackStep:
    name: str
    meta: Dict[str, str]
    asset: Asset
    type: AttackStepType
    _tags: Set[str]
    _risk: Optional[Risk]
    _ttc: Optional[TtcExpression]
    _requires: Optional[Steps]
    _reaches: Optional[Steps]

    @property
    def tags(self) -> Set[str]:
        if not self.super_attack_step:
            return self._tags
        return self.super_attack_step.tags | self._tags

    @property
    def risk(self) -> Optional[Risk]:
        if self._risk:
            return self._risk
        if not self.super_attack_step:
            return None
        return self.super_attack_step.risk

    @property
    def ttc(self) -> Optional[TtcExpression]:
        if self._ttc:
            return self._ttc
        if not self.super_attack_step:
            return None
        return self.super_attack_step.ttc

    @property
    def requires(self) -> List[StepExpression]:
        local_requires: List[StepExpression] = (
            self._requires.step_expressions if self._requires else []
        )
        overrides = self._requires.overrides if self._requires else False
        if not self.super_attack_step or overrides:
            return local_requires
        return self.super_attack_step.requires + local_requires

    @property
    def reaches(self) -> List[StepExpression]:
        local_reaches: List[StepExpression] = (
            self._reaches.step_expressions if self._reaches else []
        )
        overrides = self._reaches.overrides if self._reaches else False
        if not self.super_attack_step or overrides:
            return local_reaches
        return self.super_attack_step.reaches + local_reaches

    @property
    def super_attack_step(self) -> Optional[AttackStep]:
        if not self.asset.super_asset:
            return None
        return self.asset.super_asset.attack_steps.get(self.name)


@unique
class AttackStepType(Enum):
    AND = "and"
    OR = "or"
    DEFENSE = "defense"
    EXIST = "exist"
    NOT_EXIST = "notExist"


@dataclass(frozen=True)
class Risk:
    is_confidentiality: bool
    is_integrity: bool
    is_availability: bool


@dataclass(frozen=True)
class Steps:
    overrides: bool
    step_expressions: List[StepExpression] = field(
        default_factory=list, init=False, repr=False
    )


@dataclass(frozen=True)
class Association:
    name: str
    meta: Dict[str, str]
    left_field: Field
    right_field: Field


@unique
class Multiplicity(Enum):
    ZERO_OR_ONE = (0, 1)
    ZERO_OR_MORE = (0, None)
    ONE = (1, 1)
    ONE_OR_MORE = (1, None)

    def __init__(self, min_: int, max_: Optional[int]) -> None:
        self.min = min_
        self.max = max_ if max_ is not None else math.inf
