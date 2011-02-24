# -*- coding: utf-8 -*-
"""Reminds of, but is not Deco, just a poor substitute"""

import re

from lxml import etree
from five import grok

from zope.component import getUtility

from zope.annotation.interfaces import IAnnotatable

from zope.lifecycleevent import ObjectAddedEvent,\
    ObjectModifiedEvent, ObjectRemovedEvent

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.tiles.interfaces import ITileType, ITile, IPersistentTile
from plone.tiles.data import encode

from jyu.portfolio.layout.behaviors import ILayout

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.portfolio.layout")

NAMESPACES = {"html": "http://www.w3.org/1999/xhtml"}


@grok.subscribe(ITile, ObjectAddedEvent)
def addTile(tile, event):
    schema = getUtility(ITileType, name=tile.__name__).schema

    data = ILayout(tile.context).content
    root = etree.fromstring(data)
    
    head = root.xpath("html:head", namespaces=NAMESPACES)[0]

    rows = root.xpath(
        ("//html:div[contains(concat(' ', normalize-space(@class), ' '), "
         "' row ')]"), namespaces=NAMESPACES)
    for row in rows:
        columns = row.xpath(
            ("html:div[contains(concat(' ', normalize-space(@class), ' '), "
             "' cell ')]"), namespaces=NAMESPACES)
        for column in reversed(columns):

            link = etree.Element("link")
            link.set("rel", "tile")
            link.set("target", tile.id)
            link.set("href", u"%s/%s" % (tile.__name__, tile.id))

            head.append(link)

            div = etree.Element("div")
            div.set("id", tile.id)

            classname = getUtility(IIDNormalizer).normalize(tile.__name__)
            div.set("class", "tile %s" % classname)

            column.insert(0, div)

            if not IPersistentTile.providedBy(tile):
                link.set("href", link.get("href")
                         + u"?" + encode(tile.data, schema))
            try:
                ILayout(tile.context).content =\
                    etree.tostring(root, pretty_print=True)
            except AttributeError:
                # layout is read only
                pass
            break
        break


class MoveTile(grok.View):
    """Implements @@move-tile traversal view
    """
    grok.name('move-tile')
    grok.context(IAnnotatable)
    grok.require('cmf.ModifyPortalContent')

    def update(self, tile=None, direction=None, target=None, position=0):
        self.tile_id = tile
        self.direction =\
            direction in [u"up", u"right", u"down", u"left"] and direction\
            or None
        self.target_id = target
        try:
            self.position = max(0, int(position))
        except ValueError:
            self.position = 0

    def render(self):
        if self.tile_id and self.direction:
            data = ILayout(self.context).content
            root = etree.fromstring(data)

            columns = root.xpath(
                ("//html:div[contains(concat(' ', normalize-space(@class), ' '), "
                 "' cell ')]"), namespaces=NAMESPACES)
            
            for tile in root.xpath("//*[@id='%s']" % self.tile_id):
                modified = False
                parent = tile.getparent()

                if self.direction == u"up":
                    start = parent.index(tile)
                    position = max(0, start - 1)
                    if position != start:
                        parent.remove(tile)
                        parent.insert(position, tile)
                        modified = True

                elif self.direction == u"down":
                    start = parent.index(tile)
                    position = min(len(parent) - 1, start + 1)
                    if position != start:
                        parent.remove(tile)
                        parent.insert(position, tile)
                        modified = True

                elif self.direction == u"right":
                    start = columns.index(parent)
                    position = min(len(columns) - 1, start + 1)
                    if position != start:
                        parent.remove(tile)
                        columns[position].insert(0, tile)
                        modified = True

                elif self.direction == u"left":
                    start = columns.index(parent)
                    position = max(0, start - 1)
                    if position != start:
                        parent.remove(tile)
                        columns[position].insert(0, tile)
                        modified = True

                try:
                    if modified:
                        ILayout(self.context).content =\
                            etree.tostring(root, pretty_print=True)
                except AttributeError:
                    # layout is read only
                    pass
                break

        elif self.tile_id and self.target_id:
            data = ILayout(self.context).content
            root = etree.fromstring(data)

            for tile in root.xpath("//*[@id='%s']" % self.tile_id):
                for target in root.xpath("//*[@id='%s']" % self.target_id):

                    url = root.xpath("//html:link[@target='%s']"\
                        % self.tile_id, namespaces=NAMESPACES)[0].get("href")
                    url = re.compile("^\.?\/?@{0,2}(.*)").findall(url)[0]

                    tile.getparent().remove(tile)
                    if self.position < len(target):
                        target.insert(self.position, tile)
                    else:
                        target.append(tile)
                    try:
                        ILayout(self.context).content =\
                            etree.tostring(root, pretty_print=True)
                    except AttributeError:
                        # layout is read only
                        pass
                    break
                break

        if self.request.get("HTTP_X_REQUESTED_WITH", None) == "XMLHttpRequest":
            return u""

        return self.request.response.redirect(self.context.absolute_url())


@grok.subscribe(ITile, ObjectModifiedEvent)
def modifyTile(tile, event):
    # updates transient tiles
    if not IPersistentTile.providedBy(tile):
        schema = getUtility(ITileType, name=tile.__name__).schema
        data = ILayout(tile.context).content
        root = etree.fromstring(data)

        link = root.xpath("//html:link[@target='%s']"\
            % tile.id, namespaces=NAMESPACES)
        href = u"%s/%s" % (tile.__name__, tile.id)\
            + u"?" + encode(tile.data, schema)

        if len(link) and link[0].get("href") != href:
            link[0].set("href", href)
            try:
                ILayout(tile.context).content =\
                    etree.tostring(root, pretty_print=True)
            except AttributeError:
                # layout is read only
                pass


@grok.subscribe(ITile, ObjectRemovedEvent)
def removeTile(tile, event):
    context = event.oldParent
    tile_id = event.oldName

    data = ILayout(context).content
    root = etree.fromstring(data)

    for removable in root.xpath("//*[@target='%s']" % tile_id):
        removable.getparent().remove(removable)

    for removable in root.xpath("//*[@id='%s']" % tile_id):
        removable.getparent().remove(removable)

    try:
        ILayout(context).content =\
            etree.tostring(root, pretty_print=True)
    except AttributeError:
        # layout is read only
        pass
