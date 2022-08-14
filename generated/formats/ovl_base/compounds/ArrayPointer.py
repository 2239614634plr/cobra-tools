
from generated.array import Array
from generated.formats.ovl_base.compounds.Pointer import Pointer
from generated.formats.ovl_base.compounds.Pointer import Pointer


class ArrayPointer(Pointer):

	"""
	a pointer to an array in an ovl memory layout
	"""

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		pass

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
		pass

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		pass

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)

	def get_info_str(self, indent=0):
		return f'ArrayPointer [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s

	def read_template(self):
		if self.template:
			self.data = Array.from_stream(self.frag.struct_ptr.stream, (self.arg,), self.template, self.context, 0, None)

	@classmethod
	def _to_xml(cls, instance, elem, debug):
		"""Assigns data self to xml elem"""
		# elem, prop, instance, arguments, debug
		# instance.template.to_xml(elem, instance._handle_xml_str(prop), instance.data, arguments, debug)
		# Array.to_xml(elem, "data", instance.data, (len(instance.data), instance.template, 0, None), debug)
		# Array._to_xml(elem, "data", instance.data, (len(instance.data), instance.template, 0, None), debug)
		Array._to_xml(instance.data, elem, debug)

	# def write_template(self):
	# 	assert self.template is not None
	# 	# Array.to_stream(self.frag.struct_ptr.stream, self.data, (len(self.data),), self.template, self.context, 0, None)
	# 	self.frag.struct_ptr.write_instance(self.template, self.data)

