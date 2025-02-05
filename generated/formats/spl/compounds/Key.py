from generated.formats.base.basic import Float
from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.spl.compounds.ByteVector3 import ByteVector3
from generated.formats.spl.compounds.ShortVector3 import ShortVector3


class Key(MemStruct):

	"""
	JWE2: 16 bytes
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.pos = ShortVector3(self.context, 0, None)
		self.handle_left = ByteVector3(self.context, 0, None)
		self.handle_right = ByteVector3(self.context, 0, None)
		self.handle_scale = 0.0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.pos = ShortVector3(self.context, 0, None)
		self.handle_left = ByteVector3(self.context, 0, None)
		self.handle_right = ByteVector3(self.context, 0, None)
		self.handle_scale = 0.0

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.pos = ShortVector3.from_stream(stream, instance.context, 0, None)
		instance.handle_left = ByteVector3.from_stream(stream, instance.context, 0, None)
		instance.handle_right = ByteVector3.from_stream(stream, instance.context, 0, None)
		instance.handle_scale = Float.from_stream(stream, instance.context, 0, None)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		ShortVector3.to_stream(stream, instance.pos)
		ByteVector3.to_stream(stream, instance.handle_left)
		ByteVector3.to_stream(stream, instance.handle_right)
		Float.to_stream(stream, instance.handle_scale)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'pos', ShortVector3, (0, None), (False, None)
		yield 'handle_left', ByteVector3, (0, None), (False, None)
		yield 'handle_right', ByteVector3, (0, None), (False, None)
		yield 'handle_scale', Float, (0, None), (False, None)

	def get_info_str(self, indent=0):
		return f'Key [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* pos = {self.fmt_member(self.pos, indent+1)}'
		s += f'\n	* handle_left = {self.fmt_member(self.handle_left, indent+1)}'
		s += f'\n	* handle_right = {self.fmt_member(self.handle_right, indent+1)}'
		s += f'\n	* handle_scale = {self.fmt_member(self.handle_scale, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
