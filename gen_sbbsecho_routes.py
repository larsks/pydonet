#!/usr/bin/python

'''Generate routing information for use with sbbsecho + BinkD.'''

import os, sys, optparse
import nodelist

def parse_args():
  parser = optparse.OptionParser()
  parser.add_option('-z', '--zone')
  parser.add_option('-d', '--default-route')

  opts, args = parser.parse_args()
  return opts,args

def main ():

  opts, args = parse_args()
  nl = nodelist.Nodelist(args[0])
  nets = {}

  direct = []
  routed = []
  
  for node in nl.node():
    if opts.zone and node['zone'] != opts.zone: continue
    nets['%(zone)s:%(net)s' % node] = True

    if node.flags.get('IBN'):
      direct.append('DIRECT %s' % node.address())
    elif node['route'] is not nodelist.Default and node['route'] is not node:
      if node['route'].flags.get('IBN'):
        routed.append('ROUTE_TO %s %s' % (node['route'].address(), node.address()))

  for net in nets.keys():
    try:
      host = nl.node('%s/0' % net)
      if host.flags.get('IBN'):
        routed.append('ROUTE_TO %s %s/ALL' % (host.address(), net))
    except KeyError:
      pass

  print '\n'.join(direct)
  print
  print '\n'.join(routed)

  if opts.default_route:
    print
    print 'ROUTE_TO %s ALL' % opts.default_route

  print

if __name__ == '__main__': main()

