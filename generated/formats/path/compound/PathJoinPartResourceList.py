from source.formats.base.basic import fmt_member
import numpy
from generated.array import Array
from generated.formats.ovl_base.compound.MemStruct import MemStruct
from generated.formats.path.compound.PathJoinPartResource import PathJoinPartResource


class PathJoinPartResourceList(MemStruct):

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.resources = Array((self.arg,), PathJoinPartResource, self.context, 0, None)
		self.padding = numpy.zeros(((self.arg % 2) * 8,), dtype=numpy.dtype('int8'))
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.resources = Array((self.arg,), PathJoinPartResource, self.context, 0, None)
		self.padding = numpy.zeros(((self.arg % 2) * 8,), dtype=numpy.dtype('int8'))

	def read(self, stream):
		self.io_start = stream.tell()
		self.read_fields(stream, self)
		self.io_size = stream.tell() - self.io_start

	def write(self, stream):
		self.io_start = stream.tell()
		self.write_fields(stream, self)
		self.io_size = stream.tell() - self.io_start

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.resources = Array.from_stream(stream, (instance.arg,), PathJoinPartResource, instance.context, 0, None)
		instance.padding = stream.read_bytes(((instance.arg % 2) * 8,))

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Array.to_stream(stream, instance.resources, (instance.arg,), PathJoinPartResource, instance.context, 0, None)
		stream.write_bytes(instance.padding)

	@classmethod
	def from_stream(cls, stream, context, arg=0, template=None):
		instance = cls(context, arg, template, set_default=False)
		instance.io_start = stream.tell()
		cls.read_fields(stream, instance)
		instance.io_size = stream.tell() - instance.io_start
		return instance

	@classmethod
	def to_stream(cls, stream, instance):
		instance.io_start = stream.tell()
		cls.write_fields(stream, instance)
		instance.io_size = stream.tell() - instance.io_start
		return instance

	def get_info_str(self, indent=0):
		return f'PathJoinPartResourceList [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* resources = {fmt_member(self.resources, indent+1)}'
		s += f'\n	* padding = {fmt_member(self.padding, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
