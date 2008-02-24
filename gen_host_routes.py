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
  
  for node in nl.node():
    if opts.zone and node['zone'] != opts.zone: continue
    nets['%(zone)s:%(net)s' % node] = True
    if node.flags.get('IBN'):
      print 'DIRECT %s' % node

  for net in nets.keys():
    try:
      host = nl.node('%s/0' % net)[0]
      if host.flags.get('IBN'):
        print 'ROUTE_TO %s/0 %s/ALL' % (net, net)
    except KeyError:
      pass

  if opts.default_route:
    print
    print 'ROUTE_TO %s ALL' % opts.default_route

  print

if __name__ == '__main__': main()

