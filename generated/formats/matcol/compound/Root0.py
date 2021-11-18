from generated.context import ContextReference


class Root0:

	context = ContextReference()

	def __init__(self, context, arg=None, template=None, set_default=True):
		self.name = ''
		self._context = context
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.zero_0 = 0
		self.zero_1 = 0
		self.collection_count = 0
		self.zero_4 = 0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.zero_0 = 0
		self.zero_1 = 0
		self.collection_count = 0
		self.zero_4 = 0

	def read(self, stream):
		self.io_start = stream.tell()
		self.zero_0 = stream.read_uint()
		self.zero_1 = stream.read_uint()
		self.collection_count = stream.read_uint()
		self.zero_4 = stream.read_uint()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):
		self.io_start = stream.tell()
		stream.write_uint(self.zero_0)
		stream.write_uint(self.zero_1)
		stream.write_uint(self.collection_count)
		stream.write_uint(self.zero_4)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'Root0 [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* zero_0 = {self.zero_0.__repr__()}'
		s += f'\n	* zero_1 = {self.zero_1.__repr__()}'
		s += f'\n	* collection_count = {self.collection_count.__repr__()}'
		s += f'\n	* zero_4 = {self.zero_4.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s
