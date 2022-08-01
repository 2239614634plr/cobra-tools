from generated.formats.motiongraph.compound.MotiongraphHeader import MotiongraphHeader
from modules.formats.BaseFormat import MemStructLoader


class MotiongraphLoader(MemStructLoader):
	target_class = MotiongraphHeader
	extension = ".motiongraph"
