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

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from securicad.model import Group, Object, View, ViewItem

    from .container import Container


class VisualException(Exception):
    pass


class DuplicateViewObjectException(VisualException):
    def __init__(self, view: View, obj: Object) -> None:
        self.view = view
        self.object = obj
        super().__init__(f"{obj} is in {view}.")


class MissingViewObjectException(VisualException):
    def __init__(self, view: View, obj: Object) -> None:
        self.view = view
        self.object = obj
        super().__init__(f"{obj} isn't in {view}.")


class DuplicateViewException(VisualException):
    def __init__(self, view: View) -> None:
        self.view = view
        super().__init__(f"{view} is in the model.")


class MissingViewException(VisualException):
    def __init__(self, view_id: int) -> None:
        self.view_id = view_id
        super().__init__(f"View id {view_id} isn't in the model.")


class DuplicateGroupException(VisualException):
    def __init__(self, view: View, group: Group) -> None:
        self.view = view
        self.group = group
        super().__init__(f"{group} is in {view}.")


class MissingGroupException(VisualException):
    def __init__(self, view: View, group_id: int) -> None:
        self.view = view
        self.group_id = group_id
        super().__init__(f"Group id {group_id} isn't in {view}.")


class InvalidMoveException(VisualException):
    def __init__(self, item: ViewItem, target: Container) -> None:
        self.view = item._view
        self.item = item
        self.target = target
        super().__init__(
            f"{self.item} in {self.view} can't be moved to {self.target} because it's already there."
        )
