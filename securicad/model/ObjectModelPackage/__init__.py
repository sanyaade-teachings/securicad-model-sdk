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
