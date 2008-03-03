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

# These are the seven standard fields, described in
# FTS 5000.002 (http://www.ftsc.org/docs/fts-5000.002).
REQUIRED_FIELDS = (
    ('keyword',   lambda x: x.lower()),
    ('node',      None),
    ('name',      None),
    ('location',  None),
    ('sysop',     None),
    ('phone',     None),
    ('speed',     None),
    )

class Node (dict):

  def __init__(self, *args, **kwargs):
    super(Node, self).__init__(*args)
    self.parent = kwargs.get('parent')

  def address (self):
    return '%(zone)s:%(net)s/%(node)s' % self
  def __str__ (self):
    return self.address()

Default = Node({
    'zone': '0',
    'net': '0',
    'node': '0',
  })

def subst_spaces(s):
  return s.replace('_', ' ')

class Nodelist (object):

  def __init__ (self, src):
    # Raw list of nodes.
    self.nodelist = []

    # Indexes.
    self.nodes    = {}
    self.nets     = {}
    self.zones    = {}

    if hasattr(src, 'read'):
      # If it has a 'read' method, assume it's a file.
      self.parse(src)
    else:
      # Otherwise assume it's a filename and try to open it.
      self.parse(open(src))

  def parse(self, src):
    cur_zone = 0
    cur_net = 0
    cur_route = Default

    lineno = 0
    for line in src:
      lineno += 1

      # Skip blank lines...
      if not line.strip():
        continue

      # ...and comments.
      if line.startswith(';'):
        continue
      
      parts = line.strip().split(',')
      if len(parts) < 7:
        print >>sys.stderr, '%d: BOGUS:' % lineno, line.strip()
        continue

      # Transform the seven required fields into a Python
      # dictionary.
      node = Node(zip([x[0] for x in REQUIRED_FIELDS], parts[:8]), parent=self)
      for fieldName, transform in REQUIRED_FIELDS:
        if transform is not None:
          node[fieldName] = transform(node[fieldName])

      # Now extract the flags into the dictionary.
      node.flags = {'private' : False}
      for flag in parts[7:]:
        data = True
        if ':' in flag:
          flag, data = flag.split(':',1)

        node.flags[flag] = data

      if node['keyword'] == 'zone':
        cur_zone = node['node']
        cur_route = Default
        cur_net = 1
      elif node['keyword'] == 'region':
        cur_net = node['node']
        cur_route = Default
        node['node'] = 0
      elif node['keyword'] == 'host':
        cur_net = node['node']
        cur_route = node
        node['node'] = 0
      elif node['keyword'] == 'hub':
        cur_route = node
      elif node['keyword'] == 'pvt':
        node.flags['private'] = True

      node['zone'] = cur_zone
      node['net'] = cur_net
      node['route'] = cur_route

      # Add to sequential list of nodes.
      self.nodelist.append(node)

      # Add to node index.
      self.nodes['%(zone)s:%(net)s/%(node)s' % node] = node

  def node(self, k=None):
    '''If k is None, return all nodes.  Otherwise, return information
    on the requested node.'''

    if k is None:
      return self.nodelist
    else:
      return self.nodes[k]

if __name__ == '__main__':
  import pprint

  nl = Nodelist(sys.argv[1])

  if len(sys.argv) == 2:
    for node in nl.node():
      print '%15s %20s %s' \
          % (node.address(), node['name'], ' '.join(node.flags.keys()))
  else:
    import pprint
    x = nl.node(sys.argv[2])
    print 'Route mail for %s to %s.' % (x.address(), x['route'].address())


