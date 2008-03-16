#!/usr/bin/python

from construct import *
from StringIO import StringIO

# http://www.ftsc.org/docs/fts-0001.016
MessageReader = Struct('message',
  Const(ULInt16('messageType'), 2),
  ULInt16('origNode'),
  ULInt16('destNode'),
  ULInt16('origNet'),
  ULInt16('destNet'),
  ULInt16('attr'),
  ULInt16('cost'),
  StrictRepeater(20, ULInt8('dateTime')),
  CString('toUsername'),
  CString('fromUsername'),
  CString('subject'),
  CString('body')
)

class Message (object):

  def __init__ (self, m):
    self.raw = m
    self.body = None
    self.origAddr = '%(origNet)d/%(origNode)d' % self.raw
    self.destAddr = '%(destNet)d/%(destNode)d' % self.raw
    self.kludge = {}

    self.parseKludgeLines()

  def __getattr__ (self, k):
    return getattr(self.raw, k)

  def __str__ (self):
    return 'From: %(fromUsername)s (%(origNet)d/%(origNode)d), ' \
      'To: %(toUsername)s (%(destNet)d/%(destNode)d), ' \
      'Re: %(subject)s' % self.raw

  def addKludge(self, line):
    k,v = line.strip().split(': ')
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

