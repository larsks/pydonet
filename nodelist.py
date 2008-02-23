#!/usr/bin/python

import os, sys, re, fileinput

NORMAL_FLAGS = (
	'keyword',
	'node',
	'name',
	'location',
	'sysop',
	'phone',
	'speed'
)

class Node (dict):

  def __init__(self, *args, **kwargs):
    super(Node, self).__init__(*args)
    self.parent = kwargs.get('parent')

  def address (self):
    return '%(zone)s:%(net)s/%(node)s' % self
  def __str__ (self):
    return self.address()

def subst_spaces(s):
  return s.replace('_', ' ')

class Nodelist (object):

  def __init__ (self, src):
    self.cur_zone = 0
    self.cur_net = 0

    # Raw list of nodes.
    self.nodelist = []

    # Indexes.
    self.nodes    = {}
    self.nets     = {}
    self.zones    = {}

    if hasattr(src, 'read'):
      self.parse(src)
    else:
      self.parse(open(src))

  def parse(self, src):

    for line in src:
      if not line.strip():
        continue

      if line.startswith(';'):
        continue
      
      parts = line.strip().split(',')
      if len(parts) < 8:
        continue

      node = Node(zip(NORMAL_FLAGS, parts[:8]), parent=self)
      
      for flag in parts[7:]:
        data = True
        if ':' in flag:
          flag, data = flag.split(':',1)

        node[flag] = data

      if node['keyword'].lower() == 'zone':
        self.cur_zone = node['node']
        self.cur_net = 1
      elif node['keyword'].lower() == 'region':
        self.cur_net = node['node']
        node['node'] = 0
      elif node['keyword'].lower() == 'host':
        self.cur_net = node['node']
        node['node'] = 0

      node['zone'] = self.cur_zone
      node['net'] = self.cur_net

      self.nodelist.append(node)

      self.nodes['%(zone)s:%(net)s/%(node)s' % node] = [node]

      self.nets['%(zone)s:%(net)s' % node] \
          = self.nets.get('%(zone)s:%(net)s' % node, [])
      self.nets['%(zone)s:%(net)s' % node].append(node)

      self.zones[node['zone']] \
          = self.zones.get(node['zone'], [])
      self.zones[node['zone']].append(node)

  def node(self, k=None):
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
          % (node.address(), node['name'], ' '.join([k for k in node.keys() if k.isupper()]))
  else:
    import pprint
    pprint.pprint(nl.node(sys.argv[2]))

