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

"""Definition of meta model 'ModelViewsPackage'."""
from functools import partial

import pyecore.ecore as Ecore
from pyecore.ecore import *

name = "ModelViewsPackage"
nsURI = "http:///com/foreseeti/ModelViews.ecore"
nsPrefix = "com.foreseeti.securiCAD"

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)


class View(EObject, metaclass=MetaEClass):

    id = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)
    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    editor = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    zoom = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=1.0
    )
    guideLines = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    snapToGrid = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    loadOnStart = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    routingMethod = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    index = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=0
    )
    onTop = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    viewItem = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    viewConnection = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    groupNode = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(
        self,
        *,
        id=None,
        name=None,
        editor=None,
        viewItem=None,
        zoom=None,
        guideLines=None,
        snapToGrid=None,
        loadOnStart=None,
        routingMethod=None,
        viewConnection=None,
        index=None,
        onTop=None,
        groupNode=None,
    ):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if id is not None:
            self.id = id

        if name is not None:
            self.name = name

        if editor is not None:
            self.editor = editor

        if zoom is not None:
            self.zoom = zoom

        if guideLines is not None:
            self.guideLines = guideLines

        if snapToGrid is not None:
            self.snapToGrid = snapToGrid

        if loadOnStart is not None:
            self.loadOnStart = loadOnStart

        if routingMethod is not None:
            self.routingMethod = routingMethod

        if index is not None:
            self.index = index

        if onTop is not None:
            self.onTop = onTop

        if viewItem:
            self.viewItem.extend(viewItem)

        if viewConnection:
            self.viewConnection.extend(viewConnection)

        if groupNode:
            self.groupNode.extend(groupNode)


class ViewItem(EObject, metaclass=MetaEClass):

    id = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)

    def __init__(self, *, id=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if id is not None:
            self.id = id


class XYPoint(EObject, metaclass=MetaEClass):

    x = EAttribute(eType=EInt, unique=True, derived=False, changeable=True)
    y = EAttribute(eType=EInt, unique=True, derived=False, changeable=True)

    def __init__(self, *, x=None, y=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if x is not None:
            self.x = x

        if y is not None:
            self.y = y


class ModelViews(EObject, metaclass=MetaEClass):

    view = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    grouplayout = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(self, *, view=None, grouplayout=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if view:
            self.view.extend(view)

        if grouplayout:
            self.grouplayout.extend(grouplayout)


class GroupLayout(EObject, metaclass=MetaEClass):

    id = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)
    icon = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    color = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    groupitem = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(self, *, id=None, groupitem=None, icon=None, color=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if id is not None:
            self.id = id

        if icon is not None:
            self.icon = icon

        if color is not None:
            self.color = color

        if groupitem:
            self.groupitem.extend(groupitem)


class Location(XYPoint):

    width = EAttribute(eType=EInt, unique=True, derived=False, changeable=True)
    height = EAttribute(eType=EInt, unique=True, derived=False, changeable=True)

    def __init__(self, *, width=None, height=None, **kwargs):

        super().__init__(**kwargs)

        if width is not None:
            self.width = width

        if height is not None:
            self.height = height


class ViewNode(ViewItem):

    location = EReference(ordered=True, unique=True, containment=True, derived=False)

    def __init__(self, *, location=None, **kwargs):

        super().__init__(**kwargs)

        if location is not None:
            self.location = location


class ViewConnection(ViewItem):

    sourceId = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)
    targetId = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)
    sourceProperty = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    targetProperty = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    bendPoint = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(
        self,
        *,
        bendPoint=None,
        sourceId=None,
        targetId=None,
        sourceProperty=None,
        targetProperty=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        if sourceId is not None:
            self.sourceId = sourceId

        if targetId is not None:
            self.targetId = targetId

        if sourceProperty is not None:
            self.sourceProperty = sourceProperty

        if targetProperty is not None:
            self.targetProperty = targetProperty

        if bendPoint:
            self.bendPoint.extend(bendPoint)


class ObjectView(View):

    objectId = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)

    def __init__(self, *, objectId=None, **kwargs):

        super().__init__(**kwargs)

        if objectId is not None:
            self.objectId = objectId


class GroupItem(XYPoint):

    id = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)

    def __init__(self, *, id=None, **kwargs):

        super().__init__(**kwargs)

        if id is not None:
            self.id = id


class ViewTextNode(ViewNode):

    fgColor = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    bgColor = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    size = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=0
    )
    text = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    horizontalAlign = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=-1
    )

    def __init__(
        self,
        *,
        fgColor=None,
        bgColor=None,
        size=None,
        text=None,
        horizontalAlign=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        if fgColor is not None:
            self.fgColor = fgColor

        if bgColor is not None:
            self.bgColor = bgColor

        if size is not None:
            self.size = size

        if text is not None:
            self.text = text

        if horizontalAlign is not None:
            self.horizontalAlign = horizontalAlign


class GroupNode(ViewNode):
    def __init__(self, **kwargs):

        super().__init__(**kwargs)
