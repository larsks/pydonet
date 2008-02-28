#!/usr/bin/python

import os, sys
import optparse
import pkt

def parse_args():
  parser = optparse.OptionParser()
  parser.add_option('-n', '--normal',
      action = 'store_const',
      const = 'f',
      dest = 'mode')
  parser.add_option('-i', '--immediate',
      action = 'store_const',
      const = 'i',
      dest = 'mode')
  parser.add_option('-c', '--crash',
      action = 'store_const',
      const = 'c',
      dest = 'mode')
  parser.add_option('-d', '--dir')
  parser.set_defaults(mode = 'f')
  parser.set_defaults(dir = '/var/spool/ftn/outb')

  return parser.parse_args()

def main():
  opts, args = parse_args()

  dest = {}
  
  for f in os.listdir(opts.dir):
    if not f.endswith('.pkt') and not f.endswith('.PKT'):
      continue
    p = pkt.Packet(os.path.join(opts.dir, f))
    fbase = '%(destNet)04x%(destNode)04x' % p
    
    if dest.get(fbase):
      dest[fbase]['packets'].append((p,f))
    else:
      dest[fbase] = {
        'node': '%(destZone)s:%(destNet)s/%(destNode)s' % p,
        'fbase': fbase,
        'packets': [(p,f)]
          }

  for d, data in dest.items():
    print 'DEST:', data['node'], '[', data['fbase'], ']'
    fd = open(os.path.join(opts.dir, '%s.%slo' % (data['fbase'], opts.mode)), 'w')
    for p,f in data['packets']:
      print '  ->', f
      print >>fd, os.path.join(opts.dir, f)
    fd.close()

if __name__ == '__main__': main()

