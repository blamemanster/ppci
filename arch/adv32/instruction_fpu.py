from .tokens_fpu import * 
from copyreg import constructor
from .registers import *
from .loc_mode import loc_mode1
from ..isa import Relocation, Isa
from ..encoding import Instruction, Operand, Syntax, Constructor, Transform
isa_fpu = Isa()

class adv32fpuInstruction(Instruction):
    isa = isa_fpu
    

class adv32fpuIns_16imm(adv32fpuInstruction):
    tokens = [adv32ftoken_16imm]
def make_16imm_instruction(name, opcode0):
    patterns = {"opcode0":opcode0, "opcode1":0b11100101,}
    syntax = Syntax([name])
    members = { "syntax":syntax, "patterns":patterns, }
    return type(name.title(), (adv32fpuIns_16imm,), members)

vclrovfi = make_16imm_instruction("vclrovfi", 0b00001011)
vclrovfr = make_16imm_instruction("vclrovfr", 0b00001011)
vrndoff = make_16imm_instruction("vrndoff", 0b00001001)
vrndon = make_16imm_instruction("vrndon", 0b00001000)
vsatoff = make_16imm_instruction("vsatoff", 0b00000111)
vsaton = make_16imm_instruction("vsaton", 0b00000110)


