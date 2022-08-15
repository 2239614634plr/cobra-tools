from io import BytesIO
from struct import Struct
from contextlib import contextmanager
from typing import *


MAX_LEN = 300000


Byte = Struct("<b")  # int8
UByte = Struct("<B")  # uint8
Short = Struct("<h")  # int16
UShort = Struct("<H")  # uint16
Int = Struct("<i")  # int32
UInt = Struct("<I")  # uint32
Int64 = Struct("<q")  # int64
UInt64 = Struct("<Q")  # uint64
Double = Struct("<d")  # float64
Float = Struct("<f")  # float32
HFloat = Struct("<e")  # float16


class IoFile:

	def load(self, filepath):
		with self.reader(filepath) as stream:
			self.read(stream)
			# self.from_stream(stream, self.context)
			return stream.tell()

	def save(self, filepath):
		with self.writer(filepath) as stream:
			self.write(stream)
			return stream.tell()

	@classmethod
	@contextmanager
	def reader(cls, filepath) -> Generator[BytesIO, None, None]:
		with open(filepath, "rb") as f:
			data = f.read()
		with BytesIO(data) as stream:
			yield stream  # type: ignore

	@classmethod
	@contextmanager
	def writer(cls, filepath) -> Generator[BytesIO, None, None]:
		with BytesIO() as stream:
			yield stream  # type: ignore
			with open(filepath, "wb") as f:
				# noinspection PyTypeChecker
				f.write(stream.getbuffer())
