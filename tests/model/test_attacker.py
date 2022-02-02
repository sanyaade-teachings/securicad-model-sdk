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

import pytest

from securicad.model import Attacker, Model, Object
from securicad.model.exceptions import (
    DuplicateAttackStepException,
    DuplicateObjectException,
    MissingAttackStepException,
    MissingObjectException,
)


def test_create(model: Model, attacker: Attacker):
    assert attacker == model.object(attacker.id)


def test_duplicate_id(model: Model, attacker: Attacker):
    with pytest.raises(DuplicateObjectException):
        model.create_attacker(id=attacker.id)


def test_delete(model: Model, attacker: Attacker):
    attacker.delete()
    with pytest.raises(MissingObjectException):
        model.object(attacker.id)


def test_connect(model: Model, attacker: Attacker, objects: list[Object]):
    attacker.connect(objects[0].attack_step("access"))
    assert not model.attacker_errors


def test_connect_duplicate(attacker: Attacker, objects: list[Object]):
    attacker.connect(objects[0].attack_step("access"))
    with pytest.raises(DuplicateAttackStepException):
        attacker.connect(objects[0].attack_step("access"))


def test_connect_invalid_object(attacker: Attacker, objects: list[Object]):
    objects[0].delete()
    with pytest.raises(MissingObjectException):
        attacker.connect(objects[0].attack_step("access"))


def test_connect_invalid_attacker(attacker: Attacker, objects: list[Object]):
    attacker.delete()
    with pytest.raises(MissingObjectException):
        attacker.connect(objects[0].attack_step("access"))


def test_double_connect(model: Model, attacker: Attacker, objects: list[Object]):
    attacker.connect(objects[0].attack_step("access"))
    attacker.connect(objects[0].attack_step("read"))
    attacker.disconnect(objects[0].attack_step("access"))
    assert not model.attacker_errors


def test_disconnect(model: Model, attacker: Attacker, objects: list[Object]):
    attacker.connect(objects[0].attack_step("access"))
    attacker.disconnect(objects[0].attack_step("access"))
    assert model.attacker_errors


def test_double_disconnect(attacker: Attacker, objects: list[Object]):
    attacker.connect(objects[0].attack_step("access"))
    attacker.disconnect(objects[0].attack_step("access"))
    with pytest.raises(MissingAttackStepException):
        attacker.disconnect(objects[0].attack_step("access"))


def test_delete_with_steps(model: Model, attacker: Attacker, objects: list[Object]):
    attacker.connect(objects[0].attack_step("access"))
    attacker.delete()
    assert model.attacker_errors


def test_filter(model: Model):
    attacker1_name1 = model.create_attacker("name1")
    attacker2_name1 = model.create_attacker("name1")
    attacker_name2 = model.create_attacker("name2")
    name1 = model.attackers(name="name1")
    assert len(name1) == 2
    assert attacker1_name1 in name1
    assert attacker2_name1 in name1
    assert [attacker_name2] == model.attackers(name="name2")
