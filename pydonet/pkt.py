import os, struct

# Based on:
# http://www.ftsc.org/docs/fsc-0048.002
PKT2P_FIELDS = (
    ('origNode',	'H'),
    ('destNode',	'H'),
    ('year',		  'H'),
    ('month',		  'H'),
    ('day',		    'H'),
    ('hour',		  'H'),
    ('minute',		'H'),
    ('second',		'H'),
    ('baud',		  'H'),
    ('version',		'H'),
    ('origNet',		'H'),
    ('destNet',   'H'),
    ('productCodeA',     'B'),
    ('productRevisionA', 'B'),
    ('password',  '8s'),
    ('origZone',	'H'),
    ('destZone',  'H'),
    ('auxNet',    'H'),
    ('capWordA1',    'B'),
    ('capWordA0',    'B'),
    ('productCodeB',     'B'),
    ('productRevisionB', 'B'),
    ('capWordB0',    'B'),
    ('capWordB1',    'B'),
    ('origZoneB',	'H'),
    ('destZoneB',  'H'),
    ('origPoint',	'H'),
    ('destPoint',  'H'),
    ('prodData',  '4B'),
    )

# By inspection.  Anyone know the relevant standard?
MSGHDR_FIELDS = (
    ('unknown', 'H'),
    ('origNode', 'H'),
    ('destNode', 'H'),
    ('origNet', 'H'),
    ('destNet', 'H'),
    ('origPoint', 'H'),
    ('destPoint', 'H'),
    )

class _PKT2P (struct.Struct):

  def __init__ (self):
    super(_PKT2P, self).__init__('<' + ''.join(x[1] for x in PKT2P_FIELDS))

class _MSGHDR (struct.Struct):

  def __init__ (self):
    super(_MSGHDR, self).__init__('<' + ''.join(x[1] for x in MSGHDR_FIELDS))

class Packet (dict):

  def __init__ (self, path):
    self.path = path
    self.parse()

  def parse(self):
    raw = open(self.path).read()
    reader = _PKT2P()
    self.update(dict(zip([x[0] for x in PKT2P_FIELDS], \
        reader.unpack(raw[:reader.size]))))


if __name__ == '__main__':

  import sys
  packet = Packet(sys.argv[1])
  print packet

#  raw = open(sys.argv[1]).read()
#  reader = _PKT2P()
#  packet = zip([x[0] for x in PKT2P_FIELDS], \
#      reader.unpack(raw[:reader.size]))
#  print 'PACKET'
#  print packet
#  print
#
#  raw = raw[reader.size:]
#  reader = _MSGHDR()
#  msghdr = zip([x[0] for x in MSGHDR_FIELDS], \
#      reader.unpack(raw[:reader.size]))
#  print 'HEADER'
#  print msghdr
#  print
#
#  msg = raw[reader.size:]
#
#  print 'MESSAGE:'
#  print msg.replace('\015', '\012')
#  print


