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

from typing import TYPE_CHECKING, Any

from securicad.model.base import Base
from securicad.model.object import Object

from .viewitem import ViewItem

if TYPE_CHECKING:  # pragma: no cover
    from .container import Container


class ViewObject(ViewItem, Base):
    def __init__(
        self, meta: dict[str, Any], x: float, y: float, parent: Container, id: int
    ) -> None:
        ViewItem.__init__(self, x, y, parent)
        Base.__init__(self, meta)
        self.id = id

    @property
    def _object(self) -> Object:
        return self._view._model.object(self.id)

    # inherited viewitem

    def delete(self) -> None:
        self._parent._delete_object(self._object)

    def move(self, target: Container) -> None:
        target._validate_can_move_here(obj=self)
        del self._parent._objects[self.id]
        target._objects[self.id] = self
        self._parent = target
