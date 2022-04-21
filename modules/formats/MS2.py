import os
import shutil
import struct
import logging

from generated.formats.ms2 import Ms2File, Ms2Context
from generated.formats.ms2.compound.Ms2Root import Ms2Root

import generated.formats.ovl.versions as ovl_versions
from generated.formats.ovl_base.basic import ConvStream

from modules.formats.shared import get_versions, get_padding
from modules.formats.BaseFormat import BaseFile
from modules.helpers import as_bytes
from ovl_util import interaction


class Ms2Loader(BaseFile):
	extension = ".ms2"

	def get_version(self):
		ss_ptr = self.sized_str_entry.pointers[0]
		version = struct.unpack(f"I", ss_ptr.data[:4])[0]
		vdic = {"version": version}
		self.context = Ms2Context()
		self.context.version = version
		return vdic

	def get_frag_3(self, header):
		# some in JWE2 have a model2stream again
		expected_frag = b""
		if self.header.vertex_buffer_count:
			for stream in range(self.header.stream_count):
				expected_frag += struct.pack("<ii", 0, 0)
			for stream in range(self.header.vertex_buffer_count - self.header.stream_count):
				expected_frag += struct.pack("<ii", -1, 0)
		return expected_frag

	def collect(self):
		self.assign_ss_entry()
		self.get_version()
		ss_ptr = self.sized_str_entry.pointers[0]
		self.header = Ms2Root.from_stream(ss_ptr.stream, self.context)
		self.header.read_ptrs(ss_ptr.pool, self.sized_str_entry)
		# print(self.header)
		# old JWE1 still uses 1 fragment
		if self.header.version > 39:
			if ss_ptr.data_size != 48:
				logging.warning(f"Unexpected Root size ({ss_ptr.data_size}) for {self.file_entry.name}")
			expected_frag = self.get_frag_3(self.header)
			frag_data = self.header.buffers_presence.frag.pointers[1].data
			if frag_data != expected_frag:
				logging.warning(
					f"Unexpected frag 2 ptr data ({frag_data}) for {self.file_entry.name}, expected ({expected_frag})")
			for model_info in self.header.model_infos.data:
				objects_ptr = model_info.objects.frag.pointers[1]
				objects_ptr.split_data_padding(4 * model_info.num_objects)

	def create(self):
		ms2_file = Ms2File()
		ms2_file.load(self.file_entry.path, read_bytes=True)
		ms2_dir = os.path.dirname(self.file_entry.path)

		self.sized_str_entry = self.create_ss_entry(self.file_entry)
		self.sized_str_entry.children = []
		ss_ptr = self.sized_str_entry.pointers[0]

		self.header = ms2_file.info
		# fix up the pointers
		self.header.buffer_infos.data = ms2_file.buffer_infos
		self.header.model_infos.data = ms2_file.model_infos
		# todo - maybe store in ms2 file
		self.header.buffers_presence.data = self.get_frag_3(self.header)
		for model_info in ms2_file.model_infos:
			model_info.materials.data = model_info.model.materials
			model_info.lods.data = model_info.model.lods
			model_info.objects.data = model_info.model.objects
			model_info.meshes.data = model_info.model.meshes
			# just set empty data here, link later
			model_info.first_materials.data = b""
			for mesh in model_info.model.meshes:
				mesh.buffer_info.data = b""
				# link the right buffer_info, then clear offset value
				mesh.buffer_info.temp_index = mesh.buffer_info.offset
				# undo what we did on export
				mesh.buffer_info.offset = 0
		# print(self.header)
		# 1 for the ms2, 2 for each mdl2
		# pool.num_files += 1
		# create sized str entries and mesh data fragments
		for model_info, mdl2_name in zip(ms2_file.model_infos, ms2_file.mdl_2_names):
			# pool.num_files += 2
			mdl2_path = os.path.join(ms2_dir, mdl2_name+".mdl2")
			mdl2_file_entry = self.get_file_entry(mdl2_path)

			mdl2_entry = self.create_ss_entry(mdl2_file_entry)
			mdl2_entry.pointers[0].pool_index = -1
			self.sized_str_entry.children.append(mdl2_entry)

		# todo - padding like this is likely wrong, probably relative to start of materials
		# logging.debug(f"Objects data {objects_ptr.data_size}, padding {objects_ptr.padding_size}")
		# logging.debug(f"Sum {objects_ptr.data_size + objects_ptr.padding_size}")
		# logging.debug(f"rel offset {meshes.pointers[1].data_offset-materials.pointers[1].data_offset}")
		# logging.debug(f"rel mod 8 {(meshes.pointers[1].data_offset-materials.pointers[1].data_offset) % 8}")
		# self.write_to_pool(objects.pointers[1], 2, objects_bytes + get_padding(len(objects_bytes), alignment=8))

		# create ms2 data
		self.create_data_entry(self.sized_str_entry, ms2_file.buffers)
		# write the final memstruct
		self.header.write_ptrs(self, self.ovs, ss_ptr)
		# link some more pointers
		for model_info in self.header.model_infos.data:
			# link first_materials pointer
			first_materials = self.header.model_infos.data[0].materials.frag
			assert first_materials
			self.ptr_relative(model_info.first_materials.frag.pointers[1], first_materials.pointers[1])
			for mesh in model_info.model.meshes:
				# buffer_infos have been written, now make this mesh's buffer_info pointer point to the right entry
				offset = mesh.buffer_info.temp_index * self.header.buffer_infos.data[0].io_size
				self.ptr_relative(mesh.buffer_info.frag.pointers[1], self.header.buffer_infos.frag.pointers[1], rel_offset=offset)

	def update(self):
		if ovl_versions.is_pz16(self.ovl):
			logging.info(f"Updating MS2 buffer 0 with padding for {self.sized_str_entry.name}")
			name_buffer, bone_infos, verts = self.get_ms2_buffer_datas()
			# make sure buffer 0 is padded to 4 bytes
			padding = get_padding(len(name_buffer), 4)
			if padding:
				self.sized_str_entry.data_entry.update_data([name_buffer + padding, bone_infos, verts])
	
	def extract(self, out_dir, show_temp_files, progress_callback):
		self.get_version()
		name = self.sized_str_entry.name
		logging.info(f"Writing {name}")
		name_buffer, bone_infos, verts = self.get_ms2_buffer_datas()
		# truncate to 48 bytes for PZ af_keeperbodyparts
		ms2_general_info_data = self.sized_str_entry.pointers[0].data[:48]

		ms2_header = struct.pack("<I", len(bone_infos))
	
		# for i, buffer in enumerate(buffers):
		# 	p = out_dir(name+str(i)+".ms2")
		# 	with open(p, 'wb') as outfile:
		# 		outfile.write(buffer)

		# write the ms2 file
		out_path = out_dir(name)
		with ConvStream() as stream:
			stream.write(ms2_header)
			stream.write(ms2_general_info_data)
			for mdl2_entry in self.sized_str_entry.children:
				logging.debug(f"Writing {mdl2_entry.name}")
				stream.write(as_bytes(mdl2_entry.basename))
			stream.write(name_buffer)
			# export each mdl2
			if self.header.version > 39:
				# this corresponds to pc buffer 1 already
				# handle multiple buffer infos
				# grab all unique ptrs to buffer infos
				ptrs = set(mesh.buffer_info.frag.pointers[1] for model_info in self.header.model_infos.data for mesh in model_info.meshes.data)
				# get the sorted binary representations
				buffer_infos = [ptr.data for ptr in sorted(ptrs, key=lambda ptr: ptr.data_offset, reverse=True)]
				# turn the offset value of the pointers into a valid index
				for model_info in self.header.model_infos.data:
					for mesh in model_info.meshes.data:
						buffer_info_bytes = mesh.buffer_info.frag.pointers[1].data
						mesh.buffer_info.offset = buffer_infos.index(buffer_info_bytes)
				stream.write(b"".join(buffer_infos))
				self.header.model_infos.data.write(stream)
				for model_info in self.header.model_infos.data:
					for ptr in (model_info.materials, model_info.lods, model_info.objects, model_info.meshes):
						ptr.data.write(stream)
		
			with open(out_path, 'wb') as outfile:
				outfile.write(stream.getvalue())
				outfile.write(bone_infos)
				outfile.write(verts)
		# m = Ms2File()
		# m.load(out_path, read_editable=True)
		# m.save(out_path+"_.ms2")
		# print(m)
		return out_path,
	
	def get_ms2_buffer_datas(self):
		assert self.sized_str_entry.data_entry
		buffers_in_order = list(sorted(self.get_streams(), key=lambda b: b.index))
		for buff in buffers_in_order:
			logging.debug(f"buffer {buff.index}, size {buff.size} bytes")
		all_buffer_bytes = [buffer.data for buffer in buffers_in_order]
		name_buffer = all_buffer_bytes[0]
		bone_infos = all_buffer_bytes[1]
		verts = b"".join(all_buffer_bytes[2:])
		for i, vbuff in enumerate(all_buffer_bytes[2:]):
			logging.debug(f"Vertex buffer {i}, size {len(vbuff)} bytes")
		logging.debug(f"len buffers: {len(all_buffer_bytes)}")
		logging.debug(f"name_buffer: {len(name_buffer)}, bone_infos: {len(bone_infos)}, verts: {len(verts)}")
		return name_buffer, bone_infos, verts
	
	def load(self, ms2_file_path):
		logging.info(f"Injecting MS2")
		versions = get_versions(self.ovl)

		ms2_file = Ms2File()
		ms2_file.load(ms2_file_path, read_bytes=True)

		missing_materials = set()
		for model_info, mdl2_name, ovl_model_info in zip(ms2_file.model_infos, ms2_file.mdl_2_names, self.header.model_infos.data):
			for material in model_info.model.materials:
				fgm_name = f"{material.name.lower()}.fgm"
				if ovl_versions.is_jwe(self.ovl) or ovl_versions.is_jwe2(self.ovl) and fgm_name == "airliftstraps.fgm":
					# don't cry about this
					continue
				if fgm_name not in self.ovl._ss_dict:
					missing_materials.add(fgm_name)
			if ovl_model_info.num_meshes != model_info.num_meshes:
				raise AttributeError(
					f"{mdl2_name} ({model_info.num_meshes}) doesn't have the "
					f"expected amount ({ovl_model_info.num_meshes}) of meshes!")
		if missing_materials:
			mats = '\n'.join(missing_materials)
			msg = f"The following materials are used by {self.file_entry.name}, but are missing from the OVL:\n" \
				f"{mats}\n" \
				f"This will crash unless you are importing the materials from another OVL. Inject anyway?"
			if not interaction.showdialog(msg, ask=True):
				logging.info("Injection was canceled by the user")
				return

		for ovl_model_info, model_info in zip(self.header.model_infos.data, ms2_file.model_infos):
			for ptr, mdl2_list in (
					(ovl_model_info.materials, model_info.model.materials,),
					(ovl_model_info.lods, model_info.model.lods),
					(ovl_model_info.objects, model_info.model.objects),
					(ovl_model_info.meshes, model_info.model.meshes)):
				if len(mdl2_list) > 0:
					data = as_bytes(mdl2_list, version_info=versions)
					frag = ptr.frag
					# objects.pointers[1] has padding in stock, apparently as each entry is 4 bytes
					logging.debug(f"Injecting mdl2 data {len(data)} into {len(frag.pointers[1].data)} ({len(frag.pointers[1].padding)})")
					# frag.pointers[1].update_data(data, pad_to=8)
					# the above breaks injecting minmi
					frag.pointers[1].update_data(data)
					logging.debug(f"Result {len(frag.pointers[1].data)} ({len(frag.pointers[1].padding)})")

		# load ms2 ss data
		self.sized_str_entry.pointers[0].update_data(as_bytes(ms2_file.info, version_info=versions))
		self.header.buffer_infos.frag.pointers[1].update_data(as_bytes(ms2_file.buffer_infos, version_info=versions), update_copies=True)
		self.header.model_infos.frag.pointers[1].update_data(as_bytes(ms2_file.model_infos, version_info=versions))
	
		# update ms2 data
		self.sized_str_entry.data_entry.update_data(ms2_file.buffers)

	def rename_content(self, name_tuples):
		temp_dir, out_dir_func = self.get_tmp_dir()
		try:
			ms2_path = self.extract(out_dir_func, False, None)[0]
			# open the ms2 file
			ms2_file = Ms2File()
			ms2_file.load(ms2_path, read_bytes=True)
			# rename the materials
			ms2_file.rename(name_tuples)
			# update the hashes & save
			ms2_file.save(ms2_path)
			# inject again
			self.load(ms2_path)
		except BaseException as err:
			logging.warning(err)
		# delete temp dir again
		shutil.rmtree(temp_dir)
