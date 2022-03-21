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

from typing import Any

import pytest

from securicad.langspec import Lang, TtcDistribution, TtcFunction
from securicad.model import Model, es_serializer
from securicad.model.exceptions import InvalidLangException


def test_model6(model: Model, model6_json: dict[str, Any]):
    model.meta["mid"] = model6_json["mid"]
    computer = model.create_object("Computer")
    computer.attack_step("access").meta["consequence"] = 5
    computer.attack_step("enter").ttc = TtcFunction(TtcDistribution.EXPONENTIAL, [2])
    network = model.create_object("Network")
    attacker = model.create_attacker()
    computer.field("networks").connect(network.field("computers"))
    attacker.connect(network.attack_step("compromise"))

    overview = model.create_view("Overview")
    overview.add_object(attacker, 10, 20)
    group = overview.create_group("Objects", "Icon", 10, 40)
    group.add_object(computer, 10, 10)
    group.add_object(network, 20, 10)

    assert es_serializer.serialize_model(model, sort=True) == model6_json


def test_model6_loop(model6_json: dict[str, Any]):
    assert (
        es_serializer.serialize_model(
            es_serializer.deserialize_model(model6_json), sort=True
        )
        == model6_json
    )


def test_wrong_lang_id(securilang: Lang) -> None:
    model = Model("wrong-id", lang=securilang)
    es_model = es_serializer.serialize_model(model)
    es_model["metadata"]["langID"] = "com.foreseeti.wronglang"
    with pytest.raises(
        InvalidLangException,
        match=r"^Unexpected language 'com\.foreseeti\.wronglang@2\.1\.9', expected 'com\.foreseeti\.securilang@2\.1\.9'$",
    ):
        es_serializer.deserialize_model(es_model, lang=securilang)


def test_wrong_lang_version(securilang: Lang) -> None:
    model = Model("wrong-version", lang=securilang)
    es_model = es_serializer.serialize_model(model)
    es_model["metadata"]["langVersion"] = "9.9.9"
    with pytest.raises(
        InvalidLangException,
        match=r"^Unexpected language 'com\.foreseeti\.securilang@9\.9\.9', expected 'com\.foreseeti\.securilang@2\.1\.9'$",
    ):
        es_serializer.deserialize_model(es_model, lang=securilang)
