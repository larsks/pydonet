#!/usr/bin/python

import os, sys
from pydonet import packet
from pydonet import message

for x in sys.argv[1:]:
  p = packet.PacketFactory(open(x).read())
  print p

  for m in p.messages:
    m = message.Message(m)
    print ' ', m
    print m.kludge
    print m.body

