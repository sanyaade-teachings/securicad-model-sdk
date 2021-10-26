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

from securicad.model import Model, View
from securicad.model.exceptions import (
    InvalidAssetException,
    InvalidAssociationException,
    InvalidAttackStepException,
    InvalidDefenseException,
    InvalidFieldException,
    InvalidIconException,
    MultiplicityException,
)


def test_no_lang():
    with pytest.raises(ValueError):
        Model()


@pytest.mark.vehicle_lang
def test_invalid_asset(model: Model):
    with pytest.raises(InvalidAssetException):
        model.create_object("?")


@pytest.mark.vehicle_lang
def test_abstract_asset(model: Model):
    with pytest.raises(InvalidAssetException):
        model.create_object("PhysicalMachine")


@pytest.mark.vehicle_lang
def test_invalid_attack_step(model: Model):
    ecu = model.create_object("ECU")
    with pytest.raises(InvalidAttackStepException):
        ecu.attack_step("?")


@pytest.mark.vehicle_lang
def test_invalid_defense(model: Model):
    ecu = model.create_object("ECU")
    with pytest.raises(InvalidDefenseException):
        ecu.defense("?")


@pytest.mark.vehicle_lang
def test_invalid_field(model: Model):
    ecu = model.create_object("ECU")
    firmware = model.create_object("Firmware")
    with pytest.raises(InvalidFieldException):
        ecu.field("?").connect(firmware.field("hardware"))
    with pytest.raises(InvalidFieldException):
        ecu.field("firmware").connect(firmware.field("?"))


@pytest.mark.vehicle_lang
def test_invalid_association(model: Model):
    ecu1 = model.create_object("ECU")
    ecu2 = model.create_object("ECU")
    with pytest.raises(InvalidAssociationException):
        ecu1.field("firmware").connect(ecu2.field("firmwareUpdater"))
    with pytest.raises(InvalidAssociationException):
        ecu1.field("firmware").connect(ecu2.field("firmware"))


@pytest.mark.vehicle_lang
def test_max_multiplicity(model: Model):
    ecu1 = model.create_object("ECU")
    ecu2 = model.create_object("ECU")
    firmware = model.create_object("Firmware")
    ecu1.field("firmware").connect(firmware.field("hardware"))
    with pytest.raises(MultiplicityException):
        firmware.field("hardware").connect(ecu2.field("firmware"))


@pytest.mark.vehicle_lang
def test_invalid_icon(view: View):
    with pytest.raises(InvalidIconException):
        view.create_group("group", "?ICON?")
