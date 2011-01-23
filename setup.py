from setuptools import setup, find_packages

version = '1.0'

setup(name='jyu.portfolio.layout',
      version=version,
      description="JYU ePortfolio Layout Engine",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Asko Soukka',
      author_email='asko.soukka@iki.fi',
      url='https://webapps.jyu.fi/wiki/display/jyuplone/jyu.portfolio.layout',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jyu', 'jyu.portfolio'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        # -*- Grok: -*-
        'five.grok',
        # -*- Behaviors: -*- 
        'lxml',
        'rwproperty',
        'plone.tiles',
        'plone.behavior',
        'plone.directives.form',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
