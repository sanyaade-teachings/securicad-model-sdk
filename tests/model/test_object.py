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

from securicad.model import Attacker, Model, Object, View
from securicad.model.exceptions import DuplicateObjectException, MissingObjectException


def test_get_invalid(model: Model):
    with pytest.raises(MissingObjectException):
        model.object(1)


def test_create(model: Model, objects: list[Object]):
    assert objects[0] == model.object(objects[0].id)


def test_connected_filter(objects: list[Object]):
    objects[0].field("a").connect(objects[1].field("a"))
    objects[0].field("a").connect(objects[2].field("a"))
    objects[0].field("b").connect(objects[3].field("b"))

    field_a = objects[0].connected_objects(field="a")
    assert len(field_a) == 2
    assert objects[1] in field_a
    assert objects[2] in field_a
    assert [objects[3]] == objects[0].connected_objects(field="b")


def test_connected_filter_type_nolang(model: Model):
    gateway_ecu = model.create_object("GatewayECU")
    network = model.create_object("Network")
    gateway_ecu.field("machineNetworks").connect(network.field("networkMachines"))
    machine = model.create_object("Machine")
    machine.field("machineNetworks").connect(network.field("networkMachines"))
    dataflow = model.create_object("ConnectionlessDataflow")
    network.field("dataflows").connect(dataflow.field("networks"))

    network_machines = network.connected_objects(field="networkMachines")
    connected = network.connected_objects()

    assert len(connected) == 3
    assert len(network_machines) == 2
    assert gateway_ecu in network_machines
    assert machine in network_machines
    assert not network.connected_objects(field="networkMachines", asset_type="ECU")
    assert [machine] == network.connected_objects(asset_type="Machine")


@pytest.mark.vehiclelang
def test_connected_filter_type(model: Model):
    # GatewayECU -> ECU -> Machine -> (abstract) PhysicalMachine

    gateway_ecu = model.create_object("GatewayECU")
    network = model.create_object("Network")
    gateway_ecu.field("machineNetworks").connect(network.field("networkMachines"))
    machine = model.create_object("Machine")
    machine.field("machineNetworks").connect(network.field("networkMachines"))
    dataflow = model.create_object("ConnectionlessDataflow")
    network.field("dataflows").connect(dataflow.field("networks"))

    network_machines = network.connected_objects(field="networkMachines")
    connected = network.connected_objects()

    assert len(connected) == 3
    assert len(network_machines) == 2
    assert gateway_ecu in network_machines
    assert machine in network_machines
    assert [gateway_ecu] == network.connected_objects(
        field="networkMachines", asset_type="ECU"
    )
    assert sorted(network_machines, key=hash) == sorted(
        network.connected_objects(asset_type="Machine"), key=hash
    )


def test_filter(model: Model):
    ecu_name1 = model.create_object("ECU", "name1")
    ecu_name2 = model.create_object("ECU", "name2")
    firmware_name1 = model.create_object("Firmware", "name1")

    name1 = model.objects(name="name1")
    ecu = model.objects(asset_type="ECU")
    assert len(name1) == 2
    assert ecu_name1 in name1
    assert firmware_name1 in name1
    assert len(ecu) == 2
    assert ecu_name1 in ecu
    assert ecu_name2 in ecu
    assert [ecu_name2] == model.objects(asset_type="ECU", name="name2")


def test_delete(model: Model, objects: list[Object]):
    objects[0].delete()
    with pytest.raises(MissingObjectException):
        model.object(objects[0].id)


def test_duplicate_id(model: Model, objects: list[Object]):
    with pytest.raises(DuplicateObjectException):
        model.create_object("ECU", id=objects[0].id)


def test_double_delete(objects: list[Object]):
    objects[0].delete()
    with pytest.raises(MissingObjectException):
        objects[0].delete()


def test_create_attacker(model: Model):
    with pytest.raises(ValueError):
        model.create_object("Attacker")


def test_delete_with_associations(objects: list[Object], model: Model):
    objects[0].field("field1").connect(objects[1].field("field2"))
    objects[0].delete()
    assert not model._associations
    assert not objects[1].field("field2").objects()


def test_delete_with_attacker(model: Model, attacker: Attacker, objects: list[Object]):
    attacker.connect(objects[0].attack_step("access"))
    assert not model.attacker_errors
    objects[0].delete()
    assert model.attacker_errors


def test_delete_with_view(objects: list[Object], view: View):
    view.add_object(objects[0])
    assert view.has_object(objects[0])
    objects[0].delete()
    assert not view.has_object(objects[0])
