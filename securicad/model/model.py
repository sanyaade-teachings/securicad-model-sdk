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

import collections
import typing
from typing import Any, DefaultDict, Optional

from ..langspec import Lang
from . import serializer, utility
from .association import Association, FieldTarget
from .attacker import Attacker
from .base import Base
from .exception import (
    InvalidAssociationException,
    InvalidAttackStepException,
    InvalidIconException,
    InvalidObjectException,
)
from .icon import Icon
from .object import Object
from .validator import Validator
from .visual.exception import InvalidViewException
from .visual.view import View


class Model(Base):
    def __init__(
        self,
        name: str = "unnamed",
        *,
        lang: Optional[Lang] = None,
        lang_id: Optional[str] = None,
        lang_version: Optional[str] = None,
    ):
        if lang:
            super().__init__(
                {"langId": lang.defines["id"], "langVersion": lang.defines["version"]}
            )
        elif lang_id is not None and lang_version is not None:
            super().__init__({"langId": lang_id, "langVersion": lang_version})
        else:
            raise ValueError(
                'model must be created with keyword arguments "lang" or "lang_id" and "lang_version"'
            )

        self.name = name
        self._lang = lang
        self._validator = Validator(self)
        self._views: dict[int, View] = {}
        self._objects: dict[int, Object] = {}
        self._attackers: dict[int, Attacker] = {}
        self._associations: set[Association] = set()
        self._icons: dict[str, Icon] = {}
        self._counter = 1
        self._multiplicity_errors: DefaultDict[
            Object, list[str]
        ] = collections.defaultdict(list)

    def to_dict(self, *, sorted: bool = False) -> dict[str, Any]:
        return serializer.serialize_model(self, sorted)

    @staticmethod
    def from_dict(data: dict[str, Any], *, lang: Optional[Lang] = None) -> Model:
        return serializer.deserialize_model(data, lang=lang)

    def create_icon(self, name: str, format: str, data: bytes, license: str) -> Icon:
        if name in self._icons:
            raise InvalidIconException(f"{name} already exists")
        icon = Icon({}, name, format, data, license)
        self._icons[name] = icon
        return icon

    def _get_id(self, id: Optional[int] = None) -> int:
        return self._counter if id is None else id

    def _update_counter(self, id: int):
        self._counter = max(id + 1, self._counter)

    def icon(self, name: str) -> Icon:
        if name not in self._icons:
            raise InvalidIconException(f"{name} doesn't exist")
        return self._icons[name]

    def delete_icon(self, name: str) -> None:
        if name not in self._icons:
            raise InvalidIconException(f"{name} doesn't exist")
        del self._icons[name]

    def _check_association(self, association: Association) -> None:
        if not self.has_object(association.source_object_id):
            raise InvalidObjectException(
                f"{association.source_object_id} doesn't exist"
            )
        if not self.has_object(association.target_object_id):
            raise InvalidObjectException(
                f"{association.target_object_id} doesn't exist"
            )
        source_object = self._objects[association.source_object_id]
        target_object = self._objects[association.target_object_id]
        if target_object in source_object.field(association.source_field).objects():
            raise InvalidAssociationException(f"{association} already exists")

    def _add_object(self, obj: Object) -> None:
        self._update_counter(obj.id)
        self._objects[obj.id] = obj
        self._validator.validate_multiplicity(obj)

    @property
    def multiplicity_errors(self) -> list[str]:
        return [
            f"{obj} {error}"
            for obj, errors in self._multiplicity_errors.items()
            for error in errors
        ]

    @property
    def attacker_errors(self) -> list[str]:
        return self._validator.validate_attackers()

    def validate(self) -> list[str]:
        return self.multiplicity_errors + self.attacker_errors

    def has_object(self, id: int) -> bool:
        return id in self._objects

    def object(self, id: int) -> Object:
        if not self.has_object(id):
            raise InvalidObjectException(f"{id} doesn't exist")
        return self._objects[id]

    def objects(
        self, *, name: Optional[str] = None, asset_type: Optional[str] = None
    ) -> list[Object]:
        return utility.iterable_filter(
            self._objects.values(), name=name, asset_type=asset_type
        )

    def attackers(self, *, name: Optional[str] = None):
        return utility.iterable_filter(self._attackers.values(), name=name)

    def create_attacker(
        self, name: str = "Attacker", *, id: Optional[int] = None
    ) -> Attacker:
        id = self._get_id(id)
        if self.has_object(id):
            raise InvalidObjectException(f"{id} already exists")
        attacker = Attacker({}, self, id, name)
        self._attackers[attacker.id] = attacker
        self._add_object(attacker)
        return attacker

    def create_object(
        self, asset_type: str, name: str = "", *, id: Optional[int] = None
    ) -> Object:
        if asset_type == "Attacker":
            raise ValueError("use create_attacker()")
        id = self._get_id(id)
        if self.has_object(id):
            raise InvalidObjectException(f"{id} already exists")
        obj = Object({}, self, id, asset_type, name)
        self._validator.validate_object(obj)
        self._add_object(obj)
        return obj

    def _add_association(self, association: Association) -> None:
        source_object = self._objects[association.source_object_id]
        target_object = self._objects[association.target_object_id]

        source_field = source_object.field(association.source_field)
        target_field = target_object.field(association.target_field)
        source_field_target = FieldTarget(
            source_field, typing.cast(Any, None), association
        )
        target_field_target = FieldTarget(
            target_field, typing.cast(Any, None), association
        )
        source_field_target.target = target_field_target
        target_field_target.target = source_field_target
        source_field.targets.add(source_field_target)
        target_field.targets.add(target_field_target)

        self._associations.add(association)
        self._validator.validate_multiplicity(source_object)
        self._validator.validate_multiplicity(target_object)

    def _check_connection(
        self, attacker: Attacker, obj: Object, attack_step: str
    ) -> None:
        """Checks that the potential connection is valid in the model."""
        if not self.has_object(attacker.id):
            raise InvalidObjectException(f"{attacker} doesn't exist")
        if not self.has_object(obj.id):
            raise InvalidObjectException(f"{obj} doesn't exist")
        if attack_step in attacker._first_steps[obj]:
            raise InvalidAttackStepException(f"{attack_step} is already connected")

    def _add_connection(
        self, attacker: Attacker, obj: Object, attack_step: str
    ) -> None:
        association = Association(
            {}, attacker.id, "firstSteps", obj.id, f"{attack_step}.attacker"
        )
        attacker._first_steps[obj][attack_step] = association
        obj._attackers.add(attacker)
        self._associations.add(association)

    def _create_association(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ) -> None:
        association = Association(
            {}, source_object.id, source_field, target_object.id, target_field
        )
        self._check_association(association)
        self._validator.validate_association(association)
        self._validator.validate_max_multiplicity(source_object, source_field)
        self._validator.validate_max_multiplicity(target_object, target_field)
        self._add_association(association)

    def _delete_association(
        self, source_object: Object, source_field: str, target_object: Object
    ):
        if not self.has_object(source_object.id):
            raise InvalidObjectException(f"{source_object} doesn't exist")
        if not self.has_object(target_object.id):
            raise InvalidObjectException(f"{target_object} doesn't exist")
        if target_object not in source_object.field(source_field).objects():
            raise InvalidAssociationException(
                f"{source_object}.{source_field} to {target_object} doesn't exists"
            )
        source_field_object = source_object.field(source_field)
        source_field_target = next(  # pragma: no cover, StopIteration does not happen
            target
            for target in source_field_object.targets
            if target.target.field.object == target_object
        )
        target_field_object = source_field_target.target.field
        target_field_target = source_field_target.target

        source_field_object.targets.remove(source_field_target)
        target_field_object.targets.remove(target_field_target)

        self._associations.remove(source_field_target.association)
        self._validator.validate_multiplicity(source_object)
        self._validator.validate_multiplicity(target_object)

    def delete_object(self, id: int) -> None:
        if not self.has_object(id):
            raise InvalidObjectException(f"{id} doesn't exist")
        obj = self._objects[id]

        for field in obj._associations.values():
            for field_target in set(field.targets):  # copy set
                obj.field(field.name).disconnect(field_target.target.field.object)

        del self._objects[id]
        if isinstance(obj, Attacker):
            del self._attackers[id]
            for obj2, steps in obj._first_steps.items():
                obj2._attackers.remove(obj)
                for association in steps.values():
                    self._associations.remove(association)

        del self._multiplicity_errors[obj]

        for view in self._views.values():
            view.delete_object(obj)

        for attacker in obj._attackers:
            for association in attacker._first_steps[obj].values():
                self._associations.remove(association)
            del attacker._first_steps[obj]

    def _add_view(self, view: View) -> None:
        self._update_counter(view.id)
        self._views[view.id] = view

    def create_view(self, name: str, *, id: Optional[int] = None) -> View:
        id = self._get_id(id)
        if id in self._views:
            raise InvalidViewException(f"{id} already exists")
        view = View({}, self, name, id)
        self._add_view(view)
        return view

    def view(self, id: int) -> View:
        if not id in self._views:
            raise InvalidViewException(f"{id} doesn't exist")
        return self._views[id]

    def views(self, *, name: Optional[str] = None) -> list[View]:
        return utility.iterable_filter(self._views.values(), name=name)

    def delete_view(self, id: int) -> None:
        if id not in self._views:
            raise InvalidViewException(f"{id} doesn't exist")
        del self._views[id]
