from generated.formats.base.basic import fmt_member
import generated.formats.renderparameters.compound.Param
from generated.array import Array
from generated.formats.ovl_base.compound.MemStruct import MemStruct
from generated.formats.ovl_base.compound.Pointer import Pointer


class ParamList(MemStruct):

	"""
	this is not null ptr terminated, but padded to 16 bytes at the end
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.ptrs = 0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		self.ptrs = Array((self.arg,), Pointer, self.context, 0, generated.formats.renderparameters.compound.Param.Param)

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
		instance.ptrs = Array.from_stream(stream, (instance.arg,), Pointer, instance.context, 0, generated.formats.renderparameters.compound.Param.Param)
		instance.ptrs.arg = 0

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Array.to_stream(stream, instance.ptrs, (instance.arg,), Pointer, instance.context, 0, generated.formats.renderparameters.compound.Param.Param)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		super()._get_filtered_attribute_list(instance)
		yield ('ptrs', Array, ((instance.arg,), Pointer, 0, generated.formats.renderparameters.compound.Param.Param))

	def get_info_str(self, indent=0):
		return f'ParamList [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* ptrs = {fmt_member(self.ptrs, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
