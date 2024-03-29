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

from io import BytesIO
from typing import TYPE_CHECKING, Any, Callable

import pytest
from jsonschema.exceptions import ValidationError

from securicad.model import es_serializer, scad_serializer

if TYPE_CHECKING:
    from securicad.model import Group, Model, Object, View

serializers: list[Callable[[Model], Any]] = [
    lambda model: scad_serializer.serialize_model(model, BytesIO()),
    es_serializer.serialize_model,
]


@pytest.mark.parametrize("serializer", serializers, ids=["scad", "es"])
@pytest.mark.parametrize(
    "key,value",
    [
        ("consequence", -1),
        ("consequence", 11),
        ("consequence", "5"),
        ("costUpperLimit", "1.6"),
        ("costLowerLimit", None),
        ("description", False),
    ],
)
def test_attack_step(
    model: Model,
    objects: list[Object],
    serializer: Callable[[Model], Any],
    key: str,
    value: Any,
):
    objects[0].attack_step("step").meta[key] = value
    with pytest.raises(ValidationError):
        serializer(model)


@pytest.mark.parametrize("serializer", serializers, ids=["scad", "es"])
@pytest.mark.parametrize(
    "key,value",
    [
        ("expand", 1),
        ("expand", "True"),
        ("tags", None),
        ("description", None),
        ("color", "white"),
        ("color", False),
        ("color", "#ff"),
    ],
)
def test_group(
    model: Model, group: Group, serializer: Callable[[Model], Any], key: str, value: Any
):
    group.meta[key] = value
    with pytest.raises(ValidationError):
        serializer(model)


def test_group_no_color_es(model: Model, group: Group) -> None:
    assert "color" not in group.meta

    es_json = es_serializer.serialize_model(model)
    assert es_json["groups"][str(group.id + 1000000000)]["color"] == ""
    model2 = es_serializer.deserialize_model(es_json)
    group2 = model2.views()[0].groups()[0]
    assert group2.id == group.id + 1000000000
    assert "color" not in group2.meta


def test_group_color_es(model: Model, group: Group) -> None:
    group.meta["color"] = "#C0FFEE"

    es_json = es_serializer.serialize_model(model)
    assert es_json["groups"][str(group.id + 1000000000)]["color"] == "#C0FFEE"
    model2 = es_serializer.deserialize_model(es_json)
    group2 = model2.views()[0].groups()[0]
    assert group2.id == group.id + 1000000000
    assert group2.meta["color"] == "#C0FFEE"


def test_group_no_color_scad(model: Model, group: Group) -> None:
    assert "color" not in group.meta

    scad_bytes = BytesIO()
    scad_serializer.serialize_model(model, scad_bytes)
    model2 = scad_serializer.deserialize_model(scad_bytes)
    group2 = model2.views()[0].groups()[0]
    assert group2.id == group.id + 1000000000
    assert "color" not in group2.meta


def test_group_color_scad(model: Model, group: Group) -> None:
    group.meta["color"] = "#C0FFEE"

    scad_bytes = BytesIO()
    scad_serializer.serialize_model(model, scad_bytes)
    model2 = scad_serializer.deserialize_model(scad_bytes)
    group2 = model2.views()[0].groups()[0]
    assert group2.id == group.id + 1000000000
    assert group2.meta["color"] == "#C0FFEE"


@pytest.mark.parametrize("serializer", serializers, ids=["scad", "es"])
@pytest.mark.parametrize(
    "key,value",
    [("tags", None), ("tags", ["ok"]), ("samples", "100"), ("warningThreshold", 92.5)],
)
def test_model(model: Model, serializer: Callable[[Model], Any], key: str, value: Any):
    model.meta[key] = value
    with pytest.raises(ValidationError):
        serializer(model)


@pytest.mark.parametrize("serializer", serializers, ids=["scad", "es"])
@pytest.mark.parametrize(
    "key,value",
    [
        ("tags", -1),
        ("capex", "5"),
        ("opex", False),
        ("description", True),
        ("existence", 1.2),
        ("existence", "0.1"),
    ],
)
def test_object(model: Model, serializer: Callable[[Model], Any], key: str, value: Any):
    model.meta[key] = value
    with pytest.raises(ValidationError):
        serializer(model)


@pytest.mark.parametrize("serializer", serializers, ids=["scad", "es"])
@pytest.mark.parametrize(
    "key,value",
    [("loadOnStart", 1), ("loadOnStart", "False")],
)
def test_object(
    model: Model, view: View, serializer: Callable[[Model], Any], key: str, value: Any
):
    view.meta[key] = value
    with pytest.raises(ValidationError):
        serializer(model)
