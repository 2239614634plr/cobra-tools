# START_GLOBALS
import logging
import time
from generated.formats.ms2.compound.packing_utils import *


# END_GLOBALS


class NewMeshData:

	# START_CLASS

	# @property
	def get_stream_index(self):
		# logging.debug(f"Using stream {self.stream_info.offset}")
		return self.stream_info.offset

	def update_dtype(self):
		"""Update MeshData.dt (numpy dtype) according to MeshData.flag"""
		# basic shared stuff
		dt = [
			("pos", np.int64),
			("normal", np.ubyte, (3,)),
			("winding", np.ubyte),
			("tangent", np.ubyte, (3,)),
			("bone index", np.ubyte),
		]
		# uv variations
		if self.flag == 528:
			dt.extend([
				("uvs", np.ushort, (1, 2)),
				("zeros0", np.int32, (3,))
			])
		elif self.flag == 529:
			dt.extend([
				("uvs", np.ushort, (2, 2)),
				("zeros0", np.int32, (2,))
			])
		elif self.flag in (533, 565, 821, 853, 885, 1013):
			dt.extend([
				("uvs", np.ushort, (2, 2)),  # second UV is either fins texcoords or fur length and shell tile scale
				("colors", np.ubyte, (1, 4)),  # these appear to be directional vectors
				("zeros0", np.int32)
			])
		elif self.flag == 513:
			dt.extend([
				("uvs", np.ushort, (2, 2)),
				# ("colors", np.ubyte, (1, 4)),
				("zeros2", np.uint64, (3,))
			])
		elif self.flag == 512:
			dt.extend([
				# last lod of many tree meshes (eg. tree_birch_white_03)
				# 8 uvs for an impostor texture atlas aka flipbook
				# a different unpacking factor is used here
				("uvs", np.ushort, (8, 2)),
			])
		elif self.flag == 517:
			dt.extend([
				("uvs", np.ushort, (1, 2)),
				("shapekeys0", np.uint32),
				("colors", np.ubyte, (1, 4)),  # this appears to be normals, or something similar
				("shapekeys1", np.int32),
				# sometimes, only the last is set, the rest being 00 00 C0 7F (NaN)
				("floats", np.float32, (4,)),
			])
		elif self.flag == 545:
			dt.extend([
				# cz_glasspanel_4m_02.mdl2
				("uvs", np.ushort, (1, 2)),
				("zeros2", np.uint32, (7,)),
			])
		# bone weights
		if self.flag.weights:
			dt.extend([
				("bone ids", np.ubyte, (4,)),
				("bone weights", np.ubyte, (4,)),
				("zeros1", np.uint64)
			])
		self.dt = np.dtype(dt)
		self.update_shell_count()
		if self.dt.itemsize != self.size_of_vertex:
			raise AttributeError(
				f"Vertex size for flag {self.flag} is wrong! Collected {self.dt.itemsize}, got {self.size_of_vertex}")

	def read_verts(self):
		self.fur_length = 0.0
		# get dtype according to which the vertices are packed
		self.update_dtype()
		# create arrays for the unpacked ms2_file
		self.init_arrays()
		# create array to populate with packed vertices
		self.verts_data = np.empty(dtype=self.dt, shape=self.vertex_count)
		# read the packed data
		self.buffer_info.verts.seek(self.vertex_offset)
		self.buffer_info.verts.readinto(self.verts_data)
		# logging.debug(f"Reading {self.vertex_count} verts at {self.buffer_info.verts.tell()}")
		# first cast to the float uvs array so unpacking doesn't use int division
		self.uvs[:] = self.verts_data["uvs"]
		if self.flag == 512:
			unpack_ushort_vector_impostor(self.uvs)
		else:
			unpack_ushort_vector(self.uvs)
		if "colors" in self.verts_data:
			# first cast to the float colors array so unpacking doesn't use int division
			self.colors[:] = self.verts_data["colors"]
			self.colors /= 255
		# todo - PZ uses at least bits 4, 5, 6 with a random pattern, while JWE2 pre-Biosyn uses really just the one bit
		# print(self.verts_data["winding"], set(self.verts_data["winding"]))
		self.windings = self.verts_data["winding"] // 128
		self.normals[:] = self.verts_data["normal"]
		self.tangents[:] = self.verts_data["tangent"]
		start_time = time.time()
		# before = np.copy(self.verts_data["pos"])
		# first = int(np.copy(before[0]))
		# print("before", bin(int(first)))
		# for i in range(3):
		# 	# grab the last 21 bits with bitand
		# 	twentyone_bits = first & 0b111111111111111111111
		# 	first >>= 21
		# 	print(bin(twentyone_bits))
		unpack_int64_vector(self.verts_data["pos"], self.vertices, self.use_blended_weights)
		# int21_vec = np.copy(self.vertices)
		scale_unpack_vectorized(self.vertices, self.base)
		if "bone weights" in self.dt.fields:
			bone_weights = self.verts_data["bone weights"].astype(np.float32) / 255
			self.get_blended_weights(self.verts_data["bone ids"], bone_weights)
		self.get_static_weights(self.verts_data["bone index"], self.use_blended_weights)

		# print("start")
		# # print(int21_vec)
		# scale_pack_vectorized(self.vertices, self.base)
		# # print(self.vertices)
		# print("int21_vec", np.allclose(int21_vec, self.vertices))
		# pack_int64_vector(self.verts_data["pos"], self.vertices.astype(np.int64), self.use_blended_weights)
		# for v in (int21_vec[0], self.vertices[0]):
		# 	print([bin(int(c)) for c in v])
		# print(bin(before[0]), type(before[0]))
		# print(bin(self.verts_data["pos"][0]))
		# print("packed int64", np.allclose(before, self.verts_data["pos"]))

		unpack_ubyte_vector(self.normals)
		unpack_ubyte_vector(self.tangents)
		unpack_swizzle_vectorized(self.vertices)
		unpack_swizzle_vectorized(self.normals)
		unpack_swizzle_vectorized(self.tangents)

		# unpack the shapekeys
		if self.flag == 517:
			# create the int64 by combining its two parts
			shapes_combined = self.verts_data["shapekeys1"].astype(np.int64)
			shapes_combined <<= 32
			shapes_combined |= self.verts_data["shapekeys0"]
			unpack_int64_vector(shapes_combined, self.shapekeys, self.shape_residues)
			scale_unpack_vectorized(self.shapekeys, self.base)
			unpack_swizzle_vectorized(self.shapekeys)

		# for bit in range(0, 8):
		# 	for vertex_index, res in enumerate((self.verts_data["winding"] >> bit) & 1):
		# 		# self.add_to_weights(f"bit{bit}", vertex_index, res/128)
		# 		self.add_to_weights(f"bit{bit}", vertex_index, res)
		logging.info(f"Unpacked mesh in {time.time() - start_time:.2f} seconds")

	def pack_verts(self):
		"""Repack flat lists into verts_data"""
		logging.info("Packing vertices")
		self.verts_data = np.zeros(self.vertex_count, dtype=self.dt)

		if self.flag == 517:
			pack_swizzle_vectorized(self.shapekeys)
			scale_pack_vectorized(self.shapekeys, self.base)
			shapes_combined = np.zeros(self.vertex_count, dtype=np.int64)
			# todo - store separate shape_residues?
			pack_int64_vector(shapes_combined, self.shapekeys.astype(np.int64), self.use_blended_weights)
			self.verts_data["shapekeys1"][:] = (shapes_combined >> 32) & 0b11111111111111111111111111111111
			self.verts_data["shapekeys0"][:] = shapes_combined & 0b11111111111111111111111111111111

		pack_swizzle_vectorized(self.vertices)
		pack_swizzle_vectorized(self.normals)
		pack_swizzle_vectorized(self.tangents)
		# print(self.use_blended_weights)
		scale_pack_vectorized(self.vertices, self.base)
		pack_int64_vector(self.verts_data["pos"], self.vertices.astype(np.int64), self.use_blended_weights)
		pack_ubyte_vector(self.normals)
		pack_ubyte_vector(self.tangents)
		if self.flag == 512:
			pack_ushort_vector_impostor(self.uvs)
		else:
			pack_ushort_vector(self.uvs)
		self.verts_data["normal"] = self.normals
		self.verts_data["tangent"] = self.tangents
		self.verts_data["uvs"] = self.uvs
		# non-vectorized data
		for i, vert in enumerate(self.verts_data):
			# winding seems to be a bitflag (flipped UV toggles the first bit of all its vertices to 1)
			# 0 = natural winding matching the geometry
			# 128 = UV's winding is flipped / inverted compared to geometry
			vert["winding"] = self.windings[i] * 128
			# bone index of the strongest weight
			if self.weights[i]:
				vert["bone index"] = self.weights[i][0][0]
			# else:
			# 	print(f"bad weight {i}, {self.weights[i]}")
			if "bone ids" in self.dt.fields:
				vert["bone ids"], vert["bone weights"] = self.unpack_weights_list(self.weights[i])
			if "colors" in self.dt.fields:
				vert["colors"] = list(list(round(c * 255) for c in vcol) for vcol in self.colors[i])

	def unpack_weights_list(self, weights_sorted):
		# pad the weight list to 4 bones, ie. add empty bones if missing
		for i in range(0, 4 - len(weights_sorted)):
			weights_sorted.append([0, 0])
		assert len(weights_sorted) == 4
		ids, weights = zip(*weights_sorted)
		return ids, self.quantize_bone_weights(weights)

