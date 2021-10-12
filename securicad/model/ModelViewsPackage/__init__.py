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
