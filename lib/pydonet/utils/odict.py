class OrderedDict (dict):

  def __init__ (self, *args, **kwargs):
    self.order = []
    super(OrderedDict, self).__init__(*args, **kwargs)

  def __setitem__ (self, k, v):
    if not self.has_key(k):
      self.order.append(k)

    super(OrderedDict, self).__setitem__(k, v)

  def __delitem__ (self, k):
    self.order.remove(k)
    super(OrderedDict, self).__delitem__(k)

  def clear(self):
    super(OrderedDict, self).clear()
    self.order = []

  def keys(self):
    return self.order

  def values(self):
    return [self[x] for x in self.order]

  def items(self):
    return zip(self.order, self.values())

  def pop(self, k):
    v = self[k]
    del self[k]
    return v

  def popitem(self):
    try:
      k = self.order[0]
    except IndexError:
      raise KeyError()

    v = self[k]
    del self[k]
    return (k, v)

def main():
  items = ( ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5) )
  d = OrderedDict()

  for k,v in items:
    d[k] = v

  d.pop('b')
  print d

  while True:
    try:
      k,v = d.popitem()
      print k, '=', v
    except KeyError:
      break

if __name__ == '__main__': main()

