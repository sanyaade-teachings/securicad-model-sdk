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

from typing import Any, Iterable, TypeVar

T = TypeVar("T")


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
