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

from .container import Container

if TYPE_CHECKING:  # pragma: no cover
    from ..model import Model


class View(Container):
    def __init__(self, meta: dict[str, Any], model: Model, name: str, id: int) -> None:
        super().__init__(meta, name, id)
        self._model = model

    # inherited container

    @property
    def _view(self) -> View:
        return self

    def delete(self) -> None:
        self._model._delete_view(self.id)
