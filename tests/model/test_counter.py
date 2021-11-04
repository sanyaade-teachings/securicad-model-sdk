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

from typing import Any

from securicad.model import Model, json_serializer


def test_sequential(model: Model):
    assert model.create_object("").id == 1
    assert model.create_object("").id == 2
    v3 = model.create_view("")
    assert v3.id == 3
    assert v3.create_group("", "").id == 4
    assert model.create_object("").id == 5


def test_retake(model: Model):
    model.create_object("")
    model.create_object("")
    o3 = model.create_object("")
    model.create_object("")
    o3.delete()
    o3 = model.create_object("")
    assert o3.id == 3
    o5 = model.create_object("")
    assert o5.id == 5


def test_load(model7_json: dict[str, Any]):
    # model7 has objects 1,2,4. View 5. Groups 6, 3455436
    m = json_serializer.deserialize_model(model7_json)
    assert m.create_object("").id == 3
    assert m.create_object("").id == 7
    assert m.create_object("").id == 8
