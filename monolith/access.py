from enum import Enum

class Access(Enum):
    '''Access rights for a message. Unix-style.'''
    NONE      = 0
    SENDER    = 1
    RECIPIENT = 2
    ALL       = 3
