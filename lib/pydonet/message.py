#!/usr/bin/python

from construct import *

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
    self.origAddr = '%(origNet)d/%(origNode)d' % self.raw
    self.destAddr = '%(destNet)d/%(destNode)d' % self.raw

  def __getattr__ (self, k):
    return getattr(self.raw, k)

  def __str__ (self):
    return 'From: %(fromUsername)s (%(origNet)d/%(origNode)d), ' \
      'To: %(toUsername)s (%(destNet)d/%(destNode)d), ' \
      'Re: %(subject)s' % self.raw
