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

from typing import TYPE_CHECKING

from .attacker import Attacker
from .exceptions import LangException
from .validator import Validator

if TYPE_CHECKING:  # pragma: no cover
    from .association import Association, FieldTarget
    from .object import Object


class SecurilangValidator(Validator):
    def validate_multiplicity(self, obj: Object) -> None:
        super().validate_multiplicity(obj)

        if isinstance(obj, Attacker):
            return
        assert self.lang
        if self.lang.assets[obj.asset_type] <= self.lang.assets["Client"]:
            if not obj.field("rootHost").targets | obj.field("nonRootHost").targets:
                self.model._add_error(
                    obj, f"{obj} must be connected to at least 1 Host."
                )
        elif self.lang.assets[obj.asset_type] <= self.lang.assets["Service"]:
            hosts: set[FieldTarget] = set()
            for field in {
                "rootShellHost",
                "rootApplicationHost",
                "nonRootShellHost",
                "nonRootApplicationHost",
            }:
                hosts |= obj.field(field).targets
            if not hosts:
                self.model._add_error(
                    obj, f"{obj} must be connected to exactly 1 Host."
                )
            else:
                # if the service is connected to a host and network, the host and network must also be connected
                # Service [exposedServices] 0..* <-- NetworkExposure --> 0..1 [exposureNetwork] Network
                host = hosts.pop().target.field.object
                try:
                    network = list(obj.field("exposureNetwork").targets)[
                        0
                    ].target.field.object
                    network_hosts = [
                        field_target.target.field.object
                        for field_target in network.field("hosts").targets
                    ]
                    if host not in network_hosts:
                        self.model._add_error(
                            obj,
                            f"{host} and {network} connected to {obj} must also be connected together.",
                        )
                except IndexError:
                    pass
        elif self.lang.assets[obj.asset_type] <= self.lang.assets["Host"]:
            for field in {
                "nonRootApplicationServices",
                "rootApplicationServices",
                "nonRootShellServices",
                "rootShellServices",
            }:
                for field_target in obj.field(field).targets:
                    self.validate_multiplicity(field_target.target.field.object)
        elif self.lang.assets[obj.asset_type] <= self.lang.assets["Network"]:
            for field_target in obj.field("exposedServices").targets:
                self.validate_multiplicity(field_target.target.field.object)

    def validate_association_keystore(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ):
        # connected to * storageDatastore
        # connected to 1 host,service, or client
        # connected to * webapps
        # -> can always connect to dataflow
        # -> can always connect to authenticationDatastore (if not same already connected to storage)
        assert self.lang

        storage_datastores = source_object.field("storageDatastores").targets
        software = (
            source_object.field("host").targets
            | source_object.field("service").targets
            | source_object.field("client").targets
        )
        web_applications = source_object.field("webApplications").targets
        storage_datastores = source_object.field("storageDatastores").targets

        if source_field == "encryptedDataflows":
            try:
                assert (
                    list(target_object.field("protocol").targets)[0]
                    .target.field.object.defense("encrypted")
                    .probability
                    == 1.0
                )
            except (AssertionError, IndexError):
                raise LangException(
                    f"{source_object} can only be connected to encrypted Dataflows."
                )
        elif (
            self.lang.assets[target_object.asset_type] <= self.lang.assets["Datastore"]
        ):
            if source_field == "storageDatastores" and software | web_applications:
                raise LangException(
                    f"{source_object} is already connected to a Host, Service, Client, or WebApplications."
                )
            if (
                source_field == "encryptedDatastores"
                and target_object.defense("encrypted").probability != 1.0
            ):
                raise LangException(
                    f"{source_object} can only be connected to encrypted Datastores."
                )
            datastores = [
                field_target.target.field.object
                for field_target in source_object.field("storageDatastores").targets
            ] + [
                field_target.target.field.object
                for field_target in source_object.field("encryptedDatastores").targets
            ]
            if target_object in datastores:
                raise LangException(
                    f"{source_object} can only be connected once to the same Datastore."
                )
        elif (
            source_field in {"host", "service", "client"}
            and software | web_applications | storage_datastores
        ):
            raise LangException(
                f"{source_object} is already connected to a Host, Service, Client, WebApplications, or Datastores."
            )
        elif source_field == "webApplications" and software | storage_datastores:
            raise LangException(
                f"{source_object} is already connected to a Host, Service, Client, or Datastores."
            )

    def validate_association_datastore(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ):
        # connected to * webapps
        # connected to 1 rootHost,rootService,rootClient,nonRootHost,nonRootService,nonRootClient
        fields = {
            "rootHost",
            "rootService",
            "rootClient",
            "nonRootHost",
            "nonRootService",
            "nonRootClient",
        }
        if source_field == "webApplications":
            for field in fields:
                if source_object.field(field).targets:
                    raise LangException(
                        f"{source_object} is already connected to a Host, Service, or Client."
                    )
        elif source_field in fields:
            for field in fields | {"webApplications"}:
                if source_object.field(field).targets:
                    raise LangException(
                        f"{source_object} is already connected to a Host, Service, Client, or WebApplications."
                    )

    def validate_association_ids(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ):
        # connected to one of router or host
        if (
            source_field == "router"
            and source_object.field("host").targets
            or source_field == "host"
            and source_object.field("router").targets
        ):
            raise LangException(
                f"{source_object} can either be connected to a Host or Router."
            )

    def validate_association_vulnerability_scanner(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ):
        # connected hosts must be in only one of (scannedWithAuth, scannedWithoutAuth, notScanned)
        # connected networks must be in only one of (scannedWithAuth, scannedWithoutAuth)
        host_fields = {
            "hostsScannedWAuth",
            "hostsScannedWoAuth",
            "hostsNotScanned",
        }
        network_fields = {"networksScannedWAuth", "networksScannedWoAuth"}

        if source_field in host_fields:
            if target_object in [
                field_target.target.field.object
                for field in host_fields
                for field_target in source_object.field(field).targets
            ]:
                raise LangException(
                    f"{target_object} is already connected to {source_object}."
                )
        elif source_field in network_fields:
            if target_object in [
                field_target.target.field.object
                for field in network_fields
                for field_target in source_object.field(field).targets
            ]:
                raise LangException(
                    f"{target_object} is already connected to {source_object}."
                )

    def validate_association_user_account(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ):
        # connected to one of accessControl or nonRootAccessControl
        if (
            source_field == "accessControl"
            and source_object.field("nonRootAccessControl").targets
            or source_field == "nonRootAccessControl"
            and source_object.field("accessControl").targets
        ):
            raise LangException(
                f"{source_object} can only be connected with one AccessControl."
            )

    def validate_association_service(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ):
        fields = {
            "rootShellHost",
            "rootApplicationHost",
            "nonRootShellHost",
            "nonRootApplicationHost",
        }
        if source_field in fields:
            for field in fields:
                if source_object.field(field).targets:
                    raise LangException(
                        f"{source_object} must be connected to exactly 1 Host."
                    )

    def validate_association_software_product(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ):
        unique_fields = {"hosts", "services", "clients"}
        for field in unique_fields:
            if source_object.field(field).targets and source_field in unique_fields - {
                field
            }:
                raise LangException(
                    f"All connections from {source_object} must be of same asset type; Host, Service, or Client."
                )

    def validate_association(self, association: Association) -> None:
        super().validate_association(association)
        assert self.lang
        for (source_object, source_field, target_object, target_field) in [
            (
                association.source_object,
                association.source_field,
                association.target_object,
                association.target_field,
            ),
            (
                association.target_object,
                association.target_field,
                association.source_object,
                association.source_field,
            ),
        ]:
            if (
                self.lang.assets[source_object.asset_type]
                <= self.lang.assets["SoftwareProduct"]
            ):
                self.validate_association_software_product(
                    source_object, source_field, target_object, target_field
                )
            elif (
                self.lang.assets[source_object.asset_type]
                <= self.lang.assets["Keystore"]
            ):
                self.validate_association_keystore(
                    source_object, source_field, target_object, target_field
                )
            elif (
                self.lang.assets[source_object.asset_type]
                <= self.lang.assets["Datastore"]
            ):
                self.validate_association_datastore(
                    source_object, source_field, target_object, target_field
                )
            elif self.lang.assets[source_object.asset_type] <= self.lang.assets["IDS"]:
                self.validate_association_ids(
                    source_object, source_field, target_object, target_field
                )
            elif (
                self.lang.assets[source_object.asset_type]
                <= self.lang.assets["VulnerabilityScanner"]
            ):
                self.validate_association_vulnerability_scanner(
                    source_object, source_field, target_object, target_field
                )
            elif (
                self.lang.assets[source_object.asset_type]
                <= self.lang.assets["UserAccount"]
            ):
                self.validate_association_user_account(
                    source_object, source_field, target_object, target_field
                )
            elif (
                self.lang.assets[source_object.asset_type]
                <= self.lang.assets["Service"]
            ):
                self.validate_association_service(
                    source_object, source_field, target_object, target_field
                )
