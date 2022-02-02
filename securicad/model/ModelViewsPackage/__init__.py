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

from . import ModelViewsPackage
from .ModelViewsPackage import (
    GroupItem,
    GroupLayout,
    GroupNode,
    Location,
    ModelViews,
    ObjectView,
    View,
    ViewConnection,
    ViewItem,
    ViewNode,
    ViewTextNode,
    XYPoint,
    eClass,
    eClassifiers,
    getEClassifier,
    name,
    nsPrefix,
    nsURI,
)

__all__ = [
    "View",
    "ViewItem",
    "Location",
    "ViewNode",
    "ViewConnection",
    "XYPoint",
    "ModelViews",
    "ObjectView",
    "ViewTextNode",
    "GroupNode",
    "GroupLayout",
    "GroupItem",
]

eSubpackages = []
eSuperPackage = None
ModelViewsPackage.eSubpackages = eSubpackages
ModelViewsPackage.eSuperPackage = eSuperPackage

View.viewItem.eType = ViewItem
View.viewConnection.eType = ViewConnection
View.groupNode.eType = GroupNode
ViewNode.location.eType = Location
ViewConnection.bendPoint.eType = XYPoint
ModelViews.view.eType = View
ModelViews.grouplayout.eType = GroupLayout
GroupLayout.groupitem.eType = GroupItem

otherClassifiers = []

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
