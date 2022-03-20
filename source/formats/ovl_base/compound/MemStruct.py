# START_GLOBALS
from generated.array import Array
from generated.formats.ovl_base.compound.Pointer import Pointer
import xml.etree.ElementTree as ET

ZERO = b"\x00"


# END_GLOBALS

class MemStruct:
	"""this is a struct that is capable of having pointers"""
# START_CLASS

	def get_ptrs(self):
		return [val for prop, val in vars(self).items() if isinstance(val, Pointer)]

	def get_arrays(self):
		return [val for prop, val in vars(self).items() if isinstance(val, Array)]

	def read_ptrs(self, ovs, ref_ptr, io_start=None):
		if not io_start:
			io_start = self.io_start
		# print("read_ptrs")
		# get all pointers in this struct
		ptrs = self.get_ptrs()
		for ptr in ptrs:
			self.handle_ptr(ptr, ovs, ref_ptr, io_start)
		arrays = self.get_arrays()
		for array in arrays:
			# print("array")
			for member in array:
				if isinstance(member, MemStruct):
					# print("member is a memstruct")
					member.read_ptrs(ovs, ref_ptr, array.io_start)

	def handle_ptr(self, ptr, ovs, ref_ptr, io_start):
		rel_offset = ptr.io_start-io_start
		# print(f"handle_ptr dtype: {ptr.template.__name__} relative: {rel_offset} count: {ptr.arg}")
		# get a fragment that is relative to pointer + offset
		f = ovs.frag_at_pointer(ref_ptr, offset=rel_offset)
		# ptr may be a nullptr, so ignore
		if not f:
			# print("is a nullptr")
			return
		f_ptr = f.pointers[1]
		ptr.data = ptr.template.from_stream(f_ptr.stream, ptr.context, ptr.arg)
		if isinstance(ptr.data, MemStruct):
			# print("is a memstruct")
			ptr.data.read_ptrs(ovs, f_ptr)

	def to_xml_file(self, fp):
		pass

	def _to_xml(self, elem, prop, val):
		subelement = ET.SubElement(elem, prop)
		# pointer points to a memstruct
		if isinstance(val, MemStruct):
			print("memstruct")
			val.to_xml(subelement)
		# points to a basic type
		else:
			print("basic")
			subelement.set("data", str(val))

	def to_xml(self, elem):
		nopes = ("_context", "arg", "name", "io_start", "io_size", "template")
		for prop, val in vars(self).items():
			if prop in nopes:
				continue
			if isinstance(val, Pointer):
				print("pointer")
				# subelement
				self._to_xml(elem, prop, val.data)
			elif isinstance(val, Array):
				print("array")
				# subelement with subelements
				# print(val.dtype)
				for member in val:
					self._to_xml(elem, val.class_name, member)
			else:
				# attribute
				elem.set(prop, str(val))
				pass

	def get_info_str(self):
		return f'\nMemStruct'

	def get_fields_str(self):
		return ""

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return ""
