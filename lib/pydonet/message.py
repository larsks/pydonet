#!/usr/bin/python

from construct import *
from StringIO import StringIO

# http://www.ftsc.org/docs/fts-0001.016
PackedMessageHeader = Struct('message',
  Const(ULInt16('messageType'), 2),
  ULInt16('origNode'),
  ULInt16('destNode'),
  ULInt16('origNet'),
  ULInt16('destNet'),
  ULInt16('attr'),
  ULInt16('cost'),
  String('dateTime', 20, padchar='\x00'),
  CString('toUsername'),
  CString('fromUsername'),
  CString('subject'),
)

DiskMessageHeader = Struct('message',
  String('fromUsername', 36, padchar='\x00'),
  String('toUsername', 36, padchar='\x00'),
  String('subject', 72, padchar='\x00'),
  String('dateTime', 20, padchar='\x00'),
  ULInt16('timesRead'),
  ULInt16('destNode'),
  ULInt16('origNode'),
  ULInt16('cost'),
  ULInt16('destNet'),
  ULInt16('origNet'),
  ULInt16('destZone'),
  ULInt16('origZone'),
  ULInt16('destPoint'),
  ULInt16('origPoint'),
  ULInt16('replyTo'),
  FlagsEnum(ULInt16('attr'),
    PRIVATE   = 0x0001,
    CRASH     = 0x0002,
    RECEIVED  = 0x0004,
    SENT      = 0x0008,
    FATTACH   = 0x0010,
    INTRANSIT = 0x0020,
    ORPHAN    = 0x0040,
    KILLSENT  = 0x0080,
    LOCAL     = 0x0100,
    HOLD      = 0x0200,
    unused    = 0x0400,
    FREQ      = 0x0800,
    WANTRECEIPT   = 0x1000,
    ISRECEIPT = 0x2000,
    AUDIT     = 0x4000,
    FUPDATE   = 0x8000
  ),
  ULInt16('nextReply'),
)

def MessageReader (hdr):
  return Struct('message',
    Rename('header', hdr),
    CString('body')
  )

class Message (object):

  def __init__ (self, m):
    self.raw = m
    self.body = None
    self.origAddr = '%(origNet)d/%(origNode)d' % self.raw.header
    self.destAddr = '%(destNet)d/%(destNode)d' % self.raw.header
    self.kludge = {}

    self.parseKludgeLines()

  def __getattr__ (self, k):
    return getattr(self.raw, k)

  def __str__ (self):
    return 'From: %(fromUsername)s (%(origNet)d/%(origNode)d), ' \
      'To: %(toUsername)s (%(destNet)d/%(destNode)d), ' \
      'Re: %(subject)s' % self.raw.header

  def addKludge(self, line):
    try:
      k,v = line.strip().split(None, 1)
    except ValueError:
      k = line.strip().split()[0]
      v = None

    if k.endswith(':'):
      k = k[:-1]

    if self.kludge.has_key(k):
      self.kludge[k].append(v)
    else:
      self.kludge[k] = [v]

  def parseKludgeLines(self):
    tmp = StringIO(self.raw.body.replace('\r', '\n'))
    body = []
    s = 0
    for line in tmp:
      if line.startswith('\x01'):
        self.addKludge(line[1:])
      elif s == 0:
        if line.startswith('AREA:'):
          self.kludge['AREA'] = [line.strip().split(':')[1]]
        s = 1
      elif s == 1:
        if line.startswith(' * Origin:'):
          self.origin = line.strip()
          s = 2
        else:
          body.append(line)
      elif s == 2:
        self.addKludge(line)

    self.body = ''.join(body)

