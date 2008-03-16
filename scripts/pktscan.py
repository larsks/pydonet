#!/usr/bin/python

import os, sys, pprint
from pydonet import packet
from pydonet import message

for x in sys.argv[1:]:
  p = packet.PacketFactory(open(x).read())
  print p

  for m in p.messages:
    print m
    m = message.Message(m)
    print ' ', m
    pprint.pprint( m.kludge )

