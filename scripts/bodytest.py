import pprint

from pydonet.message import Message
from pydonet.message import Body

m = Message('sample.msg')
b = Body(m.body.body)

print 'KLINES:'
pprint.pprint(b.klines)

print 'ORIGIN:'
print b.origin

print 'SEENBY:'
pprint.pprint(b.seenby)

pprint.pprint(b.lines)

