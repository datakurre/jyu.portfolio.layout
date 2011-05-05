# -*- coding: utf-8 -*-
"""Adds layout support to your content type"""

import os.path

from rwproperty import getproperty, setproperty

from lxml import etree

from Acquisition import aq_base

from five import grok

from zope import schema
from zope.component import getUtility, getAllUtilitiesRegisteredFor
from zope.security import checkPermission

from zope.interface import Interface
# from zope.interfaces import alsoProvides
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest

from plone.memoize import view
from plone.directives import form
x
from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from zope.app.publisher.interfaces.browser import IBrowserMenu

from plone.tiles.interfaces import ITileType

from plone.app.layout.globals.interfaces import IViewView
from plone.app.contentmenu.interfaces import IContentMenuItem

from plone.dexterity.interfaces import IDexterityContent

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("jyu.portfolio.layout")

DEFAULT_LAYOUT = open(
    os.path.join(
        os.path.dirname(__file__),
        'default-layout.html'
        )
    ).read().decode('utf-8')


class IHasLayout(Interface):
    """Marker interface for an object with a layout"""


def checkValidXHTML(value):
    """Try to given parse value."""
    try:
        if len(etree.fromstring(value)):
            return True
    except:
        pass
    return False


class ILayout(form.Schema):
    """Behavior interface to make a type support layout."""
    content = schema.Text(
        title=_(u"layout_content_label",
                default=u"Content"),
        description=_(u"layout_content_description",
                      u"Describes content and layout of the object in XHTML."),
        constraint=checkValidXHTML,
        required=True,
        default=DEFAULT_LAYOUT,
        )
### NOTE: Content field is hidden to prevent accidental edits.
# alsoProvides(ILayout, form.IFormFieldProvider)

 
class LayoutAdapter(grok.Adapter):
    """Adapts dexterity content for layout"""
    grok.provides(ILayout)
    grok.context(IDexterityContent)

    def __init__(self, context):
        self.context = context

    @getproperty
    def content(self):
        base = aq_base(self.context)
        if hasattr(base, "content"):
            return base.content
        else:
            return ILayout["content"].default

    @setproperty
    def content(self, value):
        base = aq_base(self.context)
        base.content = value


class Layout(grok.View):
    """Renders layout"""
    grok.context(IHasLayout)
    grok.implements(IViewView)
    grok.require("zope2.View")


class View(grok.View):
    """Renders view"""
    grok.context(IHasLayout)
    grok.require("zope2.View")

    def render(self):
        return ILayout(self.context).content


class TilesSubMenuItem(grok.MultiAdapter, BrowserSubMenuItem):
    grok.name("remind.contentmenu.tiles")
    grok.provides(IContentMenuItem)
    grok.adapts(IHasLayout, IBrowserRequest)

    submenuId = 'remind_contentmenu_tiles'
    order = 35

    title = _(u'layout_add_new_label', default=u'Place new\u2026')
    description = _(u'layout_add_new_help',
                    default=u'Add new tile onto this page')

    @property
    def extra(self):
        return {'id': 'remind-contentmenu-tiles'}

    @property
    def action(self):
        return '%s/@@add-tile' % self.context.absolute_url()

    @view.memoize
    def available(self):
        types = []
        for type_ in getAllUtilitiesRegisteredFor(ITileType):
            if checkPermission(type_.add_permission, self.context):
                try:
                    if self.request.traverseName(
                        self.context, "@@" + type_.__name__):
                        types.append(type_)
                except NotFound:
                    continue
        return len(types) > 0

    def selected(self):
        return False


class TilesMenu(grok.GlobalUtility, BrowserMenu):
    grok.name("remind_contentmenu_tiles")
    grok.provides(IBrowserMenu)

    def __init__(self):
        super(TilesMenu, self).__init__(self)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""

        types = []
        for type_ in getAllUtilitiesRegisteredFor(ITileType):
            if checkPermission(type_.add_permission, context):
                try:
                    if request.traverseName(
                        context, "@@" + type_.__name__):
                        types.append(type_)
                except NotFound:
                    continue
        types.sort(lambda x, y: cmp(x.title, y.title))

        normalizer = getUtility(IIDNormalizer)
        return [{
                'title': type_.title,
                'description': type_.description,
                'action': "%s/@@add-tile?form.button.Create=1&type=%s"\
                    % (context.absolute_url(), type_.__name__),
                'selected': False,
                'icon': None,
                'extra': {
                    'id': "add-%s" % normalizer.normalize(type_.__name__),
                    'separator': None, 'class': ''
                    },
                'submenu': None,
                } for type_ in types]
