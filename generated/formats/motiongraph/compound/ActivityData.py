from generated.formats.base.basic import fmt_member
from generated.formats.motiongraph.compound.AnimationActivityData import AnimationActivityData
from generated.formats.ovl_base.compound.MemStruct import MemStruct


class ActivityData(MemStruct):

	"""
	# todo - investigate if this is a viable alternative, change codegen if needed to support string comparison
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		super().__init__(context, arg, template, set_default)
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.data = 0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		if self.arg == self.animation_activity:
			self.data = AnimationActivityData(self.context, 0, None)

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
		if instance.arg == instance.animation_activity:
			instance.data = AnimationActivityData.from_stream(stream, instance.context, 0, None)

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		if instance.arg == instance.animation_activity:
			AnimationActivityData.to_stream(stream, instance.data)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		super()._get_filtered_attribute_list(instance)
		if instance.arg == instance.animation_activity:
			yield ('data', AnimationActivityData, (0, None))

	def get_info_str(self, indent=0):
		return f'ActivityData [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* data = {fmt_member(self.data, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
