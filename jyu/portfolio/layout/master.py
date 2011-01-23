# -*- coding: utf-8 -*-
"""Adds layout support to your content type"""
import os.path

from rwproperty import getproperty, setproperty
from StringIO import StringIO

from lxml import etree
from five import grok

from zope import schema
from zope.interface import Interface, alsoProvides

from plone.directives import form

from plone.dexterity.interfaces import IDexterityContent

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.portfolio.layout")

DEFAULT_LAYOUT = open(
        os.path.join(
                os.path.dirname(__file__),
                'default-layout-content.html'
            )
    ).read().decode('utf-8')


class IHasLayout(Interface):
    """Marker interface for an object with a layout
    """

class ILayout(form.Schema):
    """Behavior interface to make a type support layout.
    """
    form.fieldset('layout', label=_(u"Layout"), fields=['content'])
    content = schema.Text(
            title=_(u"layout_content_label",
                    default=u"Content"),
            description=_(u"layout_content_description",
                          u"Content of the object"),
            required=False,
            default=DEFAULT_LAYOUT,
        )
alsoProvides(ILayout, form.IFormFieldProvider)


class Content(grok.Adapter):
    """Adapts content"""
    grok.provides(ILayout)
    grok.context(IDexterityContent)

    def __init__(self, context):
        self.context = context
    
    @getproperty
    def content(self):
        if hasattr(self.context, "content"):
            return self.context.content
        else:
            return ILayout["content"].default

    @setproperty
    def content(self, value):
        self.context.content = value


class Layout(grok.View):
    """Renders layout"""
    grok.context(IHasLayout)
    grok.require("zope2.View")


class View(grok.View):
    """Renders view"""
    grok.context(IHasLayout)
    grok.require("zope2.View")

    def render(self):
        return ILayout(self.context).content


class IPosition(form.Schema):
    """Text Snippet Tile"""
    form.mode(target="hidden")
    target = schema.TextLine(
        title=_(u"textsnippet_target_label",
                default="Target element"),
        required=False
        )
    form.mode(position="hidden")
    position = schema.Int(
        title=_(u"textsnippet_target_label",
                default="Target element"),
        required=False
        )
alsoProvides(IPosition, form.IFormFieldProvider)


from plone.tiles.interfaces import ITile

from plone.behavior.factory import BehaviorAdapterFactory
from zope.component import getUtility, provideAdapter

from plone.behavior.interfaces import IBehaviorAssignable

class TestingBehaviorAssignable(grok.Adapter):
    grok.provides(IBehaviorAssignable)
    grok.context(ITile)

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        import pdb; pdb.set_trace()

    def enumerateBehaviors(self):
        import pdb; pdb.set_trace()


#  <plone:behavior
#     title="Position"
#     description="Adds layout support to your tile"
#     provides=".layout.IPosition"
#     for="plone.tiles.interfaces.ITile"
#     />

#from plone.behavior.registration import BehaviorRegistration
#BehaviorRegistration(
#    title=u"Position", 
#    description=u"Adds layout support to tiles",
#    interface=IPosition,
#    for_=ITile)

#provideAdapter(
#    factory=BehaviorAdapterFactory(
#        getUtility(IPosition.__identifier__)),
#    adapts=(ITile,), provides=IPosition)


from zope.lifecycleevent import ObjectAddedEvent

@grok.subscribe(ITile, ObjectAddedEvent)
def createSubscriptions(tile, event):
    context = event.newParent
    data = StringIO(ILayout(context).content)
    root = etree.parse(data)
    namespaces = {"html": "http://www.w3.org/1999/xhtml"}
    head = root.xpath("html:head", namespaces=namespaces)
    columns = root.xpath("//html:div[contains(concat(' ', \
normalize-space(@class), ' '), ' cell ')]", namespaces=namespaces)
    import pdb; pdb.set_trace()
#    if event.action == "activate":
#        event.object.expiration_date = DateTime() + event.object.period

#from zope.event import notify

#notify(ObjectCreatedEvent(tile))
#notify(ObjectAddedEvent(tile, self.context, self.tileId))
#notify(ObjectModifiedEvent(tile))
#notify(ObjectRemovedEvent(tile, self.context, self.tileId))
