#!/usr/bin/python

from pydonet.construct import *

# http://www.ftsc.org/docs/fts-0001.016
PacketHeader = Struct('header',
	ULInt16('origNode'),
	ULInt16('destNode'),
	ULInt16('year'),
	ULInt16('month'),
	ULInt16('day'),
	ULInt16('hour'),
	ULInt16('minute'),
	ULInt16('second'),
	ULInt16('speed'),
	Const(ULInt16('packetType'), 2),
	ULInt16('origNet'),
	ULInt16('destNet'),
	ULInt8('pCodeLo'),
	ULInt8('pRevMajor'),
	String("password", 8),
	ULInt16('origZone'),
	ULInt16('destZone'),
	Array(20, ULInt8('fill')),
)

def Attributes (name):
  return FlagsEnum(ULInt16(name),
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
  )

PackedMessageHeader = Struct('message',
  Const(ULInt16('messageType'), 2),
  ULInt16('origNode'),
  ULInt16('destNode'),
  ULInt16('origNet'),
  ULInt16('destNet'),
  Attributes('flags'),
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
  ULInt16('origNet'),
  ULInt16('destNet'),
  ULInt16('destZone'),
  ULInt16('origZone'),
  ULInt16('destPoint'),
  ULInt16('origPoint'),
  ULInt16('replyTo'),
  Attributes('flags'),
  ULInt16('nextReply'),
)

MessageBody = CString('body')

