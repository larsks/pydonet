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

def modifiedPascalString(name, len, padchar = '\x00'):
  return Embed(Struct(name,
      ULInt8('%sLen' % name),
      String(name, len, padchar = padchar),
  ))

def Integer(name):
  return ULInt16(name)

def Boolean(name):
  return OneOfValidator(Byte(name), [0,1])

def Char(name):
  return String(name, 1)

def EmailAddress (name):
  return Struct(name,
    Integer('zone'),
    Integer('net'),
    Integer('node'),
    Integer('point'),
    modifiedPascalString('domain', 12),
  )

ADFRecord = Struct('ADFRecord',
  Boolean('allocated'),
  Char('alertFlag'),
  modifiedPascalString('areaTag', 16),
  modifiedPascalString('areaName', 80),
  modifiedPascalString('areaDesc', 40),
  Char('groupAccess'),
  Char('groupSort'),
  Enum(Char('storage'),
    FIDONET   = 'F',
    QUICKBBS  = 'Q',
    PASSTHRU  = 'N',
    _default_ = Pass,
  ),
  Char('processWeb'),
  Char('webASCII'),
  Integer('rescanLimit'),
  Integer('qwk'),
  Boolean('fpnpForced'),
  modifiedPascalString('directoryPath', 48),
  modifiedPascalString('database', 8),
  Enum(Char('kind'),
    LOCAL     = 'L',
    ECHOMAIL  = 'E',
    _default_ = Pass,
  ),
  Integer('quickArea'),
  Boolean('defaultPrivate'),
  Boolean('stripSeenbys'),
  modifiedPascalString('originLine', 56),
  Enum(Char('defaultPriority'),
    NORMAL    = 'N',
    CRASH     = 'C',
    IMMEDIATE = 'I',
    HOLD      = 'H',
    _default_ = Pass,
  ),
  EmailAddress('originAddress'),
  Integer('purge'),
  Integer('preserve'),
  Integer('security'),
  modifiedPascalString('archive', 80),
  Integer('highest'),
  Integer('received'),
  Integer('dupes'),
  Boolean('updateLast'),
  Array(19, Struct('forwardTo', modifiedPascalString('address', 76)))
)

# An ADF file may have zero or more ADFRecords.
ADF = OptionalGreedyRepeater(ADFRecord)

if __name__ == '__main__':
  import sys
  print 'sizeof(EmailAddress) = ', EmailAddress('tmp').sizeof()
  print 'sizeof(ADFRecord) = ', ADFRecord.sizeof()

  a = ADF.parse_stream(open(sys.argv[1]))
  n = 0
  for area in a:
    print 'AREA', n
    print area
    print
    n += 1

