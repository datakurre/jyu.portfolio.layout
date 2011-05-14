# -*- coding: utf-8 -*-
"""Enhances the original EditForm to redirect users back to the origin
context after tile is edited
"""

from types import DictType

from z3c.form import button

from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from zope.traversing.browser.absoluteurl import absoluteURL

from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFCore.utils import getToolByName

from plone.tiles.interfaces import ITileDataManager

from plone.app.tiles import MessageFactory as _

from plone.app.tiles.browser.edit import DefaultEditForm
from plone.app.tiles.browser.edit import DefaultEditView


from zope import globalrequest

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from AccessControl.User import UnrestrictedUser

from plone.z3cform.interfaces import IDeferSecurityCheck


def deferSecurityCheckDuringTraversal(func):
    """Decorator for switching to unrestricted user on traversal
    when IDeferSecurityCheck flag is attached to request."""
    def wrapper(self, *args, **kwargs):
        request = globalrequest.getRequest()
        if IDeferSecurityCheck.providedBy(request):
            old_security_manager = getSecurityManager()
            newSecurityManager(
                None, UnrestrictedUser('manager', '', ['Manager'], []))
            try:
                return func(self, *args, **kwargs)
            except:
                pass
            finally:
                # Note that finally is also called before return
                setSecurityManager(old_security_manager)
            return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper


class ReturningEditForm(DefaultEditForm):
    """Standard tile edit form, which is wrapped by DefaultEditView (see
    below).

    This form is capable of rendering the fields of any tile schema as defined
    by an ITileType utility.
    """

    buttons = DefaultEditForm.buttons.select('save', 'cancel')
    handlers = DefaultEditForm.handlers.copy()

    @deferSecurityCheckDuringTraversal
    def getContent(self):
        content = super(ReturningEditForm, self).getContent()
        if type(content) == DictType:
            content.update({
                    "portal_url": getToolByName(self.context, "portal_url"),
                    "portal_skins": self.context.restrictedTraverse("portal_skins"),
                    "wysiwyg_support": self.context.restrictedTraverse("wysiwyg_support")
                    })
        return content

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

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        typeName = self.tileType.__name__
        tile = self.context.restrictedTraverse('@@%s/%s' % (typeName, self.tileId,))
        contextURL = absoluteURL(tile.context, self.request)
        self.request.response.redirect(contextURL)


class ReturningEditView(DefaultEditView):
    """This is the default edit view as looked up by the @@edit-tile traveral
    view. It is an unnamed adapter on  (context, request, tileType).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = ReturningEditForm
