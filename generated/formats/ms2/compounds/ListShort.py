from generated.formats.base.basic import Float
from generated.formats.ms2.compounds.Descriptor import Descriptor
from generated.formats.ms2.compounds.Vector3 import Vector3


class ListShort(Descriptor):

	"""
	used in JWE dinos
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# location of the joint
		self.loc = Vector3(self.context, 0, None)

		# normalized
		self.direction = Vector3(self.context, 0, None)

		# min, le 0
		self.min = 0.0

		# max, ge 0
		self.max = 0.0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.loc = Vector3(self.context, 0, None)
		self.direction = Vector3(self.context, 0, None)
		self.min = 0.0
		self.max = 0.0

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.loc = Vector3.from_stream(stream, instance.context, 0, None)
		instance.direction = Vector3.from_stream(stream, instance.context, 0, None)
		instance.min = Float.from_stream(stream, instance.context, 0, None)
		instance.max = Float.from_stream(stream, instance.context, 0, None)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Vector3.to_stream(stream, instance.loc)
		Vector3.to_stream(stream, instance.direction)
		Float.to_stream(stream, instance.min)
		Float.to_stream(stream, instance.max)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'loc', Vector3, (0, None), (False, None)
		yield 'direction', Vector3, (0, None), (False, None)
		yield 'min', Float, (0, None), (False, None)
		yield 'max', Float, (0, None), (False, None)

	def get_info_str(self, indent=0):
		return f'ListShort [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* loc = {self.fmt_member(self.loc, indent+1)}'
		s += f'\n	* direction = {self.fmt_member(self.direction, indent+1)}'
		s += f'\n	* min = {self.fmt_member(self.min, indent+1)}'
		s += f'\n	* max = {self.fmt_member(self.max, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
