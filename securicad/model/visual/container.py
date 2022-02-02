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

from typing import TYPE_CHECKING, Any, Optional

from .. import utility
from ..base import Base
from .exceptions import (
    DuplicateGroupException,
    DuplicateViewObjectException,
    InvalidMoveException,
    MissingGroupException,
    MissingViewObjectException,
)
from .viewobject import ViewObject

if TYPE_CHECKING:  # pragma: no cover
    from ..object import Object
    from .group import Group
    from .view import View
    from .viewitem import ViewItem


class Container(Base):
    def __init__(self, meta: dict[str, Any], name: str, id: int) -> None:
        super().__init__(meta)
        self._objects: dict[int, ViewObject] = {}
        self._groups: dict[int, Group] = {}
        self.name = name
        self._id = id

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}, name='{self.name}'>"

    @property
    def id(self) -> int:
        return self._id

    def _add_group(self, group: Group) -> Group:
        self._groups[group.id] = group
        return group

    def object(self, obj: Object) -> ViewObject:
        if obj.id in self._objects:
            return self._objects[obj.id]
        for group in self._groups.values():
            try:
                return group.object(obj)
            except MissingViewObjectException:
                pass
        raise MissingViewObjectException(self._view, obj)

    def objects(self, *, name: Optional[str] = None) -> list[ViewObject]:
        objects = utility.iterable_filter(
            self._objects.values(), **{"_object.name": name}
        )
        for group in self._groups.values():
            objects += group.objects(name=name)
        return objects

    def group(self, id: int) -> Group:
        if id in self._groups:
            return self._groups[id]
        for group in self._groups.values():
            try:
                return group.group(id)
            except MissingGroupException:
                pass
        raise MissingGroupException(self._view, id)

    def groups(self, *, name: Optional[str] = None) -> list[Group]:
        groups = utility.iterable_filter(self._groups.values(), name=name)
        for group in self._groups.values():
            groups += group.groups(name=name)
        return groups

    def has_object(self, obj: Object) -> bool:
        return obj.id in self._objects or any(
            group.has_object(obj) for group in self._groups.values()
        )

    def _delete_object(self, obj: Object) -> bool:
        if obj.id in self._objects:
            del self._objects[obj.id]
            return True
        else:
            return any(group._delete_object(obj) for group in self._groups.values())

    def _delete_group(self, id: int) -> bool:
        if id in self._groups:
            del self._groups[id]
            self._view._model._update_counter(id)
            return True
        else:
            return any(group._delete_group(id) for group in self._groups.values())

    def _add_object(self, obj: ViewObject) -> ViewObject:
        self._view._model.object(obj.id)
        self._objects[obj.id] = obj
        return obj

    def add_object(self, obj: Object, x: float = 0, y: float = 0) -> ViewObject:
        if self._view.has_object(obj):
            raise DuplicateViewObjectException(self._view, obj)
        return self._add_object(ViewObject({}, x, y, self, obj.id))

    def create_group(
        self,
        name: str,
        icon: str,
        x: float = 0,
        y: float = 0,
        *,
        id: Optional[int] = None,
    ) -> Group:
        from .group import Group

        id = self._view._model._get_id(id)
        if id in self._groups:
            raise DuplicateGroupException(self._view, self.group(id))
        group = Group({}, id, x, y, self, name, icon)
        self._view._model._validator.validate_icon(icon)
        return self._add_group(group)

    @property
    def _view(self) -> View:  # pragma: no cover
        raise NotImplementedError()

    def delete(self) -> None:  # pragma: no cover
        raise NotImplementedError()

    # called to check whether the current container can accept a thing
    def _validate_can_move_here(self, obj: ViewItem) -> None:
        from .group import Group
        from .viewobject import ViewObject

        if obj._view == self._view:
            return
        if isinstance(obj, ViewObject):
            if self._view.has_object(self._view._model.object(obj.id)):
                raise InvalidMoveException(obj, self)
        elif isinstance(obj, Group):
            for viewobject in obj._objects.values():
                self._validate_can_move_here(viewobject)
            for group in obj._groups.values():
                self._validate_can_move_here(group)
