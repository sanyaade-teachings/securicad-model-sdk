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

from os import PathLike
from typing import IO, Any, Dict, List, Optional, Tuple, Union

from .lang_types import (
    Asset,
    Association,
    AttackStep,
    AttackStepType,
    Category,
    Field,
    Multiplicity,
    Risk,
    Steps,
    Variable,
)
from .reader import LangReader
from .step_types import (
    StepAttackStep,
    StepCollect,
    StepDifference,
    StepExpression,
    StepField,
    StepIntersection,
    StepSubType,
    StepTransitive,
    StepUnion,
    StepVariable,
)
from .ttc_types import (
    TtcAddition,
    TtcDistribution,
    TtcDivision,
    TtcExponentiation,
    TtcExpression,
    TtcFunction,
    TtcMultiplication,
    TtcNumber,
    TtcSubtraction,
)


class Lang:
    def __init__(self, file: Union[str, PathLike[Any], IO[bytes]]) -> None:
        self._reader = LangReader(file)
        self.defines: Dict[str, str] = self._reader.langspec["defines"]
        self.categories: Dict[str, Category] = {}
        self.assets: Dict[str, Asset] = {}
        self.associations: List[Association] = []
        self.license: Optional[str] = self._reader.license
        self.notice: Optional[str] = self._reader.notice
        self._create_lang()
        del self._reader

    def _create_lang(self) -> None:
        for category in self._reader.langspec["categories"]:
            category_ = self._create_category(category)
            self.categories[category_.name] = category_

        for asset in self._reader.langspec["assets"]:
            asset_ = self._create_asset(asset)
            self.assets[asset_.name] = asset_

        for asset in self._reader.langspec["assets"]:
            if asset["superAsset"] is None:
                continue
            asset_ = self.assets[asset["name"]]
            super_asset_ = self.assets[asset["superAsset"]]
            asset_.super_asset = super_asset_

        for association in self._reader.langspec["associations"]:
            association_ = self._create_association(association)
            self.associations.append(association_)

        self._create_step_expressions()

    def _create_category(self, category: Dict[str, Any]) -> Category:
        return Category(name=category["name"], meta=category["meta"])

    def _create_asset(self, asset: Dict[str, Any]) -> Asset:
        category_ = self.categories[asset["category"]]
        asset_ = Asset(
            name=asset["name"],
            meta=asset["meta"],
            category=category_,
            is_abstract=asset["isAbstract"],
            _svg_icon=self._reader.svg_icons.get(asset["name"]),
            _png_icon=self._reader.png_icons.get(asset["name"]),
        )
        category_.assets[asset_.name] = asset_
        for variable in asset["variables"]:
            variable_ = self._create_variable(asset_, variable)
            asset_._variables[variable_.name] = variable_
        for attack_step in asset["attackSteps"]:
            attack_step_ = self._create_attack_step(asset_, attack_step)
            asset_._attack_steps[attack_step_.name] = attack_step_
        return asset_

    def _create_variable(self, asset_: Asset, variable: Dict[str, Any]) -> Variable:
        return Variable(name=variable["name"], asset=asset_)

    def _create_attack_step(
        self, asset_: Asset, attack_step: Dict[str, Any]
    ) -> AttackStep:
        def create_risk(risk: Optional[Dict[str, bool]]) -> Optional[Risk]:
            if risk is None:
                return None
            return Risk(
                is_confidentiality=risk["isConfidentiality"],
                is_integrity=risk["isIntegrity"],
                is_availability=risk["isAvailability"],
            )

        def create_ttc(
            ttc_expression: Optional[Dict[str, Any]]
        ) -> Optional[TtcExpression]:
            if ttc_expression is None:
                return None
            return self._create_ttc_expression(ttc_expression)

        def create_steps(steps: Optional[Dict[str, Any]]) -> Optional[Steps]:
            if not steps:
                return None
            return Steps(overrides=steps["overrides"])

        return AttackStep(
            name=attack_step["name"],
            meta=attack_step["meta"],
            asset=asset_,
            type=AttackStepType(attack_step["type"]),
            _tags=set(attack_step["tags"]),
            _risk=create_risk(attack_step["risk"]),
            _ttc=create_ttc(attack_step["ttc"]),
            _requires=create_steps(attack_step["requires"]),
            _reaches=create_steps(attack_step["reaches"]),
        )

    def _create_ttc_expression(self, ttc_expression: Dict[str, Any]) -> TtcExpression:
        if ttc_expression["type"] in {
            "addition",
            "subtraction",
            "multiplication",
            "division",
            "exponentiation",
        }:
            lhs = self._create_ttc_expression(ttc_expression["lhs"])
            rhs = self._create_ttc_expression(ttc_expression["rhs"])
            if ttc_expression["type"] == "addition":
                return TtcAddition(lhs=lhs, rhs=rhs)
            if ttc_expression["type"] == "subtraction":
                return TtcSubtraction(lhs=lhs, rhs=rhs)
            if ttc_expression["type"] == "multiplication":
                return TtcMultiplication(lhs=lhs, rhs=rhs)
            if ttc_expression["type"] == "division":
                return TtcDivision(lhs=lhs, rhs=rhs)
            if ttc_expression["type"] == "exponentiation":
                return TtcExponentiation(lhs=lhs, rhs=rhs)
            raise RuntimeError(
                f"Failed to create TTC expression with type '{ttc_expression['type']}'"
            )
        if ttc_expression["type"] == "function":
            return TtcFunction(
                distribution=TtcDistribution(ttc_expression["name"]),
                arguments=ttc_expression["arguments"],
            )
        if ttc_expression["type"] == "number":
            return TtcNumber(value=ttc_expression["value"])
        raise RuntimeError(
            f"Failed to create TTC expression with type '{ttc_expression['type']}'"
        )

    def _create_association(self, association: Dict[str, Any]) -> Association:
        left_asset_ = self.assets[association["leftAsset"]]
        right_asset_ = self.assets[association["rightAsset"]]
        left_field_ = Field(
            name=association["leftField"],
            asset=right_asset_,
            multiplicity=self._create_multiplicity(association["leftMultiplicity"]),
        )
        right_field_ = Field(
            name=association["rightField"],
            asset=left_asset_,
            multiplicity=self._create_multiplicity(association["rightMultiplicity"]),
        )
        association_ = Association(
            name=association["name"],
            meta=association["meta"],
            left_field=left_field_,
            right_field=right_field_,
        )
        right_asset_._fields[left_field_.name] = left_field_
        left_asset_._fields[right_field_.name] = right_field_
        left_field_.target = right_field_
        right_field_.target = left_field_
        left_field_.association = association_
        right_field_.association = association_
        return association_

    def _create_multiplicity(self, multiplicity: Dict[str, Any]) -> Multiplicity:
        # pylint: disable=no-value-for-parameter
        return Multiplicity((multiplicity["min"], multiplicity["max"]))  # type: ignore

    def _create_step_expressions(self) -> None:
        variable_targets_: Dict[Tuple[str, str], Asset] = {}

        for asset in self._reader.langspec["assets"]:
            asset_ = self.assets[asset["name"]]
            for variable in asset["variables"]:
                variable_ = asset_._variables[variable["name"]]
                target_ = self._get_step_target(asset_, variable["stepExpression"])
                variable_targets_[(variable_.asset.name, variable_.name)] = target_

        for asset in self._reader.langspec["assets"]:
            asset_ = self.assets[asset["name"]]
            for variable in asset["variables"]:
                variable_ = asset_._variables[variable["name"]]
                variable_.step_expression = self._create_step_expression(
                    asset_, variable["stepExpression"], variable_targets_
                )
            for attack_step in asset["attackSteps"]:
                attack_step_ = asset_._attack_steps[attack_step["name"]]
                if attack_step_._requires:
                    for step_expression in attack_step["requires"]["stepExpressions"]:
                        attack_step_._requires.step_expressions.append(
                            self._create_step_expression(
                                asset_, step_expression, variable_targets_
                            )
                        )
                if attack_step_._reaches:
                    for step_expression in attack_step["reaches"]["stepExpressions"]:
                        attack_step_._reaches.step_expressions.append(
                            self._create_step_expression(
                                asset_, step_expression, variable_targets_
                            )
                        )

    def _get_step_target(
        self, source_: Asset, step_expression: Dict[str, Any]
    ) -> Asset:
        def get_asset(asset_name: str) -> Dict[str, Any]:
            for asset in self._reader.langspec["assets"]:
                if asset["name"] == asset_name:
                    return asset
            raise RuntimeError(f"Failed to get asset '{asset_name}'")

        def get_variable(asset_name: str, variable_name: str) -> Dict[str, Any]:
            asset = get_asset(asset_name)
            for variable in asset["variables"]:
                if variable["name"] == variable_name:
                    return variable
            if asset["superAsset"] is None:
                raise RuntimeError(
                    f"Failed to get variable '{asset_name}.{variable_name}'"
                )
            return get_variable(asset["superAsset"], variable_name)

        if step_expression["type"] in {"union", "intersection", "difference"}:
            lhs_target_ = self._get_step_target(source_, step_expression["lhs"])
            rhs_target_ = self._get_step_target(source_, step_expression["rhs"])
            target_ = lhs_target_ | rhs_target_
            assert target_ is not None
            return target_
        if step_expression["type"] == "collect":
            return self._get_step_target(
                self._get_step_target(source_, step_expression["lhs"]),
                step_expression["rhs"],
            )
        if step_expression["type"] == "transitive":
            return source_
        if step_expression["type"] == "subType":
            return self.assets[step_expression["subType"]]
        if step_expression["type"] == "field":
            return source_.fields[step_expression["name"]].target.asset
        if step_expression["type"] == "attackStep":
            return source_.attack_steps[step_expression["name"]].asset
        if step_expression["type"] == "variable":
            return self._get_step_target(
                source_,
                get_variable(source_.name, step_expression["name"])["stepExpression"],
            )
        raise RuntimeError(
            f"Failed to get target of step expression with type '{step_expression['type']}'"
        )

    def _create_step_expression(
        self,
        source_: Asset,
        step_expression: Dict[str, Any],
        variable_targets_: Dict[Tuple[str, str], Asset],
    ) -> StepExpression:
        if step_expression["type"] in {"union", "intersection", "difference"}:
            lhs_ = self._create_step_expression(
                source_, step_expression["lhs"], variable_targets_
            )
            rhs_ = self._create_step_expression(
                source_, step_expression["rhs"], variable_targets_
            )
            target_ = lhs_.target_asset | rhs_.target_asset
            assert target_ is not None
            if step_expression["type"] == "union":
                return StepUnion(
                    source_asset=source_, target_asset=target_, lhs=lhs_, rhs=rhs_
                )
            if step_expression["type"] == "intersection":
                return StepIntersection(
                    source_asset=source_, target_asset=target_, lhs=lhs_, rhs=rhs_
                )
            if step_expression["type"] == "difference":
                return StepDifference(
                    source_asset=source_, target_asset=target_, lhs=lhs_, rhs=rhs_
                )
            raise RuntimeError(
                f"Failed to create step expression with type '{step_expression['type']}'"
            )
        if step_expression["type"] == "collect":
            lhs_ = self._create_step_expression(
                source_, step_expression["lhs"], variable_targets_
            )
            rhs_ = self._create_step_expression(
                lhs_.target_asset, step_expression["rhs"], variable_targets_
            )
            return StepCollect(
                source_asset=source_, target_asset=rhs_.target_asset, lhs=lhs_, rhs=rhs_
            )
        if step_expression["type"] == "transitive":
            step_expression_ = self._create_step_expression(
                source_, step_expression["stepExpression"], variable_targets_
            )
            return StepTransitive(
                source_asset=source_,
                target_asset=source_,
                step_expression=step_expression_,
            )
        if step_expression["type"] == "subType":
            sub_type_ = self.assets[step_expression["subType"]]
            step_expression_ = self._create_step_expression(
                source_, step_expression["stepExpression"], variable_targets_
            )
            return StepSubType(
                source_asset=source_,
                target_asset=sub_type_,
                sub_type=sub_type_,
                step_expression=step_expression_,
            )
        if step_expression["type"] == "field":
            field_ = source_.fields[step_expression["name"]]
            return StepField(
                source_asset=source_, target_asset=field_.target.asset, field=field_
            )
        if step_expression["type"] == "attackStep":
            attack_step_ = source_.attack_steps[step_expression["name"]]
            return StepAttackStep(
                source_asset=source_,
                target_asset=attack_step_.asset,
                attack_step=attack_step_,
            )
        if step_expression["type"] == "variable":
            variable_ = source_.variables[step_expression["name"]]
            target_ = variable_targets_[(variable_.asset.name, variable_.name)]
            return StepVariable(
                source_asset=source_, target_asset=target_, variable=variable_
            )
        raise RuntimeError(
            f"Failed to create step expression with type '{step_expression['type']}'"
        )
