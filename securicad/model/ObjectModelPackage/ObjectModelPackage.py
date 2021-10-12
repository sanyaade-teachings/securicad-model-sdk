"""Definition of meta model 'ObjectModelPackage'."""
from functools import partial

import pyecore.ecore as Ecore
from pyecore.ecore import *

name = "ObjectModelPackage"
nsURI = "http:///com/foreseeti/ObjectModel.ecore"
nsPrefix = "com.foreseeti.kernalCAD"

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)


@abstract
class Serializable(EObject, metaclass=MetaEClass):
    def __init__(self):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()


class Point(EObject, metaclass=MetaEClass):

    x = EAttribute(eType=EInt, unique=True, derived=False, changeable=True)
    y = EAttribute(eType=EInt, unique=True, derived=False, changeable=True)
    width = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=-1
    )
    height = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=-1
    )

    def __init__(self, *, x=None, y=None, width=None, height=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if x is not None:
            self.x = x

        if y is not None:
            self.y = y

        if width is not None:
            self.width = width

        if height is not None:
            self.height = height


class XMINode(EObject, metaclass=MetaEClass):

    description = EAttribute(eType=EString, unique=True, derived=False, changeable=True)

    def __init__(self, *, description=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if description is not None:
            self.description = description


class XMIObjectModel(Serializable):

    samplingMethod = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    samples = EAttribute(
        eType=ELong, unique=True, derived=False, changeable=True, default_value=1000
    )
    subModelSamples = EAttribute(
        eType=ELong, unique=True, derived=False, changeable=True, default_value=1
    )
    integerUniformJumpRange = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=1
    )
    integerPrunedUniformJumpStep = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=1
    )
    doubleUniformJumpRange = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    booleanJumpProbability = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    considerInvariantsForSampling = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=True
    )
    checkInvariants = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=True
    )
    templateAttributeOCLEnable = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    subModelOneTime = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=True
    )
    burnInSamples = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=0
    )
    warningThreshold = EAttribute(
        eType=ELong, unique=True, derived=False, changeable=True
    )
    persistence = EAttribute(
        eType=EDouble,
        unique=True,
        derived=False,
        changeable=True,
        default_value=1.7976931348623157e308,
    )
    currency = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True, default_value="EUR"
    )
    attackerProfile = EAttribute(
        eType=EString,
        unique=True,
        derived=False,
        changeable=True,
        default_value="Advanced Persistent Threat",
    )
    objects = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    associations = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    groups = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    exportAttributes = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    defenseDefaultValueConfigurations = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(
        self,
        *,
        objects=None,
        associations=None,
        groups=None,
        samplingMethod=None,
        samples=None,
        subModelSamples=None,
        integerUniformJumpRange=None,
        integerPrunedUniformJumpStep=None,
        doubleUniformJumpRange=None,
        booleanJumpProbability=None,
        considerInvariantsForSampling=None,
        checkInvariants=None,
        templateAttributeOCLEnable=None,
        subModelOneTime=None,
        burnInSamples=None,
        warningThreshold=None,
        exportAttributes=None,
        defenseDefaultValueConfigurations=None,
        persistence=None,
        currency=None,
        attackerProfile=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        if samplingMethod is not None:
            self.samplingMethod = samplingMethod

        if samples is not None:
            self.samples = samples

        if subModelSamples is not None:
            self.subModelSamples = subModelSamples

        if integerUniformJumpRange is not None:
            self.integerUniformJumpRange = integerUniformJumpRange

        if integerPrunedUniformJumpStep is not None:
            self.integerPrunedUniformJumpStep = integerPrunedUniformJumpStep

        if doubleUniformJumpRange is not None:
            self.doubleUniformJumpRange = doubleUniformJumpRange

        if booleanJumpProbability is not None:
            self.booleanJumpProbability = booleanJumpProbability

        if considerInvariantsForSampling is not None:
            self.considerInvariantsForSampling = considerInvariantsForSampling

        if checkInvariants is not None:
            self.checkInvariants = checkInvariants

        if templateAttributeOCLEnable is not None:
            self.templateAttributeOCLEnable = templateAttributeOCLEnable

        if subModelOneTime is not None:
            self.subModelOneTime = subModelOneTime

        if burnInSamples is not None:
            self.burnInSamples = burnInSamples

        if warningThreshold is not None:
            self.warningThreshold = warningThreshold

        if persistence is not None:
            self.persistence = persistence

        if currency is not None:
            self.currency = currency

        if attackerProfile is not None:
            self.attackerProfile = attackerProfile

        if objects:
            self.objects.extend(objects)

        if associations:
            self.associations.extend(associations)

        if groups:
            self.groups.extend(groups)

        if exportAttributes:
            self.exportAttributes.extend(exportAttributes)

        if defenseDefaultValueConfigurations:
            self.defenseDefaultValueConfigurations.extend(
                defenseDefaultValueConfigurations
            )


class XMIDistribution(Serializable):

    type = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    parameters = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(self, *, type=None, parameters=None, **kwargs):

        super().__init__(**kwargs)

        if type is not None:
            self.type = type

        if parameters:
            self.parameters.extend(parameters)


class XMIDistributionParameter(Serializable):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    value = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )

    def __init__(self, *, name=None, value=None, **kwargs):

        super().__init__(**kwargs)

        if name is not None:
            self.name = name

        if value is not None:
            self.value = value


class XMISelectedAttribute(Serializable):

    ObjectID = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)
    AttributeName = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )

    def __init__(self, *, ObjectID=None, AttributeName=None, **kwargs):

        super().__init__(**kwargs)

        if ObjectID is not None:
            self.ObjectID = ObjectID

        if AttributeName is not None:
            self.AttributeName = AttributeName


class XMIObjectGroupItem(Serializable):

    id = EAttribute(eType=EString, unique=True, derived=False, changeable=True)

    def __init__(self, *, id=None, **kwargs):

        super().__init__(**kwargs)

        if id is not None:
            self.id = id


class XMIAttribute(Serializable, XMINode):

    metaConceptId = EAttribute(
        eType=ELong, unique=True, derived=False, changeable=True, default_value=0
    )
    metaConcept = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    evidence = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    cost = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    minTTCAssertion = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    maxTTCAssertion = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    minPercentageAssertion = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    maxPercentageAssertion = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    consequence = EAttribute(
        eType=EInt, unique=True, derived=False, changeable=True, default_value=0
    )
    costLowerLimit = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    costUpperLimit = EAttribute(
        eType=EDouble, unique=True, derived=False, changeable=True, default_value=0.0
    )
    evidenceDistribution = EReference(
        ordered=True, unique=True, containment=True, derived=False
    )
    localTtcDistribution = EReference(
        ordered=True, unique=True, containment=True, derived=False
    )

    def __init__(
        self,
        *,
        metaConceptId=None,
        metaConcept=None,
        evidenceDistribution=None,
        evidence=None,
        cost=None,
        localTtcDistribution=None,
        minTTCAssertion=None,
        maxTTCAssertion=None,
        minPercentageAssertion=None,
        maxPercentageAssertion=None,
        consequence=None,
        costLowerLimit=None,
        costUpperLimit=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        if metaConceptId is not None:
            self.metaConceptId = metaConceptId

        if metaConcept is not None:
            self.metaConcept = metaConcept

        if evidence is not None:
            self.evidence = evidence

        if cost is not None:
            self.cost = cost

        if minTTCAssertion is not None:
            self.minTTCAssertion = minTTCAssertion

        if maxTTCAssertion is not None:
            self.maxTTCAssertion = maxTTCAssertion

        if minPercentageAssertion is not None:
            self.minPercentageAssertion = minPercentageAssertion

        if maxPercentageAssertion is not None:
            self.maxPercentageAssertion = maxPercentageAssertion

        if consequence is not None:
            self.consequence = consequence

        if costLowerLimit is not None:
            self.costLowerLimit = costLowerLimit

        if costUpperLimit is not None:
            self.costUpperLimit = costUpperLimit

        if evidenceDistribution is not None:
            self.evidenceDistribution = evidenceDistribution

        if localTtcDistribution is not None:
            self.localTtcDistribution = localTtcDistribution


class XMIObject(Serializable, XMINode):

    id = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    metaConceptId = EAttribute(
        eType=ELong, unique=True, derived=False, changeable=True, default_value=0
    )
    metaConcept = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    template = EAttribute(
        eType=EBooleanObject, unique=True, derived=False, changeable=True
    )
    exportedId = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)
    maximize = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    showAttributes = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    innerObject = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    capex = EAttribute(eType=EDouble, unique=True, derived=False, changeable=True)
    opex = EAttribute(eType=EDouble, unique=True, derived=False, changeable=True)
    attributesJsonString = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True, default_value="{}"
    )
    evidenceAttributes = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    existence = EReference(ordered=True, unique=True, containment=True, derived=False)
    locations = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )
    children = EReference(
        ordered=True, unique=True, containment=False, derived=False, upper=-1
    )

    def __init__(
        self,
        *,
        id=None,
        name=None,
        metaConceptId=None,
        metaConcept=None,
        template=None,
        evidenceAttributes=None,
        existence=None,
        locations=None,
        exportedId=None,
        children=None,
        maximize=None,
        showAttributes=None,
        innerObject=None,
        capex=None,
        opex=None,
        attributesJsonString=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        if id is not None:
            self.id = id

        if name is not None:
            self.name = name

        if metaConceptId is not None:
            self.metaConceptId = metaConceptId

        if metaConcept is not None:
            self.metaConcept = metaConcept

        if template is not None:
            self.template = template

        if exportedId is not None:
            self.exportedId = exportedId

        if maximize is not None:
            self.maximize = maximize

        if showAttributes is not None:
            self.showAttributes = showAttributes

        if innerObject is not None:
            self.innerObject = innerObject

        if capex is not None:
            self.capex = capex

        if opex is not None:
            self.opex = opex

        if attributesJsonString is not None:
            self.attributesJsonString = attributesJsonString

        if evidenceAttributes:
            self.evidenceAttributes.extend(evidenceAttributes)

        if existence is not None:
            self.existence = existence

        if locations:
            self.locations.extend(locations)

        if children:
            self.children.extend(children)


class XMIAssociation(Serializable, XMINode):

    sourceObject = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    targetObject = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    id = EAttribute(eType=ELong, unique=True, derived=False, changeable=True)
    sourceProperty = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    targetProperty = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True
    )
    existence = EReference(ordered=True, unique=True, containment=True, derived=False)
    locations = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(
        self,
        *,
        sourceObject=None,
        targetObject=None,
        id=None,
        sourceProperty=None,
        targetProperty=None,
        existence=None,
        locations=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        if sourceObject is not None:
            self.sourceObject = sourceObject

        if targetObject is not None:
            self.targetObject = targetObject

        if id is not None:
            self.id = id

        if sourceProperty is not None:
            self.sourceProperty = sourceProperty

        if targetProperty is not None:
            self.targetProperty = targetProperty

        if existence is not None:
            self.existence = existence

        if locations:
            self.locations.extend(locations)


class XMIDefenseDefaultValueConfiguration(Serializable, XMINode):

    metaConcept = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    attributeConfigurations = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(self, *, metaConcept=None, attributeConfigurations=None, **kwargs):

        super().__init__(**kwargs)

        if metaConcept is not None:
            self.metaConcept = metaConcept

        if attributeConfigurations:
            self.attributeConfigurations.extend(attributeConfigurations)


class XMIAttributeConfiguration(Serializable, XMINode):

    metaConcept = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    defaultValue = EReference(
        ordered=True, unique=True, containment=True, derived=False
    )

    def __init__(self, *, metaConcept=None, defaultValue=None, **kwargs):

        super().__init__(**kwargs)

        if metaConcept is not None:
            self.metaConcept = metaConcept

        if defaultValue is not None:
            self.defaultValue = defaultValue


class XMIObjectGroup(Serializable, XMINode):

    id = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    expand = EAttribute(
        eType=EBoolean, unique=True, derived=False, changeable=True, default_value=False
    )
    attributesJsonString = EAttribute(
        eType=EString, unique=True, derived=False, changeable=True, default_value="{}"
    )
    items = EReference(
        ordered=True, unique=True, containment=True, derived=False, upper=-1
    )

    def __init__(
        self,
        *,
        id=None,
        name=None,
        expand=None,
        items=None,
        attributesJsonString=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        if id is not None:
            self.id = id

        if name is not None:
            self.name = name

        if expand is not None:
            self.expand = expand

        if attributesJsonString is not None:
            self.attributesJsonString = attributesJsonString

        if items:
            self.items.extend(items)
