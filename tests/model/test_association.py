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

from securicad.model import (
    InvalidAssociationException,
    InvalidObjectException,
    Model,
    MultiplicityException,
    Object,
)


def test_create(model: Model, objects: list[Object]):
    objects[0].field("field1").connect(objects[1].field("field2"))
    assert model._associations
    assert objects[0].field("field1").objects()
    assert objects[1].field("field2").objects()


def test_duplicate(model: Model, objects: list[Object]):
    objects[0].field("field1").connect(objects[1].field("field2"))
    with pytest.raises(InvalidAssociationException):
        objects[1].field("field2").connect(objects[0].field("field1"))


def test_delete(model: Model, objects: list[Object]):
    objects[0].field("field1").connect(objects[1].field("field2"))
    objects[0].field("field1").disconnect(objects[1])
    assert not model._associations
    assert not objects[0].field("field1").objects()
    assert not objects[1].field("field2").objects()


def test_delete_invalid(model: Model, objects: list[Object]):
    objects[0].delete()
    with pytest.raises(InvalidObjectException):
        objects[0].field("field1").disconnect(objects[1])
    with pytest.raises(InvalidObjectException):
        objects[1].field("field2").disconnect(objects[0])


def test_double_delete(model: Model, objects: list[Object]):
    objects[0].field("field1").connect(objects[1].field("field2"))
    objects[0].field("field1").disconnect(objects[1])
    with pytest.raises(InvalidAssociationException):
        objects[1].field("field2").disconnect(objects[0])


def test_create_invalid(model: Model, objects: list[Object]):
    objects[0].delete()
    with pytest.raises(InvalidObjectException):
        objects[0].field("field1").connect(objects[1].field("field2"))
    with pytest.raises(InvalidObjectException):
        objects[1].field("field2").connect(objects[0].field("field1"))


@pytest.mark.vehicle_lang
def test_multiplicity(model: Model):
    ecu1 = model.create_object("ECU")
    ecu2 = model.create_object("ECU")
    firmware = model.create_object("Firmware")
    assert len(model._associations) == 0
    ecu1.field("firmware").connect(firmware.field("hardware"))
    assert len(model._associations) == 1
    with pytest.raises(MultiplicityException):
        ecu2.field("firmware").connect(firmware.field("hardware"))
    assert len(model._associations) == 1
