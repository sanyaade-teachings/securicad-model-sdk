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

import pytest

from securicad.model import Model, Object, View
from securicad.model.exceptions import DuplicateViewException, MissingViewException


def test_create(model: Model, view: View):
    assert model.view(1) == view


def test_double_delete(view: View):
    view.delete()
    with pytest.raises(MissingViewException):
        view.delete()


def test_invalid_get(model: Model):
    with pytest.raises(MissingViewException):
        model.view(1)


def test_duplicate(view: View, model: Model):
    with pytest.raises(DuplicateViewException):
        model.create_view("default", id=view.id)


def test_delete(view: View, model: Model):
    view.delete()
    with pytest.raises(MissingViewException):
        model.view(view.id)


def test_nested_object(view: View, objects: list[Object]):
    view.create_group("g1", "icon")
    group = view.create_group("g2", "icon")
    obj = group.add_object(objects[0])
    assert view.object(objects[0]) == obj


def test_nested_group(view: View):
    view.create_group("g1", "icon")
    group = view.create_group("g2", "icon")
    g = group.create_group("g3", "icon")
    assert view.group(g.id) == g


def test_nested_object_delete(view: View, objects: list[Object]):
    view.create_group("g1", "icon")
    group = view.create_group("g2", "icon")
    group.add_object(objects[0])
    view.delete_object(objects[0])
    assert not view.objects()


def test_nested_group_delete(view: View):
    view.create_group("g1", "icon")
    group = view.create_group("g2", "icon")
    g = group.create_group("g3", "icon")
    view.delete_group(g.id)
    groups = view.groups()
    assert g not in groups
    assert len(groups) == 2


def test_filter(model: Model):
    view1_name1 = model.create_view("name1")
    view2_name1 = model.create_view("name1")
    view_name2 = model.create_view("name2")

    name1 = model.views(name="name1")
    assert len(name1) == 2
    assert view1_name1 in name1
    assert view2_name1 in name1
    assert [view_name2] == model.views(name="name2")
