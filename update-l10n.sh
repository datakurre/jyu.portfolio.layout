#!/bin/bash
i18ndude rebuild-pot --pot jyu/portfolio/layout/locales/jyu.portfolio.layout.pot --create jyu.portfolio.layout jyu/portfolio/layout

i18ndude sync --pot jyu/portfolio/layout/locales/jyu.portfolio.layout.pot jyu/portfolio/layout/locales/*/LC_MESSAGES/jyu.portfolio.layout.po