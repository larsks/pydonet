#!/usr/bin/python

from distutils.core import setup

setup(name = "pydonet",
  version = "1",
  description = "FTN tools for Python",
  author = "Lars Kellogg-Stedman",
  author_email = "lars@oddbit.com",
  url = "http://code.google.com/p/pydonet/",
  packages = [
    'pydonet',
    'pydonet.formats',
    'pydonet.utils',
    'pydonet.construct',
    'pydonet.construct.lib',
    'pydonet.construct.formats',
    'pydonet.construct.protocols',
    'ftnfilter',
  ],
  package_dir = { '': 'lib'},
  scripts = [
    'scripts/ftnfilter',
    'scripts/ftnscanpkt',
    'scripts/ftnscanmsg',
    'scripts/ftnunpack',
    'scripts/ftnchecknodes',
    'scripts/ftntextnodes',
  ]
)

