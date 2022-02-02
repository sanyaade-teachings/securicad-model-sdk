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

import importlib.resources
import json
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import jsonschema

if TYPE_CHECKING:  # pragma: no cover
    from securicad.model import Model
    from securicad.model.base import Base


@lru_cache
def schema(name: str) -> dict[str, Any]:
    with importlib.resources.open_binary(
        "securicad.model.meta", f"{name}.schema.json"
    ) as fp:
        return json.load(fp)


def validate(instance: Base, name: str):
    jsonschema.validate(instance.meta, schema(name))  # type: ignore


def validate_model(model: Model):
    validate(model, "model")
    for obj in model._objects.values():
        validate(obj, "object")
        for attack_step in obj._attack_steps.values():
            validate(attack_step, "attackstep")
    for view in model._views.values():
        validate(view, "view")
        for group in view.groups():
            validate(group, "group")
