from generated.base_struct import BaseStruct
from generated.formats.base.basic import Uint


class StreamEntry(BaseStruct):

	"""
	Description of one streamed file instance. One for every file stored in an ovs.
	Links the main pointers of a streamed file to its user, eg. a texturestream to a tex file.
	--These appear sorted in the order of sizedstr entries per ovs.-- only true for lod0, not lod1
	the order does not seem to be consistent
	interestingly, the order of root_entry entries per ovs is consistent with decreasing pool offset
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# offset to the stream's root_entry pointer inside the flattened mempools
		self.stream_offset = 0

		# offset to the user file's root_entry pointer (in STATIC) inside the flattened mempools
		self.file_offset = 0
		self.zero = 0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.stream_offset = 0
		self.file_offset = 0
		self.zero = 0

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.stream_offset = Uint.from_stream(stream, instance.context, 0, None)
		instance.file_offset = Uint.from_stream(stream, instance.context, 0, None)
		instance.zero = Uint.from_stream(stream, instance.context, 0, None)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Uint.to_stream(stream, instance.stream_offset)
		Uint.to_stream(stream, instance.file_offset)
		Uint.to_stream(stream, instance.zero)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'stream_offset', Uint, (0, None), (False, None)
		yield 'file_offset', Uint, (0, None), (False, None)
		yield 'zero', Uint, (0, None), (False, None)

	def get_info_str(self, indent=0):
		return f'StreamEntry [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* stream_offset = {self.fmt_member(self.stream_offset, indent+1)}'
		s += f'\n	* file_offset = {self.fmt_member(self.file_offset, indent+1)}'
		s += f'\n	* zero = {self.fmt_member(self.zero, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
