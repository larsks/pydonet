#!/usr/bin/python

import construct.core
from pydonet.formats import *
from StringIO import StringIO

def MessageFactory(src):
  pos = src.tell()
  for fmt in [
      fts0001.PackedMessageHeader,
      fts0001.DiskMessageHeader
      ]:
    try:
      src.seek(pos)
      m = fmt.parse_stream(src)
    except construct.core.ConstructError:
      continue

    return m

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
    self.header = MessageFactory(fd)
    self.body =  fts0001.MessageBody.parse_stream(fd)

  def getOrigAddr(self):
    return '%(origNet)s/%(origNode)s' % self.header

  def setOrigAddr(self, addr):
    net, node = addr.split('/')
    self.header.origNet = net
    self.header.origNode = node

  origAddr = property(getOrigAddr, setOrigAddr, None, 'Get/set origination address.')

  def getDestAddr(self):
    return '%(destNet)s/%(destNode)s' % self.header

  def setDestAddr(self, addr):
    net, node = addr.split('/')
    self.header.destNet = net
    self.header.destNode = node

  destAddr = property(getDestAddr, setDestAddr, None, 'Get/set destination address.')

  def __str__ (self):
    return '\n'.join([
        ' '.join([ self.origAddr, '->', self.destAddr, self.header.dateTime]),
        ' '.join(['     From:', self.header.fromUsername]),
        ' '.join(['       To:', self.header.toUsername]),
        ' '.join(['  Subject:', self.header.subject]),
        ' '.join(['    Flags:', ' '.join([x[0] for x in self.header.attr if x[1]])]),
    ])

def main():
  import sys
  for m in sys.argv[1:]:
    M = Message(file = m)
    print M.origAddr, '->', M.destAddr, M.header.dateTime
    print '     From:', M.header.fromUsername
    print '       To:', M.header.toUsername
    print '  Subject:', M.header.subject
    print '    Flags:', ' '.join([x[0] for x in M.header.attr if x[1]])
    print

if __name__ == '__main__': main()

