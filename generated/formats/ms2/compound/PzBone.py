from generated.formats.ms2.compound.Vector3 import Vector3
from generated.formats.ms2.compound.Vector4 import Vector4


class PzBone:

	"""
	32 bytes
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.rot = Vector4()
		self.loc = Vector3()
		self.scale = 0

	def read(self, stream):

		self.io_start = stream.tell()
		self.rot = stream.read_type(Vector4)
		self.loc = stream.read_type(Vector3)
		self.scale = stream.read_float()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_type(self.rot)
		stream.write_type(self.loc)
		stream.write_float(self.scale)

		self.io_size = stream.tell() - self.io_start

	def __repr__(self):
		s = 'PzBone [Size: '+str(self.io_size)+', Address: '+str(self.io_start)+'] ' + self.name
		s += '\n	* rot = ' + self.rot.__repr__()
		s += '\n	* loc = ' + self.loc.__repr__()
		s += '\n	* scale = ' + self.scale.__repr__()
		s += '\n'
		return s

	def set_bone(self, matrix):
		pos, quat, sca = matrix.decompose()
		self.loc.x, self.loc.y, self.loc.z = pos.x, pos.y, pos.z
		self.rot.x, self.rot.y, self.rot.z, self.rot.w = quat.x, quat.y, quat.z, quat.w
		self.scale = sca.x

