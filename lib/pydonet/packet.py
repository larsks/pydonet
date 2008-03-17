#!/usr/bin/python

import construct
from pydonet.message import Message
from pydonet.formats import *
from StringIO import StringIO

packetChecks = (
    ( fsc0048.PacketHeader, fsc0048.PacketHeader, lambda x: x.capWordA == 1 and x.capWordA == x.capWordB ),
    ( fsc0048.PacketHeader, fsc0039.PacketHeader, lambda x: x.capWordA == 1 ),
    ( fsc0048.PacketHeader, fts0001.PacketHeader, lambda x: x.capWordA == 0 ),
    )

def PacketFactory(src):
  pos = src.tell()
  for check in packetChecks:
    src.seek(pos)
    m = check[0].parse_stream(src)
    src.seek(pos)
    if check[2](m):
      return check[1].parse_stream(src)

  raise ValueError('Unable to recognize this packet.')

class Packet (object):

  def __init__ (self, file = None, data = None, fd = None):
    if file is not None:
      fd = open(file)
    elif fd is not None:
      fd = fd
    elif data is not None:
      fd = StringIO(data)

    self.fd = fd
    self.header = PacketFactory(fd)

  def next(self):
    try:
      m = Message(fd = self.fd)
      return m
    except ValueError:
      raise StopIteration

  def __iter__ (self):
    return self

def main():
  import sys
  for p in sys.argv[1:]:
    P = Packet(file = p)
    print P.header
    c = 0
    for m in P:
      print m
      c += 1
    print
    print '-' * 60
    print 'Found', c, 'messages.'
    print '-' * 60

if __name__ == '__main__': main()

