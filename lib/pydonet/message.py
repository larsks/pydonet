#!/usr/bin/python

import construct.core
from pydonet.formats import *
from pydonet.address import Address
from StringIO import StringIO

S_START   = 0
S_BODY    = 1
S_SEENBY  = 2

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

class Body (object):
  def __init__ (self, data):
    self.area = None
    self.origin = None
    self.klines = []
    self.seenby = []
    self.raw = data
    self.lines = self.raw.split('\r')

    self.parseLines()

  def addKludge(self, line):
    k,v = line.split(None, 1)
    self.klines.append([k[1:],v])

  def parseLines(self):

    state = S_START
    body = []

    i=0
    while i < len(self.lines):
      line = self.lines[i]

      if state == S_START:
        state = S_BODY

        if line.startswith('AREA:'):
          self.area = line.split(':')[1]
        else:
          continue
      elif state == S_BODY:
        if line.startswith('\x01'):
          self.addKludge(line)
        elif line.startswith(' * Origin:'):
          self.origin = line
          state = S_SEENBY
        else:
          body.append(line)
      elif state == S_SEENBY:
        if line.startswith('\x01'):
          self.addKludge(line)
        elif line.startswith('SEEN-BY:'):
          self.seenby.append(line)
        elif len(line) == 0:
          pass
        else:
          raise ValueError('Unexpected: %s'  % line)

      i += 1

    self.lines = body

  def __str__ (self):
    return '\n'.join(self.lines)

  def serialize(self):
    '''Rebuilds the message as:

      AREA:...
      Kludge lines
      Body
      Origin
      SEEN-BY'''

    lines = []

    if self.area:
      lines.append('AREA:%s' % self.area)

    for k,v in self.klines:
      lines.append('\x01%s %s' % (k,v))

    lines.extend(self.lines)

    if self.origin:
      lines.append(self.origin)

    lines.extend(self.seenby)

    return fts0001.MessageBody.build('\r'.join(lines))

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
    self.body =  Body(fts0001.MessageBody.parse_stream(fd))

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
    if self.body.area:
      area = ' [%s]' % self.body.area

    text = [
      '%s -> %s @ %s%s' % (self.origAddr, self.destAddr, self.dateTime, area),
      '     From: %s' % self.fromUsername,
      '       To: %s' % self.toUsername,
      '  Subject: %s' % self.subject,
      '    Flags: %s' % (' '.join([x[0] for x in self.flags if x[1]])),
    ]

    return '\n'.join(text)

  def serialize(self):
    return self.message_class.build(self.header) \
        + self.body.serialize()

  def __getattr__(self, name):
    return getattr(self.header, name)

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

