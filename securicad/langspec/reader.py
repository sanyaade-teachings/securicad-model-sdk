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
import re
import zipfile
from os import PathLike
from typing import IO, Any, AnyStr, Dict, Optional, Union

import jsonschema

MISSING: Dict[str, Any] = {}


class LangReader:
    _identifier_pattern = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

    def __init__(self, file: Union[str, PathLike[Any], IO[bytes]]) -> None:
        self.langspec: Dict[str, Any] = MISSING
        self.svg_icons: Dict[str, bytes] = {}
        self.png_icons: Dict[str, bytes] = {}
        self.license: Optional[str] = None
        self.notice: Optional[str] = None
        self._read_zip_file(file)

    def _read_zip_file(self, file: Union[str, PathLike[Any], IO[bytes]]) -> None:
        with zipfile.ZipFile(file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.is_dir():
                    continue
                if zip_info.filename == "langspec.json":
                    with zip_file.open(zip_info) as fp:
                        self.langspec = LangReader._read_langspec(fp)
                elif zip_info.filename.startswith("icons/"):
                    if zip_info.filename.endswith(".svg"):
                        asset_name = zip_info.filename[len("icons/") : -len(".svg")]
                        if LangReader._is_identifier(asset_name):
                            self.svg_icons[asset_name] = zip_file.read(zip_info)
                    elif zip_info.filename.endswith(".png"):
                        asset_name = zip_info.filename[len("icons/") : -len(".png")]
                        if LangReader._is_identifier(asset_name):
                            self.png_icons[asset_name] = zip_file.read(zip_info)
                elif zip_info.filename == "LICENSE":
                    self.license = zip_file.read(zip_info).decode("utf-8")
                elif zip_info.filename == "NOTICE":
                    self.notice = zip_file.read(zip_info).decode("utf-8")

        if self.langspec is MISSING:
            raise ValueError('File "langspec.json" not found')

    @staticmethod
    def _read_langspec(fp: IO[AnyStr]) -> Dict[str, Any]:
        """
        This function reads and validates a langspec JSON file from 'fp'.
        """
        langspec = json.load(fp, parse_constant=LangReader._parse_constant)
        langspec_schema = LangReader._read_langspec_schema()
        jsonschema.validate(instance=langspec, schema=langspec_schema)
        return langspec

    @staticmethod
    def _read_langspec_schema() -> Dict[str, Any]:
        """
        This function returns the JSON Schema for langspec JSON files.
        The schema file is located in the package "securicad.langspec",
        and is named "lang.schema.json".
        """
        with importlib.resources.open_binary(
            "securicad.langspec", "lang.schema.json"
        ) as fp:
            return json.load(fp, parse_constant=LangReader._parse_constant)

    @staticmethod
    def _is_identifier(string: str) -> bool:
        """
        This function returns whether 'string' is a valid MAL identifier.
        """
        return LangReader._identifier_pattern.fullmatch(string) is not None

    @staticmethod
    def _parse_constant(string: str) -> None:
        """
        This function should be passed to json.load() and json.loads(), e.g.

            data = json.loads("{}", parse_constant=LangReader._parse_constant)

        This function will then be called for '-Infinity', 'Infinity', and 'NaN',
        which are not valid JSON constants.
        """
        raise ValueError(f'Invalid JSON constant "{string}"')
