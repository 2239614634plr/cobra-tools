class Material1:

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0

		# index into material0 array
		self.material_index = 0
		self.model_index = 0

	def read(self, stream):

		self.io_start = stream.tell()
		self.material_index = stream.read_ushort()
		self.model_index = stream.read_ushort()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_ushort(self.material_index)
		stream.write_ushort(self.model_index)

		self.io_size = stream.tell() - self.io_start

	def __repr__(self):
		s = 'Material1 [Size: '+str(self.io_size)+', Address: '+str(self.io_start)+'] ' + self.name
		s += '\n	* material_index = ' + self.material_index.__repr__()
		s += '\n	* model_index = ' + self.model_index.__repr__()
		s += '\n'
		return s
