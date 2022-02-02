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

import collections
import typing
from typing import TYPE_CHECKING, Any, DefaultDict, Optional

from securicad.langspec import Lang

from . import utility
from .association import Association, FieldTarget
from .attacker import Attacker
from .base import Base
from .exceptions import (
    DuplicateAssociationException,
    DuplicateAttackStepException,
    DuplicateIconException,
    DuplicateObjectException,
    DuplicateViewException,
    InvalidModelException,
    MissingAssociationException,
    MissingIconException,
    MissingObjectException,
    MissingViewException,
    ModelException,
)
from .icon import Icon
from .object import Object
from .securilang_validator import SecurilangValidator
from .validator import Validator
from .visual.view import View

if TYPE_CHECKING:
    from .attackstep import AttackStep


class Model(Base):
    def __init__(
        self,
        name: str = "unnamed",
        *,
        lang: Optional[Lang] = None,
        lang_id: Optional[str] = None,
        lang_version: Optional[str] = None,
        validate_icons: bool = True,
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
        if lang and lang.defines["id"] == "com.foreseeti.securilang":
            self._validator: Validator = SecurilangValidator(self, validate_icons)
        else:
            self._validator = Validator(self, validate_icons)
        self._views: dict[int, View] = {}
        self._objects: dict[int, Object] = {}
        self._attackers: dict[int, Attacker] = {}
        self._associations: set[Association] = set()
        self._icons: dict[str, Icon] = {}
        self._counter = 1
        self._multiplicity_errors: DefaultDict[
            Object, list[str]
        ] = collections.defaultdict(list)

    def _get_id(self, id: Optional[int] = None) -> int:
        """
        Return lowest non-taken ID if `id` is not specified, otherwise return `id`.

        This is done because imported group ID's can be potentially huge, using a "dumb" sequential
        counter may yield large object ID's which is not OK with certain serializers, which may
        require small ID's.
        """
        if id is not None:
            return id
        group_ids = {
            group.id for view in self._views.values() for group in view.groups()
        }
        while (  # id's are shared between objects, views, and groups
            self._counter in self._objects
            or self._counter in self._views
            or self._counter in group_ids
        ):
            self._counter += 1
        id = self._counter
        self._counter + 1
        return id

    def _update_counter(self, id: int) -> None:
        self._counter = min(id, self._counter)

    def _add_error(self, obj: Object, error: str):
        self._multiplicity_errors[obj].append(error)

    ##
    # Icon

    def create_icon(self, name: str, format: str, data: bytes, license: str) -> Icon:
        if name in self._icons:
            raise DuplicateIconException(name)
        icon = Icon(
            meta={}, model=self, name=name, format=format, data=data, license=license
        )
        self._icons[name] = icon
        return icon

    def icon(self, name: str) -> Icon:
        if name not in self._icons:
            raise MissingIconException(name)
        return self._icons[name]

    def _delete_icon(self, name: str) -> None:
        if name not in self._icons:
            raise MissingIconException(name)
        del self._icons[name]

    ##
    # Validation

    @property
    def multiplicity_errors(self) -> list[str]:
        return [
            error for errors in self._multiplicity_errors.values() for error in errors
        ]

    @property
    def attacker_errors(self) -> list[str]:
        return self._validator.validate_attackers()

    @property
    def validation_errors(self) -> list[str]:
        return self.multiplicity_errors + self.attacker_errors

    def validate(self) -> None:
        errors = self.validation_errors
        if errors:
            raise InvalidModelException(errors)

    ###
    # Object

    def _add_object(self, obj: Object) -> None:
        self._objects[obj.id] = obj
        self._validator.validate_multiplicity(obj)

    def has_object(self, id: int) -> bool:
        return id in self._objects

    def object(self, id: int) -> Object:
        if not self.has_object(id):
            raise MissingObjectException(id)
        return self._objects[id]

    def objects(
        self, *, name: Optional[str] = None, asset_type: Optional[str] = None
    ) -> list[Object]:
        return utility.iterable_filter(
            self._objects.values(), name=name, asset_type=asset_type
        )

    def create_object(
        self,
        asset_type: str,
        name: str = "",
        *,
        id: Optional[int] = None,
        meta: Optional[dict[str, Any]] = None,
    ) -> Object:
        if asset_type == "Attacker":
            raise ValueError("Use create_attacker().")
        id = self._get_id(id)
        if self.has_object(id):
            raise DuplicateObjectException(self.object(id))
        obj = Object(meta or {}, self, id, asset_type, name)
        self._validator.validate_object(obj)
        self._add_object(obj)
        return obj

    def _delete_object(self, id: int) -> None:
        if not self.has_object(id):
            raise MissingObjectException(id)
        obj = self._objects[id]
        self._update_counter(obj.id)

        for field in obj._associations.values():
            for field_target in set(field.targets):  # copy set
                obj.field(field.name).disconnect(field_target.target.field.object)

        for view in self._views.values():
            if view.has_object(obj):
                view.object(obj).delete()

        del self._objects[id]
        if isinstance(obj, Attacker):
            del self._attackers[id]
            for obj2, steps in obj._first_steps.items():
                obj2._attackers.remove(obj)
                for association in steps.values():
                    self._associations.remove(association)

        del self._multiplicity_errors[obj]

        for attacker in obj._attackers:
            for association in attacker._first_steps[obj].values():
                self._associations.remove(association)
            del attacker._first_steps[obj]

    ##
    # Attacker

    def create_attacker(
        self,
        name: str = "Attacker",
        *,
        id: Optional[int] = None,
        meta: Optional[dict[str, Any]] = None,
    ) -> Attacker:
        id = self._get_id(id)
        if self.has_object(id):
            raise DuplicateObjectException(self.object(id))
        attacker = Attacker(meta or {}, self, id, name)
        self._attackers[attacker.id] = attacker
        self._add_object(attacker)
        return attacker

    def attackers(self, *, name: Optional[str] = None) -> list[Attacker]:
        return utility.iterable_filter(self._attackers.values(), name=name)

    def _check_connection(
        self, attacker: Attacker, obj: Object, attack_step: AttackStep
    ) -> None:
        """Checks that the potential connection is valid in the model."""
        if not self.has_object(attacker.id):
            raise MissingObjectException(attacker)
        if not self.has_object(obj.id):
            raise MissingObjectException(obj)
        if attack_step.name in attacker._first_steps[obj]:
            raise DuplicateAttackStepException(attacker, attack_step)

    def _add_connection(
        self, attacker: Attacker, obj: Object, attack_step: str
    ) -> None:
        association = Association(
            meta={},
            source_object=attacker,
            source_field="firstSteps",
            target_object=obj,
            target_field=f"{attack_step}.attacker",
        )
        attacker._first_steps[obj][attack_step] = association
        obj._attackers.add(attacker)
        self._associations.add(association)

    ##
    # Association

    def _check_association(self, association: Association) -> None:
        if association.source_object == association.target_object:
            raise ModelException(
                f"Cannot connect {association.source_object} to itself."
            )
        if not self.has_object(association.source_object.id):
            raise MissingObjectException(association.source_object)
        if not self.has_object(association.target_object.id):
            raise MissingObjectException(association.target_object)
        if (
            association.target_object
            in association.source_object.field(association.source_field).objects()
        ):
            raise DuplicateAssociationException(association)

    def _add_association(self, association: Association) -> None:
        source_field = association.source_object.field(association.source_field)
        target_field = association.target_object.field(association.target_field)
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
        self._validator.validate_multiplicity(association.source_object)
        self._validator.validate_multiplicity(association.target_object)

    def _create_association(
        self,
        source_object: Object,
        source_field: str,
        target_object: Object,
        target_field: str,
    ) -> None:
        association = Association(
            {}, source_object, source_field, target_object, target_field
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
            raise MissingObjectException(source_object)
        if not self.has_object(target_object.id):
            raise MissingObjectException(target_object)
        if target_object not in source_object.field(source_field).objects():
            raise MissingAssociationException(
                source_object, source_field, target_object
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

    ##
    # View

    def _add_view(self, view: View) -> None:
        self._views[view.id] = view

    def create_view(self, name: str, *, id: Optional[int] = None) -> View:
        id = self._get_id(id)
        if id in self._views:
            raise DuplicateViewException(self.view(id))
        view = View({}, self, name, id)
        self._add_view(view)
        return view

    def view(self, id: int) -> View:
        if not id in self._views:
            raise MissingViewException(id)
        return self._views[id]

    def views(self, *, name: Optional[str] = None) -> list[View]:
        return utility.iterable_filter(self._views.values(), name=name)

    def _delete_view(self, id: int) -> None:
        if id not in self._views:
            raise MissingViewException(id)
        self._update_counter(id)
        del self._views[id]
