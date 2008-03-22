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
import socket
from pydonet.address import Address
from pydonet.utils.attrdict import AttrDict

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

# Indicates that the host is a Host (routes for itself).
DIRECT = Address('0:0/0')

def ipForService(node, svc, checkDns = False):
  '''Given a Node, use commonly accepted heuristics to determine
  the ip address or hostname for a given Ixx service flag.  Returns
  a tuple (flag, host, port), where:
  
  - flag is the corresponding Ixx flag if the host offers that service,
    or None otherwise;

  - host is the hostname or ip address

  - port is the port if the node uses a nonstandard port for the service.
  '''

  flag = None
  host = None
  port = None

  if node.has_key(svc):
    flag = svc

    # (1) Is there a service-specific IP address or port?
    if node[svc] is not True:
      if ':' in node[svc]:
        host, port = node[svc].split(':')
      else:
        if node[svc].isdigit():
          port = node[svc]
        else:
          host = node[svc]

    if host is None:
      # (2) Is there an INA: flag?
      if node.get('INA', True) is not True:
        host = node['INA']
      elif node.get('IP', True) is not True:
        # (3) Is there an IP: flag?
        host = node['IP']
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
  
  return (flag, host, port)

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
      self.address = Address('%s:%s/%s'
          % (ctx.address.z, ctx.address.n, self.node))
      ctx.route = self.address
      self.route = DIRECT
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

