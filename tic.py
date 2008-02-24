import os

FIELDS = (
	'area',
	'origin',
	'file',
	'size',
	'desc',
	'areadesc',
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
			except ValueError:
				continue

	def validate(self):
		if not os.path.exists(os.path.join(self.base, self['file'])):
			return

		self.valid = True

