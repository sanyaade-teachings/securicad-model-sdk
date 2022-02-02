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

from . import ObjectModelPackage
from .ObjectModelPackage import (
    Point,
    Serializable,
    XMIAssociation,
    XMIAttribute,
    XMIAttributeConfiguration,
    XMIDefenseDefaultValueConfiguration,
    XMIDistribution,
    XMIDistributionParameter,
    XMINode,
    XMIObject,
    XMIObjectGroup,
    XMIObjectGroupItem,
    XMIObjectModel,
    XMISelectedAttribute,
    eClass,
    eClassifiers,
    getEClassifier,
    name,
    nsPrefix,
    nsURI,
)

__all__ = [
    "XMIAttribute",
    "XMIObject",
    "XMIAssociation",
    "XMIObjectModel",
    "XMIDistribution",
    "XMIDistributionParameter",
    "XMISelectedAttribute",
    "Serializable",
    "Point",
    "XMINode",
    "XMIDefenseDefaultValueConfiguration",
    "XMIAttributeConfiguration",
    "XMIObjectGroup",
    "XMIObjectGroupItem",
]

eSubpackages = []
eSuperPackage = None
ObjectModelPackage.eSubpackages = eSubpackages
ObjectModelPackage.eSuperPackage = eSuperPackage

XMIAttribute.evidenceDistribution.eType = XMIDistribution
XMIAttribute.localTtcDistribution.eType = XMIDistribution
XMIObject.evidenceAttributes.eType = XMIAttribute
XMIObject.existence.eType = XMIDistribution
XMIObject.locations.eType = Point
XMIObject.children.eType = XMIObject
XMIAssociation.existence.eType = XMIDistribution
XMIAssociation.locations.eType = Point
XMIObjectModel.objects.eType = XMIObject
XMIObjectModel.associations.eType = XMIAssociation
XMIObjectModel.groups.eType = XMIObjectGroup
XMIObjectModel.exportAttributes.eType = XMISelectedAttribute
XMIObjectModel.defenseDefaultValueConfigurations.eType = (
    XMIDefenseDefaultValueConfiguration
)
XMIDistribution.parameters.eType = XMIDistributionParameter
XMIDefenseDefaultValueConfiguration.attributeConfigurations.eType = (
    XMIAttributeConfiguration
)
XMIAttributeConfiguration.defaultValue.eType = XMIDistribution
XMIObjectGroup.items.eType = XMIObjectGroupItem

otherClassifiers = []

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
