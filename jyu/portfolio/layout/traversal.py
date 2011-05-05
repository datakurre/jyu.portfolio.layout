# -*- coding: utf-8 -*-
"""Enhances the original AddTile by checking the availability of found
tiles on the current context
"""

from zope.component import getAllUtilitiesRegisteredFor

from zope.security import checkPermission
from zope.publisher.interfaces import NotFound

from plone.tiles.interfaces import ITileType

from plone.app.tiles.browser.traversal import AddTile

from plone.memoize import view


class AddAvailableTile(AddTile):
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
