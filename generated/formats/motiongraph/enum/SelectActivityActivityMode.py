from generated.formats.base.basic import fmt_member
from generated.formats.base.enum import UintEnum


class SelectActivityActivityMode(UintEnum):
	ADVANCE_CHILDREN_TOGETHER = 0
	RESTART_CHILDREN_ON_SELECTION = 1
	CHOOSE_ONCE_AT_START = 2
