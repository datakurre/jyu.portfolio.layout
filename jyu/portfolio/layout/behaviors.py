# -*- coding: utf-8 -*-
"""Adds layout support to your content type"""
import os.path

from rwproperty import getproperty, setproperty

from five import grok

from zope import schema
from zope.interface import Interface, alsoProvides

from plone.directives import form

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
    """Marker interface for an object with a layout
    """


class ILayout(form.Schema):
    """Behavior interface to make a type support layout.
    """
    form.fieldset('layout', label=_(u"Layout"), fields=['content'])
    content = schema.Text(
        title=_(u"layout_content_label",
                default=u"Content"),
        description=_(u"layout_content_description",
                          u"Layout and content of the object"),
        required=False,
        default=DEFAULT_LAYOUT,
        )
alsoProvides(ILayout, form.IFormFieldProvider)


class LayoutAdapter(grok.Adapter):
    """Adapts dexterity content for layout"""
    grok.provides(ILayout)
    grok.context(IDexterityContent)

    def __init__(self, context):
        self.context = context
    
    @getproperty
    def content(self):
        if hasattr(self.context, "content"):
            return self.context.content
        else:
            return ILayout["content"].default

    @setproperty
    def content(self, value):
        self.context.content = value


class Layout(grok.View):
    """Renders layout"""
    grok.context(IHasLayout)
    grok.require("zope2.View")


class View(grok.View):
    """Renders view"""
    grok.context(IHasLayout)
    grok.require("zope2.View")

    def render(self):
        return ILayout(self.context).content
