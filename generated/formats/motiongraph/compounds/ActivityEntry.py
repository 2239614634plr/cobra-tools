import generated.formats.motiongraph.compounds.Activity
from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.ovl_base.compounds.Pointer import Pointer


class ActivityEntry(MemStruct):

	"""
	8 bytes
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = Pointer(self.context, 0, generated.formats.motiongraph.compounds.Activity.Activity)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.value = Pointer(self.context, 0, generated.formats.motiongraph.compounds.Activity.Activity)

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.value = Pointer.from_stream(stream, instance.context, 0, generated.formats.motiongraph.compounds.Activity.Activity)
		if not isinstance(instance.value, int):
			instance.value.arg = 0

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Pointer.to_stream(stream, instance.value)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'value', Pointer, (0, generated.formats.motiongraph.compounds.Activity.Activity), (False, None)

	def get_info_str(self, indent=0):
		return f'ActivityEntry [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* value = {self.fmt_member(self.value, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
