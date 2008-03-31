#!/usr/bin/python

from pydonet.construct import *
import pydonet.formats.fts0001 as fts0001

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
  ULInt32('date_written'),
  ULInt32('date_arrived'),
  fts0001.Attributes('flags'),
  ULInt16('nextReply'),
)

