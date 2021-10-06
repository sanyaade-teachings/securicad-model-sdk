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

import pytest
from jsonschema.exceptions import ValidationError

from securicad.langspec import Lang, TtcDistribution, TtcFunction
from securicad.model import Model


def test_deserialize_model2(model2: dict[str, Any], vehicle_lang: Lang):
    model = Model.from_dict(model2, lang=vehicle_lang)
    assert model._counter == 3
    assert len(model.objects()) == 2
    assert model.object(1).asset_type == "ECU"
    assert not model.validate()


def test_create_model3(model: Model, model3: dict[str, Any]):
    ecu1 = model.create_object("ECU", "ecu1")
    ecu2 = model.create_object("ECU", "ecu2")
    ecu3 = model.create_object("ECU", "ecu3")
    attacker = model.create_attacker()
    attacker.connect(ecu1.attack_step("access"))
    ecu1.defense("def").probability = 0.3
    ecu1.attack_step("att").ttc = 1
    g1 = model.create_view("default").create_group("g", "?")
    g1.create_group("g", "?")
    firmware = model.create_object("Firmware", "firmware")
    model.create_object("Unknown")
    ecu1.field("firmware").connect(firmware.field("hardware"))
    ecu2.field("firmware").connect(firmware.field("hardware"))
    ecu3.field("firmware").connect(firmware.field("hardware"))
    firmware.field("from").connect(ecu1.field("to"))
    assert not model.validate()
    assert model.to_dict(sorted=True) == model3


@pytest.mark.vehicle_lang
def test_create_model1(model: Model, model1: dict[str, Any]):
    ecu = model.create_object("ECU", "Base ECU")
    ecu.defense("operationModeProtection").probability = 0.5
    ecu.defense("operationModeProtection").meta["dsiabled"] = True
    ecu.attack_step("shutdown").ttc = 2
    attacker = model.create_attacker()
    attacker.connect(ecu.attack_step("access"))
    firmware = model.create_object("Firmware")
    firmware.field("hardware").connect(ecu.field("firmware"))
    ecu.attack_step("access").ttc = (
        TtcFunction(TtcDistribution.EXPONENTIAL, [0.6]) + 5
    ) / 12
    model.create_icon("Icon", "png", b"\x89PNG\r\n\x1A\n", "license")
    view = model.create_view("default")
    group = view.create_group("Group", "Icon")
    group.add_object(ecu)
    view.add_object(firmware)
    firmware.meta["my_tag"] = True
    group.meta["color"] = [255, 0, 0]
    assert not model.validate()
    assert model.to_dict(sorted=True) == model1


def test_validate_model1(model1: dict[str, Any], vehicle_lang: Lang):
    model = Model.from_dict(model1, lang=vehicle_lang)
    assert not model.validate()


def test_serialize_loop(model1: dict[str, Any], vehicle_lang: Lang):
    assert Model.from_dict(model1, lang=vehicle_lang).to_dict(sorted=True) == model1


def test_deserialize_model4(model4: dict[str, Any]):
    with pytest.raises(ValidationError):
        Model.from_dict(model4)


def test_serialize_invalid(model: Model):
    model.create_object("").attack_step("")._ttc = False  # type: ignore
    with pytest.raises(RuntimeError):
        model.to_dict()
