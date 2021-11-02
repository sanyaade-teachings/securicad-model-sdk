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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, unique
from typing import Union


def wrap_ttc_expression(other: TtcValue) -> TtcExpression:
    if isinstance(other, TtcExpression):
        return other
    if isinstance(other, (float, int)):  # type: ignore
        return TtcNumber(other)
    raise NotImplementedError(f"unsupported operand type: '{type(other).__name__}'")


@dataclass(frozen=True)
class TtcExpression(ABC):
    @staticmethod
    @abstractmethod
    def _abstract() -> None:
        pass

    def __add__(self, other: TtcValue) -> TtcAddition:
        return TtcAddition(self, wrap_ttc_expression(other))

    def __radd__(self, other: float) -> TtcAddition:
        return TtcAddition(wrap_ttc_expression(other), self)

    def __sub__(self, other: TtcValue) -> TtcSubtraction:
        return TtcSubtraction(self, wrap_ttc_expression(other))

    def __rsub__(self, other: float) -> TtcSubtraction:
        return TtcSubtraction(wrap_ttc_expression(other), self)

    def __mul__(self, other: TtcValue) -> TtcMultiplication:
        return TtcMultiplication(self, wrap_ttc_expression(other))

    def __rmul__(self, other: float) -> TtcMultiplication:
        return TtcMultiplication(wrap_ttc_expression(other), self)

    def __truediv__(self, other: TtcValue) -> TtcDivision:
        return TtcDivision(self, wrap_ttc_expression(other))

    def __rtruediv__(self, other: float) -> TtcDivision:
        return TtcDivision(wrap_ttc_expression(other), self)

    def __pow__(self, other: TtcValue) -> TtcExponentiation:
        return TtcExponentiation(self, wrap_ttc_expression(other))

    def __rpow__(self, other: float) -> TtcExponentiation:
        return TtcExponentiation(wrap_ttc_expression(other), self)


TtcValue = Union[TtcExpression, int, float]


@dataclass(frozen=True)
class TtcBinaryOperation(TtcExpression):
    lhs: TtcExpression
    rhs: TtcExpression


@dataclass(frozen=True)
class TtcAddition(TtcBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class TtcSubtraction(TtcBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class TtcMultiplication(TtcBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class TtcDivision(TtcBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class TtcExponentiation(TtcBinaryOperation):
    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class TtcFunction(TtcExpression):
    distribution: TtcDistribution
    arguments: list[float]

    @staticmethod
    def _abstract() -> None:
        pass


@dataclass(frozen=True)
class TtcNumber(TtcExpression):
    value: float

    @staticmethod
    def _abstract() -> None:
        pass


@unique
class TtcDistribution(Enum):
    BERNOULLI = "Bernoulli"
    BINOMIAL = "Binomial"
    EXPONENTIAL = "Exponential"
    GAMMA = "Gamma"
    LOG_NORMAL = "LogNormal"
    PARETO = "Pareto"
    TRUNCATED_NORMAL = "TruncatedNormal"
    UNIFORM = "Uniform"
    EASY_AND_CERTAIN = "EasyAndCertain"
    EASY_AND_UNCERTAIN = "EasyAndUncertain"
    HARD_AND_CERTAIN = "HardAndCertain"
    HARD_AND_UNCERTAIN = "HardAndUncertain"
    VERY_HARD_AND_CERTAIN = "VeryHardAndCertain"
    VERY_HARD_AND_UNCERTAIN = "VeryHardAndUncertain"
    INFINITY = "Infinity"
    ZERO = "Zero"
    ENABLED = "Enabled"
    DISABLED = "Disabled"
