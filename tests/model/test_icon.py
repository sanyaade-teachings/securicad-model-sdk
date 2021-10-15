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

import pytest

from securicad.langspec import Lang
from securicad.model import Icon, InvalidIconException, Model, View


@pytest.mark.vehicle_lang()
def test_create_invalid(view: View):
    with pytest.raises(InvalidIconException):
        view.create_group("group", "?")


def test_create_any(vehicle_lang: Lang):
    model = Model(lang=vehicle_lang, validate_icons=False)
    view = model.create_view("view")
    assert view.create_group("group", "?")


def test_get_invalid(model: Model):
    with pytest.raises(InvalidIconException):
        model.icon("?")


def test_create(model: Model, icon: Icon):
    assert icon == model.icon(icon.name)


def test_delete(model: Model, icon: Icon):
    model.delete_icon(icon.name)
    with pytest.raises(InvalidIconException):
        model.icon(icon.name)


def test_duplicate(model: Model, icon: Icon):
    with pytest.raises(InvalidIconException):
        model.create_icon(icon.name, "", b"", "")


def test_double_delete(model: Model, icon: Icon):
    model.delete_icon(icon.name)
    with pytest.raises(InvalidIconException):
        model.delete_icon(icon.name)
