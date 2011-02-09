# -*- coding: utf-8 -*-
"""Adds layout support to your content type"""
from StringIO import StringIO

import re
from types import IntType

from lxml import etree
from five import grok

from zope import schema
from zope.interface import alsoProvides
from zope.security import checkPermission

from zope.annotation.interfaces import IAnnotatable

from zope.lifecycleevent import\
    ObjectAddedEvent, ObjectRemovedEvent

from plone.directives import form, tiles
from plone.tiles.interfaces import ITile

from jyu.portfolio.layout.behaviors import IHasLayout, ILayout

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.portfolio.layout")

NAMESPACES = {"html": "http://www.w3.org/1999/xhtml"}


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
        title=_(u"textsnippet_position_label",
                default="Target position"),
        required=False
        )
alsoProvides(IPositioned, form.IFormFieldProvider)


class AddTile(tiles.Tile):
    tiles.name('jyu.portfolio.layout.tiles.add')
    tiles.title(_(u"Add Tile"))
    # tiles.description()

    tiles.context(IHasLayout)
    tiles.require('zope2.View')
    # tile.layer()
    # tiles.schema()
    tiles.add_permission('cmf.ManagePortal')

    def update(self):
        data = StringIO(ILayout(self.context).content)
        root = etree.parse(data)
        tile = root.xpath("//*[@id='%s']" % self.id)[0]
        self.target = tile.getprevious().get("id")

    @property
    def visible(self):
        # You'd think you could use
        # tiles.require('cmf.ModifyPortalContent'), but it doesn't
        # really work, insufficient permissions doen't hide tile, but
        # renders "You are not authorized to..." :/
        return checkPermission('cmf.ModifyPortalContent', self.context)


@grok.subscribe(ITile, ObjectAddedEvent)
def addTile(tile, event):
    context = tile.context
    data = StringIO(ILayout(context).content)
    root = etree.parse(data)
    head = root.xpath("html:head", namespaces=NAMESPACES)[0]
    columns = root.xpath(
        ("//html:div[contains(concat(' ', normalize-space(@class), ' '), "
         "' sortable ')]"), namespaces=NAMESPACES)

    if tile.data.get("target", None):
        candidates = root.xpath("//*[@id='%s']" % tile.data["target"])
        if candidates:
            target = candidates[0]
        else:
            target = columns[0]
    else:
        target = columns[0]
    tile.data["target"] = target.get("id")

    link = etree.Element("link")
    link.set("rel", "tile")
    link.set("target", tile.id)
    link.set("href", "%s/%s" % (tile.__name__, tile.id))

    head.append(link)

    div = etree.Element("div")
    div.set("id", tile.id)

    position = tile.data.get("position", None)
    if type(position) == IntType\
            and position >= 0 and position < len(target):
        target.insert(position, div)
        tile.data["position"] = position
    else:
        target.append(div)
        tile.data["position"] = len(target)

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
        view = None
        if self.tile_id and self.target_id:
            data = StringIO(ILayout(self.context).content)
            root = etree.parse(data)

            for tile in root.xpath("//*[@id='%s']" % self.tile_id):
                for target in root.xpath("//*[@id='%s']" % self.target_id):

                    url = root.xpath("//html:link[@target='%s']"\
                        % self.tile_id, namespaces=NAMESPACES)[0].get("href")
                    url = re.compile("^\.?\/?@{0,2}(.*)").findall(url)[0]
                    view = self.context.restrictedTraverse(url)

                    view.data["target"] = self.target_id
                    view.data["position"] = self.position

                    tile.getparent().remove(tile)
                    if self.position < len(target):
                        target.insert(self.position, tile)
                        view.data["position"] = self.position
                    else:
                        target.append(tile)
                        view.data["position"] = len(target)
                    view.data["target"] = self.target_id
                    ILayout(self.context).content = etree.tostring(root)
                    break
                break

        if self.request.get("HTTP_X_REQUESTED_WITH", None) == "XMLHttpRequest":
            return view and view() or u""
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
