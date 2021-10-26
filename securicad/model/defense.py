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

from typing import TYPE_CHECKING, Any, Optional

from .base import Base

if TYPE_CHECKING:  # pragma: no cover
    from .object import Object


class Defense(Base):
    def __init__(
        self, meta: dict[str, Any], obj: Object, name: str, probability: Optional[float]
    ) -> None:
        super().__init__(meta)
        self._object = obj
        self._name = name
        self.probability = probability

    def __str__(self) -> str:
        return f"<{self._object}->{self.name}>"

    @property
    def is_default(self) -> bool:
        return self.probability is None and not self.meta

    @property
    def name(self) -> str:
        return self._name
