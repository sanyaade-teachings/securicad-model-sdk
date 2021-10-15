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

from io import BytesIO
from typing import Callable

import pytest

from securicad.langspec import TtcDistribution, TtcFunction
from securicad.model import Model, es_serializer, json_serializer, scad_serializer


def _scad_loop(model: Model):
    scad = BytesIO()
    scad_serializer.serialize_model(model, scad)
    return scad_serializer.deserialize_model(scad, validate_icons=False)


@pytest.mark.parametrize(
    "serializer",
    [
        _scad_loop,
        lambda model: json_serializer.deserialize_model(
            json_serializer.serialize_model(model), validate_icons=False
        ),
        lambda model: es_serializer.deserialize_model(
            es_serializer.serialize_model(model), validate_icons=False
        ),
    ],
    ids=["scad", "json", "es"],
)
def test_create_serialize_loop(serializer: Callable[[Model], Model]):
    model = Model(
        lang_id="com.foreseeti.securilang", lang_version="2.1.9", validate_icons=False
    )
    overview = model.create_view("Overview")

    network_birch_cylinder = model.create_object("Network", "birch cylinder")
    network_birch_cylinder.meta["tags"] = {"landing": "1969-06-20T20:17:00Z"}
    host_cedar_trapezoid = model.create_object("Host", "cedar trapezoid")
    network_birch_cylinder.field("hosts").connect(
        host_cedar_trapezoid.field("networks")
    )
    group_larch_heptagon = overview.create_group(
        "larch heptagon", "larch_icon", -100, 100
    )
    group_larch_heptagon.add_object(network_birch_cylinder)
    group_larch_heptagon.add_object(host_cedar_trapezoid, 0, 100)

    network_chinkapin_hexagon = model.create_object("Network", "chinkapin hexagon")
    network_chinkapin_hexagon.defense("staticARPTables").probability = 0.4
    host_walnut_tetrahedron = model.create_object("Host", "walnut tetrahedron")
    host_walnut_tetrahedron.attack_step("compromise").meta["consequence"] = 10
    host_walnut_tetrahedron.attack_step("findExploit").ttc = TtcFunction(
        TtcDistribution.EXPONENTIAL, [1.2]
    )
    network_chinkapin_hexagon.field("hosts").connect(
        host_walnut_tetrahedron.field("networks")
    )
    group_sycamore_circle = overview.create_group(
        "sycamore circle", "cycamore_icon", 100, 100
    )
    group_sycamore_circle.add_object(network_chinkapin_hexagon)
    group_sycamore_circle.add_object(host_walnut_tetrahedron, 0, 100)

    router_sequoia_triangle = model.create_object("Router", "sequoia_triangle")
    overview.add_object(router_sequoia_triangle, 0, 0)
    router_sequoia_triangle.field("networks").connect(
        network_birch_cylinder.field("routers")
    )
    router_sequoia_triangle.field("networks").connect(
        network_chinkapin_hexagon.field("routers")
    )

    attacker_holly_cube = model.create_attacker("holly cube")
    overview.add_object(attacker_holly_cube, 0, -100)
    attacker_holly_cube.connect(host_cedar_trapezoid.attack_step("deployExploit"))

    looped = serializer(model)

    assert sorted([(obj.name, obj.asset_type) for obj in model.objects()]) == sorted(
        [(obj.name, obj.asset_type) for obj in looped.objects()]
    )
    assert (
        looped.object(network_birch_cylinder.id).meta["tags"]["landing"]
        == "1969-06-20T20:17:00Z"
    )
    assert (
        looped.object(host_walnut_tetrahedron.id)
        .attack_step("compromise")
        .meta["consequence"]
        == 10
    )
    assert (
        looped.object(network_chinkapin_hexagon.id)
        .defense("staticARPTables")
        .probability
        == 0.4
    )
    looped_cwtft = (
        looped.object(host_walnut_tetrahedron.id).attack_step("findExploit").ttc
    )
    assert isinstance(looped_cwtft, TtcFunction)
    assert looped_cwtft.distribution is TtcDistribution.EXPONENTIAL
    assert looped_cwtft.arguments == [1.2]
    looped_o = looped.views(name="Overview")[0]
    looped_owt = looped_o.objects(name="walnut tetrahedron")[0]
    assert looped_owt.x == 0
    assert looped_owt.y == 100
    assert sorted(group.name for group in looped_o.groups()) == [
        "larch heptagon",
        "sycamore circle",
    ]
