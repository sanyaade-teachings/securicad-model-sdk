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

import json
from pathlib import Path

import pytest

from securicad.langspec import Lang
from securicad.model import Attacker, Group, Icon, Model, Object, View


@pytest.fixture(scope="session")
def vehicle_lang() -> Lang:
    return Lang(Path(__file__).parent.joinpath("org.mal-lang.vehiclelang-1.0.0.mar"))


for i in range(5):
    vars()[f"model{i+1}"] = pytest.fixture(scope="session")(
        lambda i=i: json.loads(Path(__file__).parent.joinpath(f"model{i+1}.json").read_text())  # type: ignore
    )


@pytest.fixture
def simple_scad() -> bytes:
    return Path(__file__).parent.joinpath("simple.sCAD").read_bytes()


@pytest.fixture
def text_scad() -> bytes:
    return Path(__file__).parent.joinpath("text.sCAD").read_bytes()


@pytest.fixture
def model_scad() -> bytes:
    return Path(__file__).parent.joinpath("model.sCAD").read_bytes()


@pytest.fixture
def model(vehicle_lang: Lang, request: pytest.FixtureRequest) -> Model:
    if request.node.get_closest_marker("vehicle_lang"):
        return Model(lang=vehicle_lang)
    else:
        return Model(lang_id="null", lang_version="0.0.0")


@pytest.fixture
def objects(model: Model, request: pytest.FixtureRequest) -> list[Object]:
    marker = request.node.get_closest_marker("object_count")
    if not marker:
        count = 10
    else:
        count: int = marker.args[0]  # type: ignore
    return [model.create_object("obj", f"obj{i}") for i in range(count)]


@pytest.fixture
def attacker(model: Model) -> Attacker:
    return model.create_attacker()


@pytest.fixture
def view(model: Model) -> View:
    return model.create_view("default")


@pytest.fixture
def group(view: View) -> Group:
    return view.create_group("group", "icon")


@pytest.fixture
def icon(model: Model) -> Icon:
    return model.create_icon("icon", "", b"", "")
