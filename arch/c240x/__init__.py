"""
To flash the c240x board, the following program can be used:

http://www.ti.com/tool/c240x-flasher

"""

from .arch import c240xArch
from .registers import c240xRegister, c240xWordRegister

__all__ = ["c240xArch", "c240xRegister", "c240xWordRegister"]
#__all__ = ["c240xArch"]
