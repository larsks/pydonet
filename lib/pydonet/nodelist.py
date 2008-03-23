#!/usr/bin/python

'''Parses a standard FST-5000 Fidonet list.

For example:

  import nodelist
  nodes = nodelist.Nodelist('nodelist.053')

  if nodes.node('1:322/761').flags.get('IBN'):
    print 'Accepts binkp connections.'

  for node in nodes.node():
    print node.address(), node['name']
'''

import os, sys, re, fileinput
import socket
from pydonet.address import Address
from pydonet.utils.attrdict import AttrDict
from pydonet.utils.odict import OrderedDict

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

re_zeroes = re.compile(r'000(-0+)+$')
re_ipaddr = re.compile(r'\d+.\d+.\d+.\d+')
re_fqdn = re.compile(r'([a-z0-9][a-z0-9-]*)?[a-z0-9](\.([a-z0-9][a-z0-9-]*)?[a-z0-9])+\.?', re.IGNORECASE)

# Indicates that the node is a Host (routes for itself).
DIRECT = Address('0:0/0')

def ipForService(node, flag, val, checkDns = False):
  host = None
  port = None

  # (1) Is there a service-specific IP address or port?
  if val is not True:
    if ':' in val:
      host, port = val.split(':')
    else:
      if val.isdigit():
        port = val
      else:
        host = val

  if host is None:
    # (2) Is there an INA: flag?
    if node.getFlag('INA', True) is not True:
      host = node.getFlag('INA')
    elif node.getFlag('IP', True) is not True:
      # (3) Is there an IP: flag?
      host = node.getFlag('IP')
    elif node.phone.startswith('000-') and not re_zeroes.match(node.phone):
      # (4) Is the phone number really an IP address?
      host = node.phone.split('-', 1)[1].replace('-', '.')
    elif re_fqdn.match(node.name):
      # (5) Is field three (system name) really a hostname?  UGLY UGLY BAD
      host = node.name

  if host is None and checkDns:
    try:
      maybe = 'f%(f)s.n%(n)s.z%(z)s.fidonet.net' % node.address
      addr = socket.gethostbyname(maybe)
      host = maybe
    except socket.gaierror:
      pass

  return (host, port)

class NodeListError(Exception):
  def __init__(self, msg, path, line):
    self.msg = msg
    self.path = path
    self.line = line

class Node (AttrDict):
  def __init__ (self, entry, ctx):
    self.entry = entry
    self.flags = OrderedDict()
    self.parseEntry(entry, ctx)

  def parseEntry(self, entry, ctx):
    fields = entry.strip().split(',')

    if len(fields) < len(REQUIRED_FIELDS):
      raise NodeListError('Short line.', ctx.path, ctx.line)

    # Deal with required fields.
    for x in REQUIRED_FIELDS:
      self[x[0]] = x[1] is None and fields.pop(0) or x[1](fields.pop(0))

    # And now deal with optional flags.
    for x in fields:
      try:
        k,v = x.split(':', 1)
      except ValueError:
        k = x
        v = True

      try:
        self.flags[k].append(v)
      except KeyError:
        self.flags[k] = [v]

    if self.keyword == 'zone':
      self.address = Address('%s:1/1' % self.node)
      ctx.route = self.address
      self.route = DIRECT
    elif self.keyword == 'region':
      self.address = Address('%s:%s/0' % (ctx.address.z, self.node))
      ctx.route = self.address
      self.route = DIRECT
    elif self.keyword == 'host':
      self.address = Address('%s:%s/0' % (ctx.address.z, self.node))
      ctx.route = self.address
      self.route = DIRECT
    elif self.keyword == 'hub':
      self.address = Address(addr = ctx.address, f=self.node)
      ctx.route = self.address
      self.route = DIRECT
    else:
      self.address = Address(addr = ctx.address, f=self.node)
      self.route = ctx.route

    ctx.address = Address(addr = self.address)

  def getFlag(self, flag, default = None):
    if self.flags.has_key(flag):
      return self.flags[flag][0]
    else:
      return default

  def getEveryFlag(self, flag, default = []):
    return self.flags.get(flag, default)

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
    ctx = AttrDict(line = 0, path = nlpath)
    for line in fd:
      ctx.line += 1
      if line.startswith(';'):
        continue
      try:
        n = Node(line.strip(), ctx)
      except NodeListError, detail:
        print '! %s: line %s: %s' % (detail.path, detail.line, detail.msg)
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

