"""ADV32重定位类型定义"""

from ..encoding import Relocation
from ..token import Token, bit_range, bit
from .tokens import adv3216token,isa,Token13
from ...utils.bitfun import encode_imm32, align, wrap_negative

class TOKEN_COM(adv3216token):
    opcode = bit_range(0,16)

"""
1.要定义多少种重定位类型？
2.什么时候使用何种类型？ 比如跳转指令改用哪种类型？
"""

#定义PC相对寻址，用于跳转
@isa.register_relocation
class Rel32Relocation(Relocation):
    token = Token13
    name = "rel32"
    field = "rel32"

    def calc(self, sym_value, reloc_value):
        offset = sym_value - reloc_value + self.addend
        return offset


#定义绝对寻址，用于访问label
@isa.register_relocation
class Abs32Relocation(Relocation):
    token = TOKEN_COM
    name = "abs32"
    field = "abs32"

    def calc(self, sym_value, reloc_value):
        return sym_value

