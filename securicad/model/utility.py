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

from functools import lru_cache
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from securicad.langspec import AttackStepType, Lang

T = TypeVar("T")


def named_id_type(type_: type[T], subject: int | T) -> str:
    if isinstance(subject, int):
        return f"{type_.__name__} id {subject}"
    return str(subject)


def id_pad(value: int) -> int:
    if value < 10 ** 9:
        value += 10 ** 9
    return value


def get_nested_attribute(obj: Any, attribute: str) -> Any:
    for attr in attribute.split("."):
        obj = getattr(obj, attr)
    return obj


def iterable_filter(iterable: Iterable[T], **kwargs: Any) -> list[T]:
    return [
        item
        for item in iterable
        if all(
            value is None or get_nested_attribute(item, attribute) == value
            for attribute, value in kwargs.items()
        )
    ]


def uc_first(value: str) -> str:
    return value[0].upper() + value[1:]


@lru_cache
def attack_step_lookup(
    asset_type: str,
    lang: Optional[Lang],
    lowercase_attack_step: bool,
    types_: tuple[AttackStepType],
) -> Callable[[str], str]:
    if lang and asset_type != "Attacker":
        attack_steps = {
            name.lower(): name
            for name, attack_step in lang.assets[asset_type].attack_steps.items()
            if attack_step.type in types_
        }

    def lookup(attack_step: str):
        if lang and attack_step.lower() in attack_steps:
            return attack_steps[attack_step.lower()]
        if lowercase_attack_step:
            return attack_step[0].lower() + attack_step[1:]
        return attack_step

    return lookup
