import generated.formats.dinosaurmaterialvariants.compounds.Layer
import generated.formats.ovl_base.basic
from generated.formats.base.basic import Uint64
from generated.formats.ovl_base.compounds.ArrayPointer import ArrayPointer
from generated.formats.ovl_base.compounds.MemStruct import MemStruct
from generated.formats.ovl_base.compounds.Pointer import Pointer


class DinoLayersHeader(MemStruct):

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.layer_count = 0
		self.zero = 0
		self.fgm_name = Pointer(self.context, 0, generated.formats.ovl_base.basic.ZStringObfuscated)
		self.layers = ArrayPointer(self.context, self.layer_count, generated.formats.dinosaurmaterialvariants.compounds.Layer.Layer)
		if set_default:
			self.set_defaults()

	def set_defaults(self):
		super().set_defaults()
		self.layer_count = 0
		self.zero = 0
		self.fgm_name = Pointer(self.context, 0, generated.formats.ovl_base.basic.ZStringObfuscated)
		self.layers = ArrayPointer(self.context, self.layer_count, generated.formats.dinosaurmaterialvariants.compounds.Layer.Layer)

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		instance.fgm_name = Pointer.from_stream(stream, instance.context, 0, generated.formats.ovl_base.basic.ZStringObfuscated)
		instance.layers = ArrayPointer.from_stream(stream, instance.context, instance.layer_count, generated.formats.dinosaurmaterialvariants.compounds.Layer.Layer)
		instance.layer_count = Uint64.from_stream(stream, instance.context, 0, None)
		instance.zero = Uint64.from_stream(stream, instance.context, 0, None)
		if not isinstance(instance.fgm_name, int):
			instance.fgm_name.arg = 0
		if not isinstance(instance.layers, int):
			instance.layers.arg = instance.layer_count

	@classmethod
	def write_fields(cls, stream, instance):
		super().write_fields(stream, instance)
		Pointer.to_stream(stream, instance.fgm_name)
		ArrayPointer.to_stream(stream, instance.layers)
		Uint64.to_stream(stream, instance.layer_count)
		Uint64.to_stream(stream, instance.zero)

	@classmethod
	def _get_filtered_attribute_list(cls, instance):
		yield from super()._get_filtered_attribute_list(instance)
		yield 'fgm_name', Pointer, (0, generated.formats.ovl_base.basic.ZStringObfuscated), (False, None)
		yield 'layers', ArrayPointer, (instance.layer_count, generated.formats.dinosaurmaterialvariants.compounds.Layer.Layer), (False, None)
		yield 'layer_count', Uint64, (0, None), (False, None)
		yield 'zero', Uint64, (0, None), (False, None)

	def get_info_str(self, indent=0):
		return f'DinoLayersHeader [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self, indent=0):
		s = ''
		s += super().get_fields_str()
		s += f'\n	* fgm_name = {self.fmt_member(self.fgm_name, indent+1)}'
		s += f'\n	* layers = {self.fmt_member(self.layers, indent+1)}'
		s += f'\n	* layer_count = {self.fmt_member(self.layer_count, indent+1)}'
		s += f'\n	* zero = {self.fmt_member(self.zero, indent+1)}'
		return s

	def __repr__(self, indent=0):
		s = self.get_info_str(indent)
		s += self.get_fields_str(indent)
		s += '\n'
		return s
