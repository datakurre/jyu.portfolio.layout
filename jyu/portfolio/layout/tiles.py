# -*- coding: utf-8 -*-
"""Adds layout support to your content type"""
from StringIO import StringIO

import re

from lxml import etree
from five import grok

from zope import schema
from zope.interface import alsoProvides

from zope.annotation.interfaces import IAnnotatable

from zope.lifecycleevent import\
    ObjectAddedEvent, ObjectRemovedEvent

from plone.directives import form, tiles
from plone.tiles.interfaces import ITile

from jyu.portfolio.layout.behaviors import IHasLayout, ILayout

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.portfolio.layout")

TILE_TYPE_REGEXP = re.compile(".*(@@[^/]+).*")


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


class Toolbox(tiles.Tile):
    tiles.name('jyu.portfolio.app.tiles.toolbox')
    tiles.title(_(u"Column Toolbox"))
    # tiles.description()

    tiles.context(IHasLayout)
    tiles.require('cmf.ModifyPortalContent')
    # tile.layer()
    # tiles.schema()
    tiles.add_permission('cmf.ManagePortal')

    def render(self):
        return '<a class="tile" \
href="@@add-tile?target=%s">\
Add</a>' % self.id


@grok.subscribe(ITile, ObjectAddedEvent)
def addTile(tile, event):
    context = tile.context
    data = StringIO(ILayout(context).content)
    root = etree.parse(data)
    namespaces = {"html": "http://www.w3.org/1999/xhtml"}
    head = root.xpath("html:head", namespaces=namespaces)[0]
    columns = root.xpath("//html:div[contains(concat(' ', \
normalize-space(@class), ' '), ' cell ')]", namespaces=namespaces)[0]

    if tile.data.get("target", None):
        candidates = root.xpath("//*[@id='%s']" % tile.data["target"])
        if candidates:
            target = candidates[0]
        else:
            target = columns[0]
    else:
        target = columns[0]

    assert TILE_TYPE_REGEXP.match(tile.url), "Tile type extraction failed."

    tile_type = TILE_TYPE_REGEXP.findall(tile.url)[0]
    link = etree.Element("link")
    link.set("rel", "tile")
    link.set("target", tile.id)
    link.set("href", "./%s/%s" % (tile_type, tile.id))

    head.append(link)

    div = etree.Element("div")
    div.set("id", tile.id)
    target.append(div)

    ILayout(context).content = etree.tostring(root)


class MoveTile(grok.View):
    """Implements @@move-tile traversal view
    """
    grok.name('move-tile')
    grok.context(IAnnotatable)
    grok.require('cmf.ModifyPortalContent')

    def update(self, tile=None, target=None, position=0):
        self.tile_id = tile
        self.target_id = target
        try:
            self.position = max(0, int(position))
        except ValueError:
            self.position = 0

    def render(self):
        if self.tile_id and self.target_id:
            data = StringIO(ILayout(self.context).content)
            root = etree.parse(data)

            for tile in root.xpath("//*[@id='%s']" % self.tile_id):
                for target in root.xpath("//*[@id='%s']" % self.target_id):
                    tile.getparent().remove(tile)
                    if self.position < len(target):
                        target.insert(self.position, tile)
                    else:
                        target.append(tile)
                    ILayout(self.context).content = etree.tostring(root)
                    break
                break
    
        if self.request.get("HTTP_X_REQUESTED_WITH", None) == "XMLHttpRequest":
            return u""
        return self.request.response.redirect(self.context.absolute_url())


@grok.subscribe(ITile, ObjectRemovedEvent)
def removeTile(tile, event):
    context = event.oldParent
    tile_id = event.oldName

    data = StringIO(ILayout(context).content)
    root = etree.parse(data)

    for removable in root.xpath("//*[@target='%s']" % tile_id):
        removable.getparent().remove(removable)

    for removable in root.xpath("//*[@id='%s']" % tile_id):
        removable.getparent().remove(removable)

    ILayout(context).content = etree.tostring(root)
