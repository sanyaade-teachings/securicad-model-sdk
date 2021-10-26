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

import typing

import pytest

from securicad.model import Group, Model, Object, View
from securicad.model.exceptions import (
    DuplicateGroupException,
    DuplicateViewObjectException,
    MissingGroupException,
    MissingViewObjectException,
)


def test_create_nested_group(group: Group):
    group2 = group.create_group("group", "icon")
    assert [group2] == group.groups()


def test_create_duplicated_nested_group(group: Group):
    group2 = group.create_group("group", "icon")
    with pytest.raises(DuplicateGroupException):
        group2 = group.create_group("group", "icon", id=group2.id)


def test_move_object(view: View, objects: list[Object], group: Group):
    group2 = group.create_group("group", "icon")
    obj = group2.add_object(objects[0])
    obj.move(typing.cast(Group, obj.parent).parent)
    assert not group2.objects()
    assert [obj] == group.objects()
    obj.move(typing.cast(Group, obj.parent).parent)
    assert not group.objects()
    assert [obj] == view.objects()


def test_move_group(view: View, group: Group):
    group2 = group.create_group("group", "icon")
    group2.move(view)
    assert not group.groups()
    assert len(view.groups()) == 2


def test_delete_nested(view: View, objects: list[Object]):
    group = view.create_group("group", "icon")
    group.add_object(objects[0])
    view.delete_object(objects[0])
    assert not group.objects()


def test_create_group(view: View, group: Group):
    assert group == view.group(group.id)


def test_duplicate_group(group: Group, view: View):
    with pytest.raises(DuplicateGroupException):
        view.create_group("group", "icon", id=group.id)


def test_add_object(view: View, objects: list[Object]):
    obj = view.add_object(objects[0])
    assert obj == view.object(objects[0])


def test_add_duplicate(view: View, objects: list[Object]):
    view.add_object(objects[0])
    with pytest.raises(DuplicateViewObjectException):
        view.add_object(objects[0])


def test_delete_object(view: View, objects: list[Object]):
    obj = view.add_object(objects[0])
    obj.delete()
    with pytest.raises(MissingViewObjectException):
        view.object(objects[0])


def test_delete_group(view: View, group: Group):
    group.delete()
    with pytest.raises(MissingGroupException):
        view.group(group.id)


def test_get_invalid_object(view: View, objects: list[Object]):
    with pytest.raises(MissingViewObjectException):
        view.object(objects[0])


def test_get_invalid_group(view: View):
    with pytest.raises(MissingGroupException):
        view.group(0)


def test_object_filter(view: View, model: Model):
    obj1_name1 = view.add_object(model.create_object("obj", "name1"))
    obj2_name1 = view.add_object(model.create_object("obj", "name1"))
    obj_name2 = view.add_object(model.create_object("obj", "name2"))

    name1 = view.objects(name="name1")
    assert len(name1) == 2
    assert obj1_name1 in name1
    assert obj2_name1 in name1
    assert [obj_name2] == view.objects(name="name2")


def test_group_filter(view: View):
    group1_name1 = view.create_group("name1", "icon")
    group2_name1 = view.create_group("name1", "icon")
    group_name2 = view.create_group("name2", "icon")

    name1 = view.groups(name="name1")
    assert len(name1) == 2
    assert group1_name1 in name1
    assert group2_name1 in name1
    assert [group_name2] == view.groups(name="name2")
