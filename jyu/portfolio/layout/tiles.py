# -*- coding: utf-8 -*-
"""Adds layout support to your content type"""
from StringIO import StringIO

from lxml import etree
from five import grok

from zope import schema
from zope.interface import alsoProvides

from zope.lifecycleevent import ObjectAddedEvent

from plone.directives import form
from plone.tiles.interfaces import ITile

from jyu.portfolio.layout.behavior import ILayout

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.portfolio.layout")


class IPositioned(form.Schema):
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
alsoProvides(IPositioned, form.IFormFieldProvider)


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
