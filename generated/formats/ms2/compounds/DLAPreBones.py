import numpy
from generated.array import Array
from generated.base_struct import BaseStruct
from generated.formats.base.basic import Ubyte


class DLAPreBones(BaseStruct):

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unk = numpy.zeros((120,), dtype=numpy.dtype('uint8'))
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.unk = numpy.zeros((120,), dtype=numpy.dtype('uint8'))

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.unk = Array.from_stream(stream, instance.context, 0, None, (120,), Ubyte)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Array.to_stream(stream, instance.unk, (120,), Ubyte, instance.context, 0, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'unk', Array, ((120,), Ubyte, 0, None), (False, None)

	def get_info_str(self, indent=0):
		return f'DLAPreBones [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* unk = {self.fmt_member(self.unk, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
