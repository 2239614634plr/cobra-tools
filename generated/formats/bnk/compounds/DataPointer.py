from generated.base_struct import BaseStruct
from generated.formats.base.basic import Uint


class DataPointer(BaseStruct):

	"""
	second Section of a soundbank aux
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.wem_id = 0

		# offset into data section
		self.data_section_offset = 0

		# length of the wem file
		self.wem_filesize = 0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.wem_id = 0
		self.data_section_offset = 0
		self.wem_filesize = 0

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.wem_id = Uint.from_stream(stream, instance.context, 0, None)
		instance.data_section_offset = Uint.from_stream(stream, instance.context, 0, None)
		instance.wem_filesize = Uint.from_stream(stream, instance.context, 0, None)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Uint.to_stream(stream, instance.wem_id)
		Uint.to_stream(stream, instance.data_section_offset)
		Uint.to_stream(stream, instance.wem_filesize)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'wem_id', Uint, (0, None), (False, None)
		yield 'data_section_offset', Uint, (0, None), (False, None)
		yield 'wem_filesize', Uint, (0, None), (False, None)

	def get_info_str(self, indent=0):
		return f'DataPointer [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* wem_id = {self.fmt_member(self.wem_id, indent+1)}'
		s += f'\n	* data_section_offset = {self.fmt_member(self.data_section_offset, indent+1)}'
		s += f'\n	* wem_filesize = {self.fmt_member(self.wem_filesize, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
