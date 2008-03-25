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

class RepeatUntilSafe(Subconstruct):
    """
    An array that repeat until the predicate indicates it to stop. Note that
    the last element (which caused the repeat to exit) is included in the 
    return value.

    Parameters:
    * predicate - a predicate function that takes (obj, context, stream) and returns
      True if the stop-condition is met, or False to continue.
    * subcon - the subcon to repeat.
    
    Example:
    # will read chars until \x00 (inclusive)
    RepeatUntil(lambda obj, ctx: obj == "\x00",
        Field("chars", 1)
    )
    """
    __slots__ = ["predicate"]
    def __init__(self, predicate, subcon):
        Subconstruct.__init__(self, subcon)
        self.predicate = predicate
        self._clear_flag(self.FLAG_COPY_CONTEXT)
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        obj = []
        try:
            if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
                while True:
                    subobj = self.subcon._parse(stream, context.__copy__())
                    obj.append(subobj)
                    if self.predicate(subobj, context):
                        break
            else:
                while True:
                    subobj = self.subcon._parse(stream, context)
                    obj.append(subobj)
                    if self.predicate(subobj, context):
                        break
        except FieldError:
            pass
        except ConstructError, ex:
            raise ArrayError("missing terminator", ex)
        return obj
    def _build(self, obj, stream, context):
        terminated = False
        if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
            for subobj in obj:
                self.subcon._build(subobj, stream, context.__copy__())
                if self.predicate(subobj, context): 
                    terminated = True
                    break
        else:
            for subobj in obj:
                self.subcon._build(subobj, stream, context.__copy__())
                if self.predicate(subobj, context):
                    terminated = True
                    break
        if not terminated:
            raise ArrayError("missing terminator")
    def _sizeof(self, context):
        raise SizeofError("can't calculate size")


def eofSafeCString (name, terminators = "\x00", encoding = None, 
    char_field = Field(None, 1)):
  '''This is like a CString, except that it won't barf if the parser
    finds an EOF before finding a terminator.'''

  return Rename(name,
      CStringAdapter(
        RepeatUntilSafe(lambda obj, ctx: obj in terminators, 
            char_field,
        ),
        terminators = terminators,
        encoding = encoding,
      )
  )

MessageBody = eofSafeCString('body')

def Message(header, body):
  return Struct(
    header,
    body
  )

