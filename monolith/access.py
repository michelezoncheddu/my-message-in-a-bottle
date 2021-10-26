from enum import Enum

class Access(Enum):
    NONE      = 0
    SENDER    = 1
    RECIPIENT = 2
    ALL       = 3
