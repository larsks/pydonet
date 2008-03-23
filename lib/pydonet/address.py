import re
from pydonet.utils.attrdict import AttrDict

re_address = re.compile('((?P<z>\d+):)?(?P<n>\d+)/(?P<f>\d+)(\.(?P<p>\d+))?(@(?P<d>\S+))?')

class Address (AttrDict):
  '''A class for manipulating Fidonet addresses.  Examples::
    
    >>> from pydonet.address import Address
    >>> a = Address('1:322/761')
    >>> print a
    1:322/761
    >>> print a.z
    1
    >> print a.n
    322
    >> print a.f
    761
    
    '''

  def __init__ (self, addr = None, z = None, n = None, f = None, p = None, d = None):
    if addr is not None:
      if isinstance(addr, Address):
          self.update(addr)
      else:
        mo = re_address.match(addr)
        if not mo:
          raise ValueError('\"%s\" is not a FTN address.' % addr)

        for attr in [ 'z', 'n', 'f', 'p', 'd' ]:
          self[attr] = mo.group(attr)

      for attr in [ 'z', 'n', 'f', 'p', 'd' ]:
        v = eval(attr)
        if v is not None:
          self[attr] = v

  def __str__ (self):
    addr = []
    if self.z is not None:
      addr.append('%s:' % self.z)

    addr.append('%s/%s' % (self.n, self.f))

    if self.p is not None:
      addr.append('.%s' % self.p)
    if self.d is not None:
      addr.append('@%s' % self.d)

    return ''.join(addr)

  def __repr__ (self):
    return str(self)

  def __hash__ (self):
    return hash(str(self))
