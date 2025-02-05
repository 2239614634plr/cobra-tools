import numpy
from generated.array import Array
from generated.base_struct import BaseStruct
from generated.formats.base.basic import Byte
from generated.formats.base.basic import Short


class MinusPadding(BaseStruct):

	"""
	Used in PC
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# -1
		self.indices = numpy.zeros((self.arg,), dtype=numpy.dtype('int16'))

		# 0
		self.padding = numpy.zeros(((16 - ((self.arg * 2) % 16)) % 16,), dtype=numpy.dtype('int8'))
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.indices = numpy.zeros((self.arg,), dtype=numpy.dtype('int16'))
		self.padding = numpy.zeros(((16 - ((self.arg * 2) % 16)) % 16,), dtype=numpy.dtype('int8'))

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.indices = Array.from_stream(stream, instance.context, 0, None, (instance.arg,), Short)
		instance.padding = Array.from_stream(stream, instance.context, 0, None, ((16 - ((instance.arg * 2) % 16)) % 16,), Byte)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Array.to_stream(stream, instance.indices, (instance.arg,), Short, instance.context, 0, None)
		Array.to_stream(stream, instance.padding, ((16 - ((instance.arg * 2) % 16)) % 16,), Byte, instance.context, 0, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'indices', Array, ((instance.arg,), Short, 0, None), (False, None)
		yield 'padding', Array, (((16 - ((instance.arg * 2) % 16)) % 16,), Byte, 0, None), (False, None)

	def get_info_str(self, indent=0):
		return f'MinusPadding [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* indices = {self.fmt_member(self.indices, indent+1)}'
		s += f'\n	* padding = {self.fmt_member(self.padding, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
