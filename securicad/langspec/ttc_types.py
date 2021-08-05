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
from typing import List


@dataclass(frozen=True)
class TtcExpression(ABC):
    @staticmethod
    @abstractmethod
    def _abstract():
        pass


@dataclass(frozen=True)
class TtcBinaryOperation(TtcExpression):
    lhs: TtcExpression
    rhs: TtcExpression


@dataclass(frozen=True)
class TtcAddition(TtcBinaryOperation):
    @staticmethod
    def _abstract():
        pass


@dataclass(frozen=True)
class TtcSubtraction(TtcBinaryOperation):
    @staticmethod
    def _abstract():
        pass


@dataclass(frozen=True)
class TtcMultiplication(TtcBinaryOperation):
    @staticmethod
    def _abstract():
        pass


@dataclass(frozen=True)
class TtcDivision(TtcBinaryOperation):
    @staticmethod
    def _abstract():
        pass


@dataclass(frozen=True)
class TtcExponentiation(TtcBinaryOperation):
    @staticmethod
    def _abstract():
        pass


@dataclass(frozen=True)
class TtcFunction(TtcExpression):
    distribution: TtcDistribution
    arguments: List[float]

    @staticmethod
    def _abstract():
        pass


@dataclass(frozen=True)
class TtcNumber(TtcExpression):
    value: float

    @staticmethod
    def _abstract():
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
