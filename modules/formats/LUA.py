import logging
from generated.formats.lua.compound.LuaRoot import LuaRoot
from modules.formats.BaseFormat import MemStructLoader
from ovl_util import texconv
from ovl_util.interaction import showdialog


class LuaLoader(MemStructLoader):
	extension = ".lua"
	target_class = LuaRoot
	
	def create(self):
		buffer_0 = self._get_data(self.file_entry.path)
		self.sized_str_entry = self.create_ss_entry(self.file_entry)
		self.create_data_entry(self.sized_str_entry, (buffer_0,))

		self.header = LuaRoot(self.ovl.context)
		self.header.lua_size = len(buffer_0)
		self.header.source_path = self.file_entry.basename
		# todo - likely wrong, not sure how to handle
		self.header.likely_alignment = b"\x00"
		self.header.write_ptrs(self, self.ovs, self.sized_str_entry.struct_ptr, self.file_entry.pool_type)

	def load(self, file_path):
		buffer_0 = self._get_data(file_path)
		self.header.lua_size = len(buffer_0)
		# todo - update stream from header
		# self.sized_str_entry.struct_ptr.update_data(ss, update_copies=True)
		self.sized_str_entry.data_entry.update_data((buffer_0,))

	def extract(self, out_dir, show_temp_files, progress_callback):
		name = self.sized_str_entry.name
		logging.info(f"Writing {name}")
		buffer_data = self.sized_str_entry.data_entry.buffer_datas[0]
		logging.debug(f"buffer size: {len(buffer_data)}")
		# write lua
		out_path = out_dir(name)
		# print(out_path)
		# DLA & ZTUAC - clip away the start (fragment data at start of buffer?)
		if self.ovl.context.version <= 17:
			buffer_data = buffer_data[8:]
		out_files = []
		if buffer_data[1:4] == b"Lua":
			logging.debug("compiled lua")
			bin_path = out_path + ".bin"
			with open(bin_path, 'wb') as outfile:
				# write the buffer
				outfile.write(buffer_data)
			# see if it worked
			if texconv.bin_to_lua(bin_path):
				out_files.append(out_path)
				# optional bin
				if show_temp_files:
					out_files.append(bin_path)
			# no conversion, just get bin
			else:
				out_files.append(bin_path)
		else:
			logging.debug("uncompiled lua")
			with open(out_path, 'wb') as outfile:
				# write the buffer
				outfile.write(buffer_data)
			out_files.append(out_path)
		return out_files

	def _get_data(self, file_path):
		"""Loads and returns the data for a LUA"""
		buffer_0 = self.get_content(file_path)
		if b"DECOMPILER ERROR" in buffer_0:
			confirmed = showdialog(
				f"{file_path} has not been successfully decompiled and may crash your game. Inject anyway?", ask=True)
			if not confirmed:
				raise UserWarning(f"Injection aborted for {file_path}")
		return buffer_0
