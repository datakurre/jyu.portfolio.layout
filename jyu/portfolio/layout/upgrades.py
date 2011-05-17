# -*- coding: utf-8 -*-
"""Profile migration steps for jyu.portfolio.layout"""

from Products.CMFCore.utils import getToolByName


def upgrade1to2(self):
    setup_tool = getToolByName(self, "portal_setup")
    setup_tool.runAllImportStepsFromProfile(
        "profile-jyu.portfolio.layout:upgrade1to2")
    return "Upgraded jyu.portfolio.layout from 1 to 2."
