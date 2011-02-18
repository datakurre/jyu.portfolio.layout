# -*- coding: utf-8 -*-
"""Enhances original AddFOrm to redirect after creation back to the context"""

from z3c.form import button

from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
from zope.event import notify

from zope.traversing.browser.absoluteurl import absoluteURL

from Products.statusmessages.interfaces import IStatusMessage

from plone.tiles.interfaces import ITileDataManager

from plone.app.tiles import MessageFactory as _

from plone.app.tiles.browser.add  import DefaultAddForm
from plone.app.tiles.browser.add  import DefaultAddView


class ReturningAddForm(DefaultAddForm):
    """Standard tile add form, which is wrapped by DefaultAddView (see below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    buttons = DefaultAddForm.buttons.select('save', 'cancel')
    handlers = DefaultAddForm.handlers.copy()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        typeName = self.tileType.__name__

        # Traverse to a new tile in the context, with no data
        tile = self.context.restrictedTraverse(
            '@@%s/%s' % (typeName, self.tileId,))

        dataManager = ITileDataManager(tile)
        dataManager.set(data)

        # Look up the URL - we need to do this after we've set the data to
        # correctly account for transient tiles
        tileURL = absoluteURL(tile, self.request)
        contextURL = absoluteURL(tile.context, self.request)

        notify(ObjectCreatedEvent(tile))
        notify(ObjectAddedEvent(tile, self.context, self.tileId))

        IStatusMessage(self.request).addStatusMessage(
                _(u"Tile created at ${url}",
                  mapping={'url': tileURL}),
                type=u'info',
            )

        self.request.response.redirect(contextURL)


class ReturningAddView(DefaultAddView):
    """This is the default add view as looked up by the @@add-tile traversal
    view. It is an unnamed adapter on  (context, request, tileType).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = ReturningAddForm
