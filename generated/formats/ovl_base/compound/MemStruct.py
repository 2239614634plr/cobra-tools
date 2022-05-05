
import logging
import xml.etree.ElementTree as ET
from numpy.core.multiarray import ndarray

from generated.array import Array
from generated.base_enum import BaseEnum
from generated.formats.ovl_base.compound.ArrayPointer import ArrayPointer
from generated.formats.ovl_base.compound.ForEachPointer import ForEachPointer
from generated.formats.ovl_base.compound.Pointer import Pointer

ZERO = b"\x00"
SKIPS = ("_context", "arg", "name", "io_start", "io_size", "template")
POOL_TYPE = "_pool_type"
XML_STR = "xml_string"


def indent(e, level=0):
	i = "\n" + level*"	"
	if len(e):
		if not e.text or not e.text.strip():
			e.text = i + "	"
		if not e.tail or not e.tail.strip():
			e.tail = i
		for e in e:
			indent(e, level+1)
		if not e.tail or not e.tail.strip():
			e.tail = i
	else:
		if level and (not e.tail or not e.tail.strip()):
			e.tail = i



from source.formats.base.basic import fmt_member
from generated.context import ContextReference


class MemStruct:

	"""
	this is a struct that is capable of having pointers
	"""

	context = ContextReference()

	def __init__(self, context, arg=0, template=None, set_default=True):
		self.name = ''
		self._context = context
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		if set_default:
			self.set_defaults()

	def set_defaults(self):
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
		pass

	@classmethod
	def write_fields(cls, stream, instance):
		pass

	@classmethod
	def from_stream(cls, stream, context, arg=0, template=None):
		instance = cls(context, arg, template, set_default=False)
		instance.io_start = stream.tell()
		cls.read_fields(stream, instance)
		instance.io_size = stream.tell() - instance.io_start
		return instance

	@classmethod
	def to_stream(cls, stream, instance):
		instance.io_start = stream.tell()
		cls.write_fields(stream, instance)
		instance.io_size = stream.tell() - instance.io_start
		return instance

	# used for the pointer alignment mapping
	ptr_al_dict = {}

	def get_props_and_ptrs(self):
		return [(prop, val) for prop, val in vars(self).items() if isinstance(val, Pointer)]

	def get_arrays(self):
		return [val for prop, val in vars(self).items() if isinstance(val, Array)]

	def get_memstructs(self):
		return [val for prop, val in vars(self).items() if isinstance(val, MemStruct)]

	def handle_write(self, val, struct_ptr, loader, ovs, pool_type, is_member=False):
		logging.debug(f"handle_write {type(val).__name__}, {len(loader.sized_str_entry.fragments)} frags")
		if isinstance(val, MemStruct):
			val.write_ptrs(loader, ovs, struct_ptr, pool_type, is_member=is_member)
		elif isinstance(val, Array):
			for member in val:
				self.handle_write(member, struct_ptr, loader, ovs, pool_type, is_member=True)
		elif isinstance(val, Pointer):
			if val.data:
				val.frag = loader.create_fragment(loader.sized_str_entry)
				val.frag.struct_ptr.pool = loader.get_pool(pool_type, ovs=ovs.arg.name)
				# this writes pointer.data to the pool
				val.write_pointer()
				# now repeat with pointer.data
				self.handle_write(val.data, val.frag.struct_ptr, loader, ovs, pool_type)
				# set link_ptr
				p = val.frag.link_ptr
				p.data_offset = val.io_start
				p.pool = struct_ptr.pool

	def write_ptrs(self, loader, ovs, struct_ptr, pool_type, is_member=False):
		logging.debug(f"write_ptrs")
		# don't write array members again, they have already been written!
		if not is_member:
			# write this struct's data
			struct_ptr.pool = loader.get_pool(pool_type, ovs=ovs.arg.name)
			struct_ptr.write_instance(type(self), self)
			logging.debug(f"memstruct's struct_ptr after {struct_ptr}")

		# write their data and update frags
		for prop, pointer in self.get_props_and_ptrs():
			self.handle_write(pointer, struct_ptr, loader, ovs, pool_type)
		# get all arrays of this MemStruct
		for array in self.get_arrays():
			self.handle_write(array, struct_ptr, loader, ovs, pool_type)

	def read_ptrs(self, pool):
		logging.debug(f"read_ptrs for {self.__class__.__name__}")
		# get all pointers in this struct
		for prop, ptr in self.get_props_and_ptrs():
			self.handle_pointer(prop, ptr, pool)
		# read arrays attached to this memstruct
		arrays = self.get_arrays()
		for array in arrays:
			# print(f"array, start at at {array.io_start}")
			for member in array:
				if isinstance(member, MemStruct):
					# print("member is a memstruct")
					member.read_ptrs(pool)
				elif isinstance(member, Pointer):
					self.handle_pointer(None, member, pool)
		# continue reading sub-memstructs directly attached to this memstruct
		for memstr in self.get_memstructs():
			memstr.read_ptrs(pool)

	def get_ptr_template(self, prop):
		"""Returns the appropriate template for a pointer named 'prop', if exists.
		Must be overwritten in subclass"""
		return None

	def handle_pointer(self, prop, pointer, pool):
		"""Ensures a pointer has a valid template, load it, and continue processing the linked memstruct."""
		logging.debug(f"handle_pointer for {self.__class__.__name__}")
		if not pointer.template:
			# try the lookup function
			pointer.template = self.get_ptr_template(prop)
		# reads the template and grabs the frag
		pointer.read_ptr(pool)  # , sized_str_entry)
		if pointer.frag and hasattr(pointer.frag, "struct_ptr"):
			pool = pointer.frag.struct_ptr.pool
			pointer.pool_type = pool.type
			logging.debug(f"Set pool type {pointer.pool_type} for pointer {prop}")
			if isinstance(pointer.data, MemStruct):
				# print("pointer to a memstruct")
				pointer.data.read_ptrs(pool)
			# ArrayPointer
			elif isinstance(pointer.data, Array):
				assert isinstance(pointer, (ArrayPointer, ForEachPointer))
				# print("ArrayPointer")
				for member in pointer.data:
					if isinstance(member, MemStruct):
						# print(f"member {member.__class__} of ArrayPointer is a MemStruct")
						member.read_ptrs(pool)
			else:
				# points to a normal struct or basic type, which can't have any pointers
				pass

	@classmethod
	def from_xml_file(cls, file_path, context, arg=0, template=None):
		"""Load MemStruct represented by the xml in 'file_path'"""
		instance = cls(context, arg, template, set_default=False)
		tree = ET.parse(file_path)
		xml = tree.getroot()
		instance.from_xml(xml)
		return instance

	def from_xml(self, elem):
		"""Sets the data from the XML to this MemStruct"""
		# go over all fields of this MemStruct
		# cast to list to avoid 'dictionary changed size during iteration'
		for prop, val in list(vars(self).items()):
			# skip dummy properties
			if prop in SKIPS:
				continue
			if isinstance(val, (MemStruct, Array, ndarray, Pointer)):
				sub = elem.find(f'.//{prop}')
				if sub is None:
					logging.warning(f"Missing sub-element '{prop}' on XML element '{elem.tag}'")
					return
				self._from_xml(self, sub, prop, val)
			else:
				self._from_xml(self, elem, prop, val)

	@staticmethod
	def _handle_xml_str(prop):
		return "data" if prop != XML_STR else XML_STR

	def _from_xml(self, target, elem, prop, val):
		"""Populates this MemStruct from the xml elem"""
		# print("_from_xml", elem, prop, val)
		if isinstance(val, Pointer):
			if val.template is None:
				logging.warning(f"No template set for pointer '{prop}' on XML element '{elem.tag}'")
				return
			if POOL_TYPE in elem.attrib:
				val.pool_type = int(elem.attrib[POOL_TYPE])
				logging.debug(f"Set pool type {val.pool_type} for pointer {prop}")
			else:
				logging.warning(f"Missing pool type for pointer '{prop}' on '{elem.tag}'")
			# print("val.template", val.template)
			if isinstance(val, ArrayPointer):
				# print("ArrayPointer", elem, len(elem))
				val.data = Array((len(elem)), val.template, val.context, set_default=False)
			else:
				# print("other pointer")
				logging.debug(f"Creating pointer.data = {val.template.__name__}()")
				# val.data = val.template(self._context, 0, val.arg, set_default=False)
				val.data = val.template(self._context, 0, val.arg)
			self._from_xml(val, elem, self._handle_xml_str(prop), val.data)
		elif isinstance(val, (Array, ndarray)):
			# create array elements
			# print(f"array, len {len(elem)}")
			if isinstance(val, ndarray):
				# todo - init from given dtype?
				val.resize(len(elem), refcheck=False)
				# print(val)
			else:
				val[:] = [val.dtype(self._context, 0, val.template, set_default=False) for i in range(len(elem))]
			# subelement with subelements
			for subelem, member in zip(elem, val):
				self._from_xml(self, subelem, subelem.tag, member)
		elif isinstance(val, MemStruct):
			# print("MemStruct")
			val.from_xml(elem)
		elif isinstance(val, BaseEnum):
			# print("BaseEnum")
			setattr(target, prop, val.from_str(elem.attrib[prop]))
		else:
			# print("basic")
			# set basic attribute
			cls = type(val)
			if prop != XML_STR:
				if prop in elem.attrib:
					data = elem.attrib[prop]
					if data != "None":
						try:
							logging.debug(f"Setting {type(target).__name__}.{prop} = {cls(data)}")
							setattr(target, prop, cls(data))
						except TypeError:
							raise TypeError(f"Could not convert attribute {prop} = '{data}' to {cls.__name__}")
				else:
					logging.warning(f"Missing attribute '{prop}' in element '{elem.tag}'")
			else:
				# logging.debug(f"Can't handle {XML_STR} inside '{elem.tag}'")
				data = ET.tostring(elem[0], encoding="unicode").replace("\t", "").replace("\n", "")
				setattr(target, "data", cls(data))
				logging.debug(f"Setting {type(target).__name__}.data = {cls(data)}")

	def to_xml_file(self, file_path):
		"""Create an xml elem representing this MemStruct, recursively set its data, indent and save to 'file_path'"""
		xml = ET.Element(self.__class__.__name__)
		self.to_xml(xml)
		indent(xml)
		with open(file_path, 'wb') as outfile:
			outfile.write(ET.tostring(xml))

	def _to_xml(self, elem, prop, val):
		"""Assigns data val to xml elem"""
		# logging.debug(f"_to_xml {elem.tag} - {prop}")
		if isinstance(val, Pointer):
			if val.frag and hasattr(val.frag, "struct_ptr"):
				f_ptr = val.frag.struct_ptr
				elem.set("_address", f"{f_ptr.pool_index} {f_ptr.data_offset}")
				elem.set("_size", f"{f_ptr.data_size}")
				elem.set(POOL_TYPE, f"{f_ptr.pool.type}")
			self._to_xml(elem, self._handle_xml_str(prop), val.data)
		# todo - multiple dimensions?
		elif isinstance(val, (Array, ndarray)):
			for member in val:
				cls_name = member.__class__.__name__.lower()
				member_elem = ET.SubElement(elem, cls_name)
				self._to_xml(member_elem, cls_name, member)
		elif isinstance(val, MemStruct):
			val.to_xml(elem)
		# basic attribute
		else:
			if prop == XML_STR:
				elem.append(ET.fromstring(val))
			else:
				elem.set(prop, str(val))

	def to_xml(self, elem):
		"""Adds data of this MemStruct to 'elem', recursively"""
		# go over all fields of this MemStruct
		for prop, val in vars(self).items():
			# skip dummy properties
			if prop in SKIPS:
				continue
			# add a sub-element if these are child of a MemStruct
			if isinstance(val, (MemStruct, Array, ndarray, Pointer)):
				sub = ET.SubElement(elem, prop)
				self._to_xml(sub, prop, val)
			else:
				self._to_xml(elem, prop, val)

	def debug_ptrs(self):
		"""Iteratively debugs all pointers of a struct"""
		cls_name = self.__class__.__name__
		if cls_name not in self.ptr_al_dict:
			self.ptr_al_dict[cls_name] = {}
		cls_al_dict = self.ptr_al_dict[cls_name]
		props_arrays = [(prop, val) for prop, val in vars(self).items() if isinstance(val, Array)]
		props_ptrs = self.get_props_and_ptrs() + [(prop, ptr) for prop, arr in props_arrays for ptr in arr if isinstance(ptr, Pointer)]
		for prop, ptr in props_ptrs:
			# dtype = pointer.template.__name__ if pointer.template else None
			# al = None
			if ptr.frag:
				# if isinstance(pointer.frag,)
				# skip dependency
				if not hasattr(ptr.frag, "struct_ptr"):
					continue
				d_off = ptr.frag.struct_ptr.data_offset
				if d_off:
					# go over decreasing possible alignments
					# 64, 32, 16, 8, 4, 2, 1
					for x in reversed(range(6)):
						al = 2 ** x
						# logging.debug(f"Testing alignment: {al}")
						# is data_offset of struct pointer aligned at al bytes?
						if d_off % al == 0:
							# add or overwrite if new al is smaller than stored al
							if prop not in cls_al_dict or al < cls_al_dict[prop]:
								cls_al_dict[prop] = al
							# don't test smaller alignments
							break
				# else:
				# 	al = "can't tell, data_offset=0"
				# test children
				if isinstance(ptr.data, MemStruct):
					ptr.data.debug_ptrs()
				elif isinstance(ptr.data, Array):
					for member in ptr.data:
						if isinstance(member, Pointer):
							member = member.data
						if isinstance(member, MemStruct):
							member.debug_ptrs()

			# logging.debug(f"Pointer: {prop} Dtype: {dtype} Alignment: {al}")
		logging.debug(f"MemStruct: {self.__class__.__name__} {cls_al_dict}")

	def get_info_str(self):
		return f'\nMemStruct'

	def get_fields_str(self):
		return ""

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return ""

