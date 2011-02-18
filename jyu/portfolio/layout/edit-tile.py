# -*- coding: utf-8 -*-
"""Enhances original AddFOrm to redirect after creation back to the context"""

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
        contextURL = absoluteURL(tile.context, self.request)

        notify(ObjectModifiedEvent(tile))

        # Get the tile URL, possibly with encoded data
        IStatusMessage(self.request).addStatusMessage(_(u"Tile saved",), type=u'info')

        self.request.response.redirect(contextURL)


class ReturningEditView(DefaultEditView):
    """This is the default edit view as looked up by the @@edit-tile traveral
    view. It is an unnamed adapter on  (context, request, tileType).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = ReturningEditForm
