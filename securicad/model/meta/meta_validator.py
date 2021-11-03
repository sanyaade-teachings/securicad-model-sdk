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
