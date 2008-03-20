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
    'ftnfilter',
    'construct',
    'construct.lib',
    'construct.formats',
    'construct.protocols',
  ],
  package_dir = { '': 'lib'},
  scripts = [
    'scripts/ftnfilter',
    'scripts/ftnscanpkt',
    'scripts/ftnscanmsg',
    'scripts/ftnunpack',
  ]
)

