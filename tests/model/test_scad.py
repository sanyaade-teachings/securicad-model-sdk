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
from typing import TYPE_CHECKING, Any

from securicad.langspec import Lang
from securicad.model import Model, json_serializer, scad_serializer

if TYPE_CHECKING:
    from securicad.model import Object


def test_serialize_loop_model2(model2_json: dict[str, Any], vehicle_lang: Lang):
    model = json_serializer.deserialize_model(model2_json, lang=vehicle_lang)
    scad = BytesIO()
    scad_serializer.serialize_model(model, scad)
    looped = scad_serializer.deserialize_model(scad, lang=vehicle_lang)
    assert json_serializer.serialize_model(
        looped, sort=True
    ) == json_serializer.serialize_model(model, sort=True)


def test_simple(model5_json: dict[str, Any], simple_scad: bytes):
    # simple.sCAD has attacker association flipped (target side)
    assert (
        json_serializer.serialize_model(
            scad_serializer.deserialize_model(BytesIO(simple_scad)), sort=True
        )
        == model5_json
    )


def test_serialize(model5_json: dict[str, Any]):
    scad_serializer.serialize_model(
        json_serializer.deserialize_model(model5_json), BytesIO()
    )


def test_deserialize_text(text_scad: bytes):
    # text.sCAD has no meta, but defined xLang attribute. It also has textNodes and objectNodes.
    scad_serializer.deserialize_model(BytesIO(text_scad))


def test_defense_probability(model: Model, objects: list[Object]):
    objects[0].defense("def").probability = None
    scad = BytesIO()
    scad_serializer.serialize_model(model, scad)
    m = scad_serializer.deserialize_model(scad)
    assert m.object(objects[0].id).defense("def").probability is None


def test_model_loop(model_scad: bytes):
    # model.sCAD changes every attribute once somewhere
    model = scad_serializer.deserialize_model(BytesIO(model_scad))
    scad = BytesIO()
    scad_serializer.serialize_model(model, scad)
    looped = scad_serializer.deserialize_model(scad)
    assert json_serializer.serialize_model(
        model, sort=True
    ) == json_serializer.serialize_model(looped, sort=True)
