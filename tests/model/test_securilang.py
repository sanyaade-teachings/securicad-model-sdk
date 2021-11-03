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

from contextlib import contextmanager
from io import BytesIO
from typing import TYPE_CHECKING

import pytest

from securicad.model import Model, scad_serializer
from securicad.model.exceptions import LangException

if TYPE_CHECKING:
    from securicad.langspec import Lang


@contextmanager
def raises(exc: type[Exception]):
    with pytest.raises(exc) as error:
        yield
    assert error.type == exc, error.value


@pytest.mark.securilang
@pytest.mark.parametrize("root", ["root", "nonRoot"])
def test_client(model: Model, root: str):
    """Client must be connected to a host, either root or non-root."""
    client = model.create_object("Client")
    host = model.create_object("Host")
    assert len(model.validation_errors) == 4
    client.field(f"{root}Host").connect(host.field(f"{root}Clients"))
    assert len(model.validation_errors) == 3
    client.field(f"{root}Host").disconnect(host)
    assert len(model.validation_errors) == 4


@pytest.mark.securilang
@pytest.mark.parametrize("asset", ["Host", "Client", "Service"])
@pytest.mark.parametrize("target_asset", ["Host", "Client", "Service"])
def test_software_product(model: Model, asset: str, target_asset: str):
    """SoftwareProduct must be connected to only hosts, clients, or services."""
    if asset == target_asset:
        pytest.skip()
    software_product = model.create_object("SoftwareProduct")
    obj = model.create_object(asset)
    software_product.field(f"{asset.lower()}s").connect(obj.field("softwareProduct"))

    target = model.create_object(target_asset)
    with raises(LangException):
        software_product.field(f"{target_asset.lower()}s").connect(
            target.field("softwareProduct")
        )


@pytest.mark.securilang
def test_keystore_encrypted_datastore(model: Model):
    """Encrypted datastores must be encrypted."""
    keystore = model.create_object("Keystore")
    datastore = model.create_object("Datastore")
    with raises(LangException):
        datastore.field("keystore").connect(keystore.field("encryptedDatastores"))
    datastore.defense("encrypted").probability = 1.0
    datastore.field("keystore").connect(keystore.field("encryptedDatastores"))


@pytest.mark.securilang
def test_keystore_encrypted_dataflow(model: Model):
    """Encrypted dataflows must be encrypted."""
    keystore = model.create_object("Keystore")
    dataflow = model.create_object("Dataflow")
    with raises(LangException):
        dataflow.field("keystore").connect(keystore.field("encryptedDataflows"))
    protocol = model.create_object("Protocol")
    protocol.defense("encrypted").probability = 1.0
    dataflow.field("protocol").connect(protocol.field("dataflows"))
    dataflow.field("keystore").connect(keystore.field("encryptedDataflows"))


@pytest.mark.securilang
def test_keystore_unique_datastore(model: Model):
    """Datastores cannot both be encrypted and used for storage."""
    keystore = model.create_object("Keystore")
    datastore = model.create_object("Datastore")
    datastore.defense("encrypted").probability = 1.0
    datastore.field("keystore").connect(keystore.field("encryptedDatastores"))
    with raises(LangException):
        datastore.field("storedKeystores").connect(keystore.field("storageDatastores"))


keystore_connections = [
    ("Host", "host", "keystores"),
    ("Client", "client", "keystores"),
    ("Service", "service", "keystores"),
    ("WebApplication", "webApplications", "keystores"),
    ("Datastore", "storageDatastores", "storedKeystores"),
]


@pytest.mark.securilang
@pytest.mark.parametrize("asset,field,connected", keystore_connections)
@pytest.mark.parametrize(
    "target_asset,target_field,target_connected", keystore_connections
)
def test_keystore_restriction(
    model: Model,
    asset: str,
    field: str,
    connected: str,
    target_asset: str,
    target_field: str,
    target_connected: str,
):
    """Connected to one of host,client,service,webapplications,or datastore."""
    if asset == target_asset:
        pytest.skip()
    keystore = model.create_object("Keystore")
    obj = model.create_object(asset)
    keystore.field(field).connect(obj.field(connected))
    target = model.create_object(target_asset)
    with raises(LangException):
        keystore.field(target_field).connect(target.field(target_connected))


@pytest.mark.parametrize(
    "asset,field,target_field",
    [
        ("WebApplication", "webApplications", "keystores"),
        ("Datastore", "storageDatastores", "storedKeystores"),
    ],
)
@pytest.mark.securilang
def test_keystore_multiple(model: Model, asset: str, field: str, target_field: str):
    """Can connect multiple webapplications and datastores."""
    keystore = model.create_object("Keystore")
    obj1 = model.create_object(asset)
    keystore.field(field).connect(obj1.field(target_field))
    obj2 = model.create_object(asset)
    keystore.field(field).connect(obj2.field(target_field))


@pytest.mark.securilang
@pytest.mark.parametrize("asset,field,target_field", keystore_connections)
def test_keystore_dataflow(model: Model, asset: str, field: str, target_field: str):
    """Can always connect encrypted dataflows."""
    keystore = model.create_object("Keystore")
    obj = model.create_object(asset)
    keystore.field(field).connect(obj.field(target_field))
    dataflow = model.create_object("Dataflow")
    protocol = model.create_object("Protocol")
    protocol.defense("encrypted").probability = 1.0
    dataflow.field("protocol").connect(protocol.field("dataflows"))
    dataflow.field("keystore").connect(keystore.field("encryptedDataflows"))


@pytest.mark.securilang
@pytest.mark.parametrize("asset,field,target_field", keystore_connections)
def test_keystore_datastore(model: Model, asset: str, field: str, target_field: str):
    """Can always connect encrypted datastores."""
    keystore = model.create_object("Keystore")
    obj = model.create_object(asset)
    keystore.field(field).connect(obj.field(target_field))
    datastore = model.create_object("Datastore")
    datastore.defense("encrypted").probability = 1.0
    datastore.field("keystore").connect(keystore.field("encryptedDatastores"))


@pytest.mark.securilang
@pytest.mark.parametrize("asset", ["Host", "Client", "Service"])
@pytest.mark.parametrize("root", ["root", "nonRoot"])
@pytest.mark.parametrize("target_asset", ["Host", "Client", "Service"])
@pytest.mark.parametrize("target_root", ["root", "nonRoot"])
def test_datastore_software(
    model: Model, asset: str, root: str, target_asset: str, target_root: str
):
    """Connected to host,client,service, or webapp."""
    datastore = model.create_object("Datastore")
    obj1 = model.create_object(asset)
    obj1.field(f"{root}Datastores").connect(datastore.field(f"{root}{asset}"))
    obj2 = model.create_object(target_asset)
    with raises(LangException):
        obj2.field(f"{target_root}Datastores").connect(
            datastore.field(f"{target_root}{target_asset}")
        )

    obj3 = model.create_object("WebApplication")
    with raises(LangException):
        obj3.field("datastores").connect(datastore.field("webApplications"))


@pytest.mark.securilang
def test_datastore_webapplications(model: Model):
    datastore = model.create_object("Datastore")
    wa1 = model.create_object("WebApplication")
    wa1.field("datastores").connect(datastore.field("webApplications"))
    wa2 = model.create_object("WebApplication")
    wa2.field("datastores").connect(datastore.field("webApplications"))


@pytest.mark.securilang
@pytest.mark.parametrize("asset,field", [("Router", "nIDS"), ("Host", "hIDS")])
@pytest.mark.parametrize(
    "target_asset,target_field", [("Router", "nIDS"), ("Host", "hIDS")]
)
def test_ids(
    model: Model, asset: str, field: str, target_asset: str, target_field: str
):
    """Connected to either router or host."""
    if asset == target_asset:
        pytest.skip()
    ids = model.create_object("IDS")
    obj = model.create_object(asset)
    ids.field(asset.lower()).connect(obj.field(field))

    target = model.create_object(target_asset)
    with raises(LangException):
        ids.field(target_asset.lower()).connect(target.field(target_field))


host_scanner_fields = [
    ("hostsScannedWAuth", "authenticatedVulnerabilityScanners"),
    ("hostsScannedWoAuth", "unauthenticatedVulnerabilityScanners"),
    ("hostsNotScanned", "vulnerabilityScannersNotScanningThisOS"),
]


@pytest.mark.securilang
@pytest.mark.parametrize("field,connected", host_scanner_fields)
@pytest.mark.parametrize("target_field,target_connected", host_scanner_fields)
def test_vuln_scanner_host(
    model: Model, field: str, connected: str, target_field: str, target_connected: str
):
    """
    Host connected to vulnerability scanner can only be in one of not scanned, scanned with auth,
    or scanned without auth.
    """
    if field == target_field:
        pytest.skip()
    scanner = model.create_object("VulnerabilityScanner")
    host = model.create_object("Host")
    scanner.field(field).connect(host.field(connected))
    with raises(LangException):
        scanner.field(target_field).connect(host.field(target_connected))


network_scanner_fields = [
    ("networksScannedWAuth", "authenticatedVulnerabilityScanners"),
    ("networksScannedWoAuth", "unauthenticatedVulnerabilityScanners"),
]


@pytest.mark.securilang
@pytest.mark.parametrize("field,connected", network_scanner_fields)
@pytest.mark.parametrize("target_field,target_connected", network_scanner_fields)
def test_vuln_scanner_network(
    model: Model, field: str, connected: str, target_field: str, target_connected: str
):
    """Network connected to vulnerability scanner can only be in one of scanned w/ or w/o auth."""
    if field == target_field:
        pytest.skip()
    scanner = model.create_object("VulnerabilityScanner")
    network = model.create_object("Network")
    scanner.field(field).connect(network.field(connected))
    with raises(LangException):
        scanner.field(target_field).connect(network.field(target_connected))


@pytest.mark.securilang
@pytest.mark.parametrize(
    "field,connected",
    [
        ("nonRootAccessControl", "nonRootUserAccounts"),
        ("accessControl", "userAccounts"),
    ],
)
@pytest.mark.parametrize(
    "target_field,target_connected",
    [
        ("nonRootAccessControl", "nonRootUserAccounts"),
        ("accessControl", "userAccounts"),
    ],
)
def test_user_account(
    model: Model, field: str, connected: str, target_field: str, target_connected: str
):
    """UserAccount can only be connected to one typeof AccessControl"""
    if field == target_field:
        pytest.skip()
    user_account = model.create_object("UserAccount")
    ac1 = model.create_object("AccessControl")
    user_account.field(field).connect(ac1.field(connected))
    ac2 = model.create_object("AccessControl")
    with raises(LangException):
        user_account.field(target_field).connect(ac2.field(target_connected))


@pytest.mark.securilang
def test_service(model: Model):
    service = model.create_object("Service")
    host = model.create_object("Host")
    network = model.create_object("Network")

    # for validity
    attacker = model.create_attacker()
    attacker.connect(host.attack_step("compromise"))
    sp1 = model.create_object("SoftwareProduct")
    sp1.field("services").connect(service.field("softwareProduct"))
    sp2 = model.create_object("SoftwareProduct")
    sp2.field("hosts").connect(host.field("softwareProduct"))

    assert len(model.validation_errors) == 1
    host.field("rootShellServices").connect(service.field("rootShellHost"))
    model.validate()

    service.field("exposureNetwork").connect(network.field("exposedServices"))
    assert len(model.validation_errors) == 1  # must also connect network and host
    host.field("networks").connect(network.field("hosts"))
    model.validate()
    host.field("networks").disconnect(network)
    assert len(model.validation_errors) == 1


def test_text_scad(text_scad: bytes, securilang: Lang):
    # text.sCAD has no meta, but defined xLang attribute. It also has textNodes and objectNodes.
    scad_serializer.deserialize_model(BytesIO(text_scad), lang=securilang)


def test_model_scad(model_scad: bytes, securilang: Lang):
    # model.sCAD changes every attribute once somewhere
    scad_serializer.deserialize_model(BytesIO(model_scad), lang=securilang)
