#!/usr/bin/python

'''Parses a standard FST-5000 Fidonet list.

For example:

  import nodelist
  nodes = nodelist.Nodelist('nodelist.053')

  if nodes.node('1:322/761').get('IBN'):
    print 'Accepts binkp connections.'

  for node in nodes.node():
    print node.address(), node['name']
'''

import os, sys, re, fileinput
from pydonet.address import Address

# These are the seven standard fields, described in
# FTS 5000.002 (http://www.ftsc.org/docs/fts-5000.002).
# This is a list of (x,y) tuples, where x is the field
# name and y is a transformation to apply to it.
REQUIRED_FIELDS = (
    ('keyword',   lambda x: x.lower()),
    ('node',      None),
    ('name',      lambda x: x.replace('_', ' ')),
    ('location',  lambda x: x.replace('_', ' ')),
    ('sysop',     lambda x: x.replace('_', ' ')),
    ('phone',     None),
    ('speed',     None),
    )

DEFAULT = Address('0:0/0')

class AttrDict (dict):
  def __getattr__ (self, k):
    try:
      return self[k]
    except KeyError, detail:
      raise AttributeError(detail)

  def __setattr__ (self, k, v):
    self[k] = v

class ShortLineError(Exception):
  pass

class Node (AttrDict):
  def __init__ (self, entry, ctx):
    self.entry = entry
    self.parseEntry(entry, ctx)

  def parseEntry(self, entry, ctx):
    fields = entry.strip().split(',')

    if len(fields) < len(REQUIRED_FIELDS):
      raise ShortLineError

    for x in REQUIRED_FIELDS:
      self[x[0]] = x[1] is None and fields.pop(0) or x[1](fields.pop(0))

    for x in fields:
      try:
        k,v = x.split(':', 1)
      except ValueError:
        k = x
        v = True

      self[k] = v

    if self.keyword == 'zone':
      self.address = Address('%s:1/1' % self.node)
      ctx.route = self.address
      self.route = DEFAULT
    elif self.keyword == 'region':
      self.address = Address('%s:%s/1' % (ctx.address.z, self.node))
      ctx.route = self.address
      self.route = DEFAULT
    elif self.keyword == 'host':
      self.address = Address('%s:%s/1' % (ctx.address.z, self.node))
      ctx.route = self.address
      self.route = DEFAULT
    elif self.keyword == 'hub':
      self.address = Address('%s:%s/%s'
          % (ctx.address.z, ctx.address.n, self.node))
      ctx.route = self.address
      self.route = DEFAULT
    else:
      self.address = Address(addr = ctx.address)
      self.address.f = self.node
      self.route = ctx.route

    ctx.address = Address(addr = self.address)

class Nodelist (object):
  def __init__ (self, nlpath = None):
    self.nodes = []
    self.index = {
        'zone': {},
        'net':  {},
        'node': {},
    }

    if nlpath is not None:
      self.parseFile(nlpath)

  def parseFile(self, nlpath):
    fd = open(nlpath)
    ctx = AttrDict()
    lc = 0
    for line in fd:
      lc += 1
      if line.startswith(';'):
        continue
      try:
        n = Node(line.strip(), ctx)
      except ShortLineError:
        continue

      self.nodes.append(n)
      self.index['node']['%s' % n.address] = n

      try:
        self.index['zone'][n.address.z].append(n)
      except KeyError:
        self.index['zone'][n.address.z] = [n]

      net = '%s:%s' % (n.address.z, n.address.n)

      try:
        self.index['net'][net].append(n)
      except KeyError:
        self.index['net'][net] = [n]

def main():
  N = Nodelist(nlpath = sys.argv[1])

  for addr in sys.argv[2:]:
    print N.index['node'][addr]

if __name__ == '__main__': main()

