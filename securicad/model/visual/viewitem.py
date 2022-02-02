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

if TYPE_CHECKING:  # pragma: no cover
    from .container import Container
    from .view import View


class ViewItem:
    def __init__(self, x: float, y: float, parent: Container) -> None:
        self.x = x
        self.y = y
        self._parent = parent

    @property
    def parent(self) -> Container:
        return self._parent

    @property
    def _view(self) -> View:
        return self._parent._view

    def move(self, target: Container) -> None:  # pragma: no cover
        raise NotImplementedError()

    def delete(self) -> None:  # pragma: no cover
        raise NotImplementedError()
