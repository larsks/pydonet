#!/usr/bin/python

import construct.core
from pydonet.formats import *
from pydonet.address import Address
from StringIO import StringIO

def MessageFactory(src):
  pos = src.tell()
  for fmt in [ fts0001.PackedMessageHeader, fts0001.DiskMessageHeader ]:
    try:
      src.seek(pos)
      m = fmt.parse_stream(src)
    except construct.core.ConstructError:
      continue

    return (fmt, m)

  raise ValueError('Not a FTS-0001 message.')

class Message (object):

  def __init__ (self, file = None, data = None, fd = None):
    if file is not None:
      fd = open(file)
    elif fd is not None:
      fd = fd
    elif data is not None:
      fd = StringIO(data)

    self.fd = fd
    self.message_class, self.header = MessageFactory(fd)
    self.body =  fts0001.MessageBody.parse_stream(fd)

  def getOrigAddr(self):
    return Address(n = self.header.origNet, f = self.header.origNode)

  def setOrigAddr(self, addr):
    self.header.origNet = addr.n
    self.header.origNode = addr.f

  origAddr = property(getOrigAddr, setOrigAddr, None, 'Get/set origination address.')

  def getDestAddr(self):
    return Address(n = self.header.origNet, f = self.header.origNode)

  def setDestAddr(self, addr):
    self.header.destNet = addr.n
    self.header.destNode = addr.f

  destAddr = property(getDestAddr, setDestAddr, None, 'Get/set destination address.')

  def __str__ (self):
    return '\n'.join([
        ' '.join([ str(self.origAddr), '->', str(self.destAddr), self.header.dateTime]),
        ' '.join(['     From:', self.header.fromUsername]),
        ' '.join(['       To:', self.header.toUsername]),
        ' '.join(['  Subject:', self.header.subject]),
        ' '.join(['    Flags:', ' '.join([x[0] for x in self.header.flags if x[1]])]),
    ])

  def serialize(self):
    return self.message_class.build(self.header) \
        + fts0001.MessageBody.build(self.body)

def main(verbose = False):
  import sys
  for m in sys.argv[1:]:
    M = Message(file = m)
    print M.origAddr, '->', M.destAddr, M.header.dateTime
    print '     From:', M.header.fromUsername
    print '       To:', M.header.toUsername
    print '  Subject:', M.header.subject
    print '    Flags:', ' '.join([x[0] for x in M.header.flags if x[1]])
    print
    if (verbose):
      print M.header

if __name__ == '__main__': main()

