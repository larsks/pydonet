import pprint

from pydonet.message import Message
from pydonet.message import Body

m = Message('sample.msg')
print m.serialize()

