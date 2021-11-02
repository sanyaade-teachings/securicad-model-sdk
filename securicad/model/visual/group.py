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

from typing import Any

from .container import Container
from .viewitem import ViewItem


class Group(ViewItem, Container):
    def __init__(
        self,
        meta: dict[str, Any],
        id: int,
        x: float,
        y: float,
        parent: Container,
        name: str,
        icon: str,
    ) -> None:
        ViewItem.__init__(self, x, y, parent)
        Container.__init__(self, meta, name, id)
        self._icon: str
        self.icon = icon

    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value: str) -> None:
        self._view._model._validator.validate_icon(value)
        self._icon = value

    # inherited viewitem

    def move(self, target: Container) -> None:
        target._validate_can_move_here(obj=self)
        del self._parent._groups[self.id]
        target._groups[self.id] = self
        self._parent = target

    # inherited viewitem, container

    def delete(self) -> None:
        self._parent._delete_group(self.id)
