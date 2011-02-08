# -*- coding: utf-8 -*-
"""Dummy copy from plone.app.tiles.browser.traversal.

Adds support for hidden fields "target" and "position.
"""

from urllib import urlencode

from zope.component import getUtility
from zope.component import getAllUtilitiesRegisteredFor

from zope.security import checkPermission
from zope.publisher.interfaces import NotFound

from plone.uuid.interfaces import IUUIDGenerator

from plone.tiles.interfaces import ITileType

from plone.app.tiles import MessageFactory as _
from plone.app.tiles.browser.traversal import AddTile

from plone.memoize import view


class AddPositionedTile(AddTile):
    """Implements the @@add-tile traversal view

    Rendering this view on its own will display a template where the user
    may choose a tile type to add.

    Traversing to /path/to/obj/@@add-tile/tile-name/tile-id will:

        * Look up the tile info for 'tile-name' as a named utility
        * Attempt to find an adapter for (context, request, tile_info) with
            the name 'tile-name'
        * Fall back on the unnamed adapter of the same triple
        * Set the 'tileId' property on the view to the id 'tile-id
        * Return the view for rendering
    """

    @view.memoize
    def tileTypes(self):
        """Get a list of addable ITileType objects representing tiles         
        which are addable in the current context                              
        """
        types = []
    
        for type_ in getAllUtilitiesRegisteredFor(ITileType):
            if checkPermission(type_.add_permission, self.context):
                ### Here we've added test (traverseName) that the
                ### registered tile is really registerd for our
                ### context.
                try:
                    if self.request.traverseName(
                        self.context, "@@" + type_.__name__):
                        types.append(type_)
                except NotFound:
                    continue
                ###
        types.sort(self.tileSortKey)
        return types

    def __call__(self):
        self.errors = {}
        self.request['disable_border'] = True

        if 'form.button.Create' in self.request:
            newTileType = self.request.get('type', None)
            if newTileType is None:
                self.errors['type'] = _(u"You must select the type of " + \
                                        u"tile to create")

            generator = getUtility(IUUIDGenerator)
            newTileId = generator()

            if newTileId is None:
                self.errors['id'] = _(u"You must specify an id")

            if len(self.errors) == 0:
                ### Here we've added target and position attributes
                ### to allow tile to be inserted into requested div.
                target = self.request.get('target', None)
                position = self.request.get('position', '0')
                parameters = {}
                if target is not None:
                    parameters["target"] = target
                if position is not None:
                    parameters["position"] = position
                self.request.response.redirect("%s/@@add-tile/%s/%s?%s" % \
                        (self.context.absolute_url(), newTileType, newTileId,
                         urlencode(parameters)))
                ###
                return ''

        return self.index()
