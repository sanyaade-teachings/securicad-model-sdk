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

from io import BytesIO
from typing import Any

from securicad.langspec import Lang
from securicad.model import Model, Object


def test_serialize_loop_model2(model2: dict[str, Any], vehicle_lang: Lang):
    model = Model.from_dict(model2, lang=vehicle_lang)
    scad = BytesIO()
    model.write_scad(scad)
    looped = Model.read_scad(scad, lang=vehicle_lang)
    assert looped.to_dict(sorted=True) == model.to_dict(sorted=True)


def test_simple(model5: dict[str, Any], simple_scad: bytes):
    # simple.sCAD has attacker association flipped (target side)
    assert Model.read_scad(BytesIO(simple_scad)).to_dict(sorted=True) == model5


def test_serialize(model5: dict[str, Any]):
    Model.from_dict(model5).write_scad(BytesIO())


def test_deserialize_text(text_scad: bytes):
    # text.sCAD has no meta, but defined xLang attribute. It also has textNodes and objectNodes.
    assert Model.read_scad(BytesIO(text_scad))


def test_defense_probability(model: Model, objects: list[Object]):
    objects[0].defense("def").probability = None
    scad = BytesIO()
    model.write_scad(scad)
    m = Model.read_scad(scad)
    assert m.object(objects[0].id).defense("def").probability is None


def test_model_loop(model_scad: bytes):
    # model.sCAD changes every attribute once somewhere
    model = Model.read_scad(BytesIO(model_scad))
    scad = BytesIO()
    model.write_scad(scad)
    looped = Model.read_scad(scad)
    assert model.to_dict(sorted=True) == looped.to_dict(sorted=True)
