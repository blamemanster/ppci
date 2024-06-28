"""C28X浮点指令集的token类"""
from ppci.arch.arch_info import Endianness
from ..token import Token, bit_range, bit


#两种长度类型16/32
class adv32f16tokens(Token):
    class Info:
        size = 16
class adv32f32tokens(Token):
    class Info:
        size = 32


#16位立即数全已知的编码
class adv32ftoken_16imm(adv32f16tokens):
    opcode0 = bit_range(0,8)
    opcode1 = bit_range(8,16)

