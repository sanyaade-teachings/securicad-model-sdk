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


class Association(Base):
    def __init__(
        self,
        meta: dict[str, Any],
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ) -> None:
        super().__init__(meta)
        self.source_object = source_object
        self.source_field = source_field
        self.target_object = target_object
        self.target_field = target_field

    def __str__(self) -> str:
        return f"<{self.source_object}.{self.source_field} <-> {self.target_object}.{self.target_field}>"


class Field:
    def __init__(
        self, obj: Object, name: str, targets: Optional[set[FieldTarget]] = None
    ) -> None:
        self.object = obj
        self.name = name
        self.targets = targets or set()

    def objects(self) -> list[Object]:
        return [target.target.field.object for target in self.targets]

    def connect(self, field: Field):
        self.object._model._create_association(
            self.object, self.name, field.object, field.name
        )

    def disconnect(self, obj: Object):
        self.object._model._delete_association(self.object, self.name, obj)


class FieldTarget:
    def __init__(
        self, field: Field, target: FieldTarget, association: Association
    ) -> None:
        self.field = field
        self.target = target
        self.association = association
