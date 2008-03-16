#!/usr/bin/python

from construct import *
import message

# http://www.ftsc.org/docs/fts-0001.016
HdrFTS0001 = Struct('FTS-0001',
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

# http://www.ftsc.org/docs/fsc-0039.001
HdrFSC0039 = Struct('FSC-0039',
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
	Array(4, ULInt8('fill')),
	ULInt8('pCodeHi'),
	ULInt8('pRevMinor'),
	ULInt16('capWord'),
	ULInt16('origZoneB'),
	ULInt16('destZoneB'),
	ULInt16('origPoint'),
	ULInt16('destPoint'),
	ULInt32('pData'),
)

# http://www.ftsc.org/docs/fsc-0048.002
HdrFSC0048 = Struct('FSC-0048',
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
	ULInt16('auxNet'),
	UBInt16('capWordA'),
	ULInt8('pCodeHi'),
	ULInt8('pRevMinor'),
	ULInt16('capWordB'),
	ULInt16('origZoneB'),
	ULInt16('destZoneB'),
	ULInt16('origPoint'),
	ULInt16('destPoint'),
	ULInt32('pData'),
)

def PacketReader (hdr):
  return Struct('packet',
      Rename('header', hdr),
      Rename('messages', GreedyRepeater(message.MessageReader)),
      Const(ULInt16('nullTerminator'), 0)
  )
    
class Packet (object):

  def __init__ (self, p):
    self.raw = p
    self.origAddr = '%(origZone)d:%(origNet)d/%(origNode)d.%(origPoint)d' % self.raw.header
    self.destAddr = '%(destZone)d:%(destNet)d/%(destNode)d.%(destPoint)d' % self.raw.header

  def __getattr__ (self, k):
    return getattr(self.raw, k)

  def __str__ (self):
    return '%s -> %s (%d messages)' \
        % (self.origAddr, self.destAddr, len(self.raw.messages))

def PacketFactory (src):

  p = HdrFSC0048.parse(src)
  if p.capWordA == 0:
    return Packet(PacketReader(HdrFTS0001).parse(src))
  elif p.capWordA != p.capWordB:
    return Packet(PacketReader(HdrFSC0039).parse(src))
  else:
    return Packet(PacketReader(HdrFSC0048).parse(src))

