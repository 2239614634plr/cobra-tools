class Root1Pad:

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.zero_0 = 0
		self.zero_1 = 0
		self.zero_2 = 0
		self.zero_3 = 0

	def read(self, stream):

		self.io_start = stream.tell()
		self.zero_0 = stream.read_uint()
		self.zero_1 = stream.read_uint()
		self.zero_2 = stream.read_uint()
		self.zero_3 = stream.read_uint()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_uint(self.zero_0)
		stream.write_uint(self.zero_1)
		stream.write_uint(self.zero_2)
		stream.write_uint(self.zero_3)

		self.io_size = stream.tell() - self.io_start

	def __repr__(self):
		s = 'Root1Pad [Size: '+str(self.io_size)+', Address: '+str(self.io_start)+'] ' + self.name
		s += '\n	* zero_0 = ' + self.zero_0.__repr__()
		s += '\n	* zero_1 = ' + self.zero_1.__repr__()
		s += '\n	* zero_2 = ' + self.zero_2.__repr__()
		s += '\n	* zero_3 = ' + self.zero_3.__repr__()
		s += '\n'
		return s
