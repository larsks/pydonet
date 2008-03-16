import os

'''Tools for reading data in a TIC file.'''

# This is a list of fields we read from a TIC file.  We ignore
# everything else.
FIELDS = (
  'created',
  'area',
  'origin',
  'from',
  'file',
  'size',
  'desc',
  'crc',
  'areadesc',
)

MV_FIELDS = (
  'seenby',
  'path',
    )

class TIC (dict):

  def __init__ (self, path):
    self.valid = False
    self.path = path
    self.base = os.path.dirname(path)
    self.parse()
    self.validate()

  def parse(self):
    fd = open(self.path)
    for line in fd:
      line = line.strip()
      try:
        k,v = line.split(None, 1)
        if k.lower() in FIELDS:
          self[k.lower()] = v
        elif k.lower() in MV_FIELDS:
          if self.has_key(k.lower()):
            self[k.lower()].append(v)
          else:
            self[k.lower()] = [v]
      except ValueError:
        continue

  def validate(self):
    if not os.path.exists(os.path.join(self.base, self['file'])):
      return

    self.valid = True

if __name__ == '__main__':
  import sys
  import pprint

  t = TIC(sys.argv[1])
  pprint.pprint(t)

