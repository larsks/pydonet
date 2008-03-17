import re

re_address = re.compile('((?P<z>\d+):)?(?P<n>\d+)/(?P<f>\d+)(\.(?P<p>\d+))?')

class Address (object):

  def __init__ (self, addr = None, z = None, n = None, f = None, p = None):
    if addr is not None:
      mo = re_address.match(addr)
      if not mo:
        raise ValueError('\"%s\" is not a FTN address.' % addr)

      self.z = mo.group('z')
      self.n = mo.group('n')
      self.f = mo.group('f')
      self.p = mo.group('p')

  def __str__ (self):
    addr = []
    if self.z is not None:
      addr.append('%s:' % self.z)

    addr.append('%s/%s' % (self.n, self.f))

    if self.p is not None:
      addr.append('.%s' % self.p)

    return ''.join(addr)

  def __repr__ (self):
    return 'Address("%s")' % self

