#!/usr/bin/python

from pydonet.construct import *

# http://www.ftsc.org/docs/fsc-0039.001
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

