# -*- coding: utf-8 -*-
"""Dummy copy from plone.app.tiles.browser.edit.

Modifies redirect after saving to target the context instead of edit
view.
"""

from z3c.form import button

from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from zope.traversing.browser.absoluteurl import absoluteURL

from Products.statusmessages.interfaces import IStatusMessage

from plone.tiles.interfaces import ITileDataManager

from plone.app.tiles import MessageFactory as _

from plone.app.tiles.browser.edit import DefaultEditForm
from plone.app.tiles.browser.edit import DefaultEditView


class ReturningEditForm(DefaultEditForm):
    """Standard tile edit form, which is wrapped by DefaultEditView (see
    below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    buttons = DefaultEditForm.buttons.select('save', 'cancel')
    handlers = DefaultEditForm.handlers.copy()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        typeName = self.tileType.__name__

        # Traverse to a new tile in the context, with no data
        tile = self.context.restrictedTraverse('@@%s/%s' % (typeName, self.tileId,))

        dataManager = ITileDataManager(tile)
        dataManager.set(data)

        # Look up the URL - we need to do this after we've set the data to
        # correctly account for transient tiles
#       tileURL = absoluteURL(tile, self.request)
        contextURL = absoluteURL(tile.context, self.request)
#       tileRelativeURL = tileURL

#       if tileURL.startswith(contextURL):
#           tileRelativeURL = '.' + tileURL[len(contextURL):]

        notify(ObjectModifiedEvent(tile))

        # Get the tile URL, possibly with encoded data
        IStatusMessage(self.request).addStatusMessage(_(u"Tile saved",), type=u'info')

#       # Calculate the edit URL and append some data in a JSON structure,
#       # to help the UI know what to do.
#
#       url = getEditTileURL(tile, self.request)
#
#       tileDataJson = {}
#       tileDataJson['action'] = "save"
#       tileDataJson['mode'] = "edit"
#       tileDataJson['url'] = tileRelativeURL
#       tileDataJson['tile_type'] = typeName
#       tileDataJson['id'] = tile.id

#       url = appendJSONData(url, 'tiledata', tileDataJson)
        self.request.response.redirect(contextURL)


class ReturningEditView(DefaultEditView):
    """This is the default edit view as looked up by the @@edit-tile traveral
    view. It is an unnamed adapter on  (context, request, tileType).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = ReturningEditForm
