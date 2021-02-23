# Copyright 2020-2021 Foreseeti AB <https://foreseeti.com>
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

from collections import defaultdict
from typing import Any, Dict, List, Optional


class Model:
    def __init__(self, model: Dict[str, Any]) -> None:
        self.model = model

    def disable_attackstep(
        self, metaconcept: str, attackstep: str, name: Optional[str] = None
    ) -> None:
        for obj in self.model["objects"].values():
            if obj["metaconcept"] == metaconcept:
                if name is not None and obj["name"] != name:
                    continue
                self.__set_evidence(obj, attackstep, distribution="Infinity")

    def set_high_value_assets(self, high_value_assets: List[Dict[str, Any]]) -> None:
        # Collect the high value assets under their metaconcept
        hv_assets = defaultdict(list)
        for hv_asset in high_value_assets:
            hv_assets[hv_asset["metaconcept"]].append(hv_asset)

        # Check if any of the objects are eligible as a high value asset
        for obj in self.model["objects"].values():
            if obj["metaconcept"] in hv_assets:
                for hv_asset in hv_assets[obj["metaconcept"]]:
                    if self.__is_high_value_asset(obj, hv_asset):
                        self.__set_high_value_asset(obj, hv_asset)

    def __is_high_value_asset(
        self, obj: Dict[str, Any], hv_asset: Dict[str, Any]
    ) -> bool:
        # Check if a model object matches any of the high value assets
        if "id" not in hv_asset or hv_asset["id"] is None:
            return True
        if hv_asset["id"]["type"] == "name":
            value = hv_asset["id"]["value"]
            obj_name = obj["name"]
            return obj_name == value
        if hv_asset["id"]["type"] == "tag":
            key = hv_asset["id"]["key"]
            value = hv_asset["id"]["value"]
            obj_tags = obj.get("tags", {})
            return key in obj_tags and obj_tags[key] == value
        return False

    def __set_high_value_asset(
        self, obj: Dict[str, Any], hv_asset: Dict[str, Any]
    ) -> None:
        attackstep = hv_asset["attackstep"]
        if "consequence" in hv_asset and hv_asset["consequence"] is not None:
            consequence = hv_asset["consequence"]
        else:
            consequence = 10
        self.__set_evidence(obj, attackstep, consequence=consequence)

    def __set_evidence(
        self, obj: Dict[str, Any], attackstep: str, consequence=None, distribution=None
    ):
        for step in obj["attacksteps"]:
            if step["name"] == attackstep:
                if consequence is not None:
                    step["consequence"] = consequence
                if distribution is not None:
                    step["distribution"] = distribution
                break
        else:
            obj["attacksteps"].append(
                {
                    "name": attackstep,
                    "distribution": distribution,
                    "lowercost": None,
                    "uppercost": None,
                    "consequence": consequence,
                }
            )
