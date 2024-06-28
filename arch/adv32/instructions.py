#Description of instructions 
from copyreg import constructor
from lib2to3.pgen2 import token
from lib2to3.pgen2.token import OP
from re import A, X
import re
from sys import flags
from unittest import case
from ..stack import StackLocation, FramePointerLocation,Frame
from ..encoding import Instruction, Operand, Syntax, Constructor, Transform
from ..generic_instructions import Alignment, ArtificialInstruction
from ..generic_instructions import RegisterUseDef, Global
from ..isa import Relocation, Isa
from ..token import Token, bit_range, bit
from .registers import *
from ...utils.bitfun import align
from ...utils.bitfun import encode_imm32, align, wrap_negative
from ..arch_info import Endianness
from .loc_mode import loc_mode1
from .relocation import Rel32Relocation,Abs32Relocation
from .tokens import * 
#---------------------------------------------------------------------------------------------------------------#
class adv32Instruction(Instruction):
    isa = isa
#---------------------------------------------------------------------------------------------------------------#
########## 操作数的内存片段定义  #####################
class NEQ(Constructor):
    syntax = Syntax(["neq"])
    patterns = { "cond":0x0 }

class EQ(Constructor):
    syntax = Syntax(["eq"])
    patterns = { "cond":0x1 }
    
class GT(Constructor):
    syntax = Syntax(["gt"])
    patterns = { "cond":0x2 }

class GEQ(Constructor):
    syntax = Syntax(["geq"])
    patterns = { "cond":0x3 }

class LT(Constructor):
    syntax = Syntax(["lt"])
    patterns = { "cond":0x4 }

class LEQ(Constructor):
    syntax = Syntax(["leq"])
    patterns = { "cond":0x5 }

class HI(Constructor):
    syntax = Syntax(["hi"])
    patterns = { "cond":0x6 }

class HIS(Constructor):
    syntax = Syntax(["his"])
    patterns = { "cond":0x7 }

class C(Constructor):
    syntax = Syntax(["c"])
    patterns = { "cond":0x7 }

class LO(Constructor):
    syntax = Syntax(["lo"])
    patterns = { "cond":0x8 }

class NC(Constructor):
    syntax = Syntax(["nc"])
    patterns = { "cond":0x8 }

class LOS(Constructor):
    syntax = Syntax(["los"])
    patterns = { "cond":0x9 }

class NOV(Constructor):
    syntax = Syntax(["nov"])
    patterns = { "cond":0xa }

class OV(Constructor):
    syntax = Syntax(["ov"])
    patterns = { "cond":0xb }

class NTC(Constructor):
    syntax = Syntax(["ntc"])
    patterns = { "cond":0xc }

class TC(Constructor):
    syntax = Syntax(["tc"])
    patterns = { "cond":0xd }

class NBIO(Constructor):
    syntax = Syntax(["nbio"])
    patterns = { "cond":0xe }

class UNC(Constructor):
    syntax = Syntax(["unc"])
    patterns = { "cond":0xf }

cond_mode = (NEQ,EQ,GT,GEQ,LT,LEQ,HI,HIS,C,LO,NC,LOS,NOV,OV,NTC,TC,NBIO,UNC)

#---------------------------------------------------------------------------------------------------------------#
#32位token
###############测试
class ffc89(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['ffc'," ",'xar7',',',int22])
    patterns = { "opcode0":0b0000000011,"int22":int22 }


class mov155(adv32Instruction):
    tokens = [Token4]
    imm = Operand("imm", int)
    loc16 = Operand("loc16", loc_mode1)
    syntax = Syntax(['mov'," ",'acc', ',', loc16, '<<', imm])
    patterns = { "opcode0":0x56030,"imm":imm }

###########################
class add21(adv32Instruction):
    tokens = [Token1]
    int16 = Operand("int16",int)
    shft = Operand("shft",int)
    syntax = Syntax(['add'," ","acc",',',int16,'<<',shft])
    patterns = { "opcode0":0b111111110001,"shft":shft,"int16":int16 }

class mov152(adv32Instruction):
    tokens = [Token1]
    int16 = Operand("int16",int)
    shft = Operand("shft",int)
    syntax = Syntax(['mov'," ",'acc',',',int16,'<<',shft])
    patterns = { "opcode0":0b111111110010,"shft":shft,"int16":int16 }

class mov172(adv32Instruction):
    tokens = [Token2]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['mov'," ",'ovc',',',loc16])
    patterns = { "opcode0":0x560200 }

class add22(adv32Instruction):
    tokens = [Token2]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['add'," ",'acc',',',loc16,'<<','t'])
    patterns = { "opcode0":0b010101100010001100000000 }

class addl39(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['addl'," ",loc32,',','acc'])
    patterns = { "opcode0":0b010101100000000100000000 }

class addul41(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['addul'," ",'p',',',loc32])
    patterns = { "opcode0":0b010101100101011100000000 }

class imacl93(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['imacl'," ",'p',',',loc32,',','*','xar7'])
    patterns = { "opcode0":0b010101100100110111000111 }


class imacl94(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['imacl'," ",'p',',',loc32,',','*','xar7','+','+'])
    patterns = { "opcode0":0b010101100100110110000111 }

class impyal95(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['impyal'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100100110000000000 }

class impyl96(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['impyl'," ",'acc',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100100010000000000 }

class impyl97(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['impyl'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100000010100000000 }

class impysl98(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['impysl'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100100001100000000 }

class impyxul99(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['impyxul'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100110010100000000 }

class mac140(adv32Instruction):
    tokens = [Token2]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['mac'," ",'p',',',loc16,',','*','xar7'])
    patterns = { "opcode0":0b010101100000011111000111 }

class mac141(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['mac'," ",'p',',',loc16,',','*','xar7','+','+'])
    patterns = { "opcode0":0b010101100000011110000111 }

class max142(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['max'," ",'al',',',loc16])
    patterns = { "opcode0":0b010101100111001000000000 }

class max143(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['max'," ",'ah',',',loc16])
    patterns = { "opcode0":0b010101100111001100000000 }

class maxcul144(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['maxcul'," ",'p',',',loc32])
    patterns = { "opcode0":0b010101100101000100000000 }

class maxl145(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['maxl'," ",'acc',',',loc32])
    patterns = { "opcode0":0b010101100110000100000000 }

class min146(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['min'," ",'al',',',loc16])
    patterns = { "opcode0":0b010101100111010000000000 }

class min147(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['min'," ",'ah',',',loc16])
    patterns = { "opcode0":0b010101100111010100000000 }

class minl148(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['minl'," ",'acc',',',loc32])
    patterns = { "opcode0":0b010101100101000000000000 }

class mov153(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['mov'," ",'acc',',',loc16,'<<','t'])
    patterns = { "opcode0":0b010101100111011000000000 }

class movu234(adv32Instruction):
    tokens = [Token2]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['movu'," ",loc16,',','ovc'])
    patterns = { "opcode0":0b010101100010100000000000 }

class movu235(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc = Operand("loc",loc_mode1)
    
    syntax = Syntax(['movu'," ",'ovc',',',loc])
    patterns = { "opcode0":0b010101100110001000000000 }

class zalr254(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['zalr'," ",'acc',',',loc16])
    patterns = { "opcode0":0b010101100001001100000000 }

class xpwrite256(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['xpwrite'," ",'*','al',',',loc16])
    patterns = { "opcode0":0b010101100011110100000000 }

class xpread257(adv32Instruction):
    tokens = [Token2]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['xpread'," ",loc16,',','*','al'])
    patterns = { "opcode0":0b010101100011110000000000 }

class tbit292(adv32Instruction):
    tokens = [Token2]
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['tbit'," ",loc16,',','t'])
    patterns = { "opcode0":0b010101100010010100000000 }


class subul294(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['subul'," ",'p',',',loc16])
    patterns = { "opcode0":0b010101100101110100000000 }

class subul295(adv32Instruction):
    tokens = [Token2]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['subul'," ",'acc',',',loc32])
    patterns = { "opcode0":0b010101100101010100000000 }

class subrl297(adv32Instruction):
    tokens = [Token2]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['subrl'," ",loc32,',','acc'])
    patterns = { "opcode0":0b010101100100100100000000 }

class subl300(adv32Instruction):
    tokens = [Token2]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['subl'," ",loc32,',','acc'])
    patterns = { "opcode0":0b010101100100000100000000 }

class subcul302(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['subcul'," ",'acc',',',loc32])
    patterns = { "opcode0":0b010101100001011100000000 }

class subbl304(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['subbl'," ",'acc',',',loc32])
    patterns = { "opcode0":0b010101100101010000000000 }

class sub313(adv32Instruction):
    tokens = [Token2]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['sub'," ",'acc',',',loc16,'<<','t'])
    patterns = { "opcode0":0b010101100010011100000000 }

class sqra314(adv32Instruction):
    tokens = [Token2]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['sqra'," ",loc16])
    patterns = { "opcode0":0b010101100001010100000000 }

class ror340(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['ror'," ",'acc'])
    patterns = { "opcode0":0b1111111101010010 }

class qmpyxul341(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmpyxul'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100100001000000000 }

class qmpyul342(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmpyul'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100100011100000000 }

class qmpysl343(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmpysl'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100100010100000000 }

class qmpyl344(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmpyl'," ",'acc',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100110001100000000 }

class qmpyl345(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmpyl'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100110011100000000 }

class qmpyal346(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmpyal'," ",'p',',','xt',',',loc32])
    patterns = { "opcode0":0b010101100100011000000000 }

class qmacl347(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmacl'," ",'p',',',loc32,',','*','xar7'])
    patterns = { "opcode0":0b010101100100111111000111 }

class qmacl348(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['qmacl'," ",'p',',',loc32,',','*','xar7','+','+'])
    patterns = { "opcode0":0b010101100100111110000111 }

class dmac431(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['dmac'," ",'acc',':','p',',',loc32,',','*','xar7'])
    patterns = { "opcode0":0b010101100100101111000111}  

class dmac432(adv32Instruction):
    tokens = [Token2]
    loc32 = Operand("loc32",loc_mode1)

    syntax = Syntax(['dmac'," ",'acc',':','p',',',loc32,',','*','xar7','+','+'])
    patterns = { "opcode0":0b010101100100101110000111}  

class mov438(adv32Instruction):
    tokens = [Token2]
    
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['mov'," ",loc16,',','acc','<<','shft1'])
    patterns = { "opcode0":0b10110001}

class mov440(adv32Instruction):
    tokens = [Token2]
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",loc16,',','ovc'])
    patterns = { "opcode0":0x562900 }

class add24(adv32Instruction):
    tokens = [Token4]
    loc16 = Operand("loc16",loc_mode1)
    shft = Operand("shft",int)
    syntax = Syntax(['add'," ",'acc',',',loc16,',',shft])
    patterns = { "opcode0":0x56000,"shft":shft }


class add31(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['add'," ",loc16,',',int16])
    patterns = { "opcode0":0b00001000,"int16":int16 }

class and46(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['and'," ",'al',',',loc16,',',int16])
    patterns = { "opcode0":0b11001100,"int16":int16 }


class and47(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['and'," ",'ah',',',loc16,',',int16])
    patterns = { "opcode0":0b11001101,"int16":int16 }

class and54(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['and'," ",loc16,',',int16])
    patterns = { "opcode0":0b00011000,"int16":int16 }

class cmp82(adv32Instruction):
    tokens = [Token6]
    
    loc16 = Operand("loc16",loc_mode1)
    
    int16 = Operand("int16",int)
    
    syntax = Syntax(['cmp'," ",loc16,',',int16])
    patterns = { "opcode0":0b00011011,"int16":int16 }

class loopnz125(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['loopnz'," ",loc16,',',int16])
    patterns = { "opcode0":0b00101110,"int16":int16 }

class loopz126(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['loopz'," ",loc16,',',int16])
    patterns = { "opcode0":0b00101100,"int16":int16 }

class mov149(adv32Instruction):
    tokens = [Token6]
    int16 = Operand("int16",int)
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['mov'," ","*","(",int16,")",',',loc16])
    patterns = { "opcode0":0b11110100,"int16":int16 }

class mov161(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['mov'," ",loc16,',',int16])
    patterns = { "opcode0":0b00101000,"int16":int16 }

class mov162(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    zero = Operand("zero",int)
    syntax = Syntax(['mov'," ",loc16,',','*','(',zero,':',int16,')'])
    patterns = { "opcode0":0b11110101,"int16":int16 }

class mpy241(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['mpy'," ",'acc',',',loc16,',',int16])
    patterns = { "opcode0":0b00110100,"int16":int16 }

class mpy243(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['mpy'," ",'p',',',loc16,',',int16])
    patterns = { "opcode0":0b10001100,"int16":int16 }


class mpya245(adv32Instruction):
    tokens = [Token6]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['mpya'," ",'p',',',loc16,',',int16])
    patterns = { "opcode0":0b00010101,"int16":int16 }

class and43(adv32Instruction):
    tokens = [Token10]
    int16 = Operand("int16",int)
    int4 = Operand("int4",int)
    syntax = Syntax(['and'," ",'acc',',',int16,'<<',int4])
    patterns = { "opcode0":0b001111100000,"int4":int4,"int16":int16 }

class xor266(adv32Instruction):
    tokens = [Token10]
    int16 = Operand("int16",int)
    int4 = Operand("int4",int)
    syntax = Syntax(['xor'," ",'acc',',',int16,'<<',int4])
    patterns = { "opcode0":0b001111100010,"int4":int4,"int16":int16 }

class sub312(adv32Instruction):
    tokens = [Token10]
    int16 = Operand("int16",int)
    int4 = Operand("int4",int)
    syntax = Syntax(['sub'," ",'acc',',',int16,'<<',int4])
    patterns = { "opcode0":0b111111110000,"int4":int4,"int16":int16 }


class and44(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['and'," ",'acc',',',int16,"<<16"])
    patterns = { "opcode0":0b0101011000001000,"int16":int16 }

class and48(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['and'," ",'ier',',',int16])
    patterns = { "opcode0":0b0111011000100110,"int16":int16 }

class and49(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['and'," ",'ifr',',',int16])
    patterns = { "opcode0":0b0111011000101111,"int16":int16 }

class iack92(adv32Instruction):
    tokens = [Token11]
    
    int16 = Operand("int16",int)
    
    syntax = Syntax(['iack'," ",int16])
    patterns = { "opcode0":0b0111011000111111,"int16":int16 }

class movw236(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['movw'," ",'dp',',',int16])
    patterns = { "opcode0":0b0111011000011111,"int16":int16 }


class xor267(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['xor'," ",'acc',',',int16])
    patterns = { "opcode0":0b0101011001001110,"int16":int16 }

class or1008(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['or'," ","al",",",int16])
    patterns = { "opcode0":0x1aa9,"int16":int16}

class mov1009(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['mov'," ","acc",",",int16])
    patterns = { "opcode0":0xff20,"int16":int16}

class mov1010(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['mov'," ","al",",",int16])
    patterns = { "opcode0":0x28a9,"int16":int16}

class mov1015(adv32Instruction):
    tokens = [Token11]    
    int16 = Operand("int16",int) 
    syntax = Syntax(['mov'," ","sp",",",int16])
    patterns = { "opcode0":0x28ad,"int16":int16}

class mov1016(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)
    syntax = Syntax(['mov'," ","ah",",",int16])
    patterns = { "opcode0":0x28a8,"int16":int16}

class mov1024(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)  
    syntax = Syntax(['mov'," ","pl",",",int16])
    patterns = { "opcode0":0x28ab,"int16":int16}

class mov1025(adv32Instruction):
    tokens = [Token11]
    int16 = Operand("int16",int)   
    syntax = Syntax(['mov'," ","ph",",",int16])
    patterns = { "opcode0":0x28aa,"int16":int16}

class b62(adv32Instruction):
    tokens = [Token13]
    int16 = Operand("int16",int)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['b'," ", int16 ,',',cond])
    patterns = { "opcode0":0b111111111110,"int16":int16 }
    def gen_relocations(self):
        yield Rel32Relocation(self.int16)

class bf66(adv32Instruction):
    tokens = [Token13]
    
    int16 = Operand("int16",int)
    
    cond = Operand("cond",cond_mode)
    
    syntax = Syntax(['bf'," ",int16,',',cond])
    patterns = { "opcode0":0b010101101100,"int16":int16 }

class bar64(adv32Instruction):
    tokens = [Token14]
    int16 = Operand("int16",int)
    arn = Operand("arn",ARNRegisters_n_to_m,write = True)
    arm = Operand("arm",ARNRegisters_n_to_m,write = True)
    syntax = Syntax(['bar'," ",int16,',',arn,',',arm,',',"eq"])
    patterns = { "opcode0":0b1000111110,"arn":arn,"arm":arm,"int16":int16 }

class bar65(adv32Instruction):
    tokens = [Token14]
    int16 = Operand("int16",int)
    arn = Operand("arn",ARNRegisters_n_to_m,write = True)
    arm = Operand("arm",ARNRegisters_n_to_m,write = True)
    syntax = Syntax(['bar'," ",int16,',',arn,',',arm,',','neq'])
    patterns = { "opcode0":0b1000111111,"arn":arn,"arm":arm,"int16":int16 }


class lb120(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['lb'," ",int22])
    patterns = { "opcode0":0b0000000001,"int22":int22 }

class lc122(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['lc'," ",int22])
    patterns = { "opcode0":0b0000000010,"int22":int22 }

class lcr125(adv32Instruction):
    tokens = [Token51] 
    syntax = Syntax(['lcr'," ",'abort'])
    patterns = { "opcode0":0x76409056}

class lcr126(adv32Instruction):
    tokens = [Token51] 
    syntax = Syntax(['lcr'," ",'memcpy'])
    patterns = { "opcode0":0x764090a3}

class lcr127(adv32Instruction):
    tokens = [Token51] 
    syntax = Syntax(['lcr'," ",'_args_main'])
    patterns = { "opcode0":0x764090c0}

class lcr128(adv32Instruction):
    tokens = [Token51] 
    syntax = Syntax(['lcr'," ",'exit'])
    patterns = { "opcode0":0x76409058}

class lcr123(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['lcr'," ",int22])
    patterns = { "opcode0":0b0111011001,"int22":int22 }

class movl222(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar0',',',int22])
    patterns = { "opcode0":0b1000110100,"int22":int22 }

class movl223(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar1',',',int22])
    patterns = { "opcode0":0b1000110101,"int22":int22 }

class movl224(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar2',',',int22])
    patterns = { "opcode0":0b1000110110,"int22":int22 }

class movl225(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar3',',',int22])
    patterns = { "opcode0":0b1000110111,"int22":int22 }

class movl226(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar4',',',int22])
    patterns = { "opcode0":0b1000111100,"int22":int22 }

class movl227(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar5',',',int22])
    patterns = { "opcode0":0b1000111101,"int22":int22 }

class movl228(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar6',',',int22])
    patterns = { "opcode0":0b0111011010,"int22":int22 }

class movl229(adv32Instruction):
    tokens = [Token15]
    int22 = Operand("int22",int)
    syntax = Syntax(['movl'," ",'xar7',',',int22])
    patterns = { "opcode0":0b0111011011,"int22":int22 }

class mac139(adv32Instruction):
    tokens = [Token18]
    zero = Operand("zero",int)
    loc16 = Operand("loc16",loc_mode1)
    pma = Operand("pma",int)
    syntax = Syntax(['mac'," ",'p',',',loc16,',',zero,':',pma])
    patterns = { "opcode0":0b00010100,"pma":pma }

class xmacd269(adv32Instruction):
    tokens = [Token18]
    loc16 = Operand("loc16",loc_mode1)
    pma = Operand("pma",int)
    syntax = Syntax(['xmacd'," ",'p',',',loc16,',','*','(',pma,')'])
    patterns = { "opcode0":0b10100100,"pma":pma }

class xmac270(adv32Instruction):
    tokens = [Token18]
    loc16 = Operand("loc16",loc_mode1)
    pma = Operand("pma",int)
    syntax = Syntax(['xmac'," ",'p',',',loc16,',','*','(',pma,')'])
    patterns = { "opcode0":0b10000100,"pma":pma }

class mov167(adv32Instruction):
    tokens = [Token21]
    loc16 = Operand("loc16",loc_mode1)
    cond = Operand("cond",int)
    syntax = Syntax(['mov'," ",loc16,',','al',',',cond])
    patterns = { "opcode0":0b01010110001010100000,"cond":cond }

class mov168(adv32Instruction):
    tokens = [Token21]
    loc16 = Operand("loc16",loc_mode1)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['mov'," ",loc16,',','ah',',',cond])
    patterns = { "opcode0":0b01010110001010110000}

class movl201(adv32Instruction):
    tokens = [Token21]
    loc32 = Operand("loc32",loc_mode1)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['movl'," ",loc32,',','acc',',',cond])
    patterns = { "opcode0":0b01010110010010000000, }

class mov189(adv32Instruction):
    tokens = [Token24]
    loc16 = Operand("loc16",loc_mode1)
    int8 = Operand("int8",int)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['movb'," ",loc16,',',int8,',',cond])
    patterns = { "opcode0":0x56b,"int8":int8 }

class movb190(adv32Instruction):
    tokens = [Token25]
    loc16 = Operand("loc16",loc_mode1)
    allsb = Operand("allsb",AXRegisters,write = True)
    syntax = Syntax(['movb'," ",loc16,',',allsb])
    patterns = { "opcode0":0b0011110,"allsb":allsb }

class movh197(adv32Instruction):
    tokens = [Token28]
    loc16 = Operand("loc16",loc_mode1)
    shf = Operand("shf",int)
    syntax = Syntax(['movh'," ",loc16,',','acc',',',shf])
    patterns = { "opcode0":0b010101100010111100000,"shf":shf }

class xpread258(adv32Instruction):
    tokens = [Token30]
    loc16 = Operand("loc16",loc_mode1)
    pma = Operand("pma",int)
    syntax = Syntax(['xpread'," ",loc16,',','*','(',pma,')'])
    patterns = { "opcode0":0b10101100,"pma":pma }

class xcall271(adv32Instruction):
    tokens = [Token31]
    pma = Operand("pma",int)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['xcall'," ",pma,',',cond])
    patterns = { "opcode0":0b010101101110,"pma":pma }

class xb284(adv32Instruction):
    tokens = [Token31]
    pma = Operand("pma",int)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['xb'," ",pma,',',cond])
    patterns = { "opcode0":0b010101101101,"pma":pma }

class banz63(adv32Instruction):
    tokens = [Token32]
    int16 = Operand("int16",int)
    arn = Operand("arn",ARNRegisters_n_to_m,write = True)
    syntax = Syntax(['banz'," ",int16,',',arn,'-','-'])
    patterns = { "opcode0":0b0000000000001,"xarn":arn,"pma":int16 }

class xcall272(adv32Instruction):
    tokens = [Token32]
    pma = Operand("pma",int)
    xarn = Operand("xarn",ARPNRegisters,write = True)
    syntax = Syntax(['xcall'," ",pma,',','*',',',xarn])
    patterns = { "opcode0":0b0011111001101,"xarn":xarn,"pma":pma }

class xbanz274(adv32Instruction):
    tokens = [Token33]
    pma = Operand("pma",int)
    syntax = Syntax(['xbanz'," ",pma,',','*'])
    patterns = { "opcode0":0b0101011000001100,"pma":pma }

class xbanz275(adv32Instruction):
    tokens = [Token33]
    pma = Operand("pma",int)
    syntax = Syntax(['xbanz'," ",pma,',','*','+','+'])
    patterns = { "opcode0":0b0101011000001010,"pma":pma }

class xbanz276(adv32Instruction):
    tokens = [Token33]
    pma = Operand("pma",int)
    syntax = Syntax(['xbanz'," ",pma,',','*','-','-'])
    patterns = { "opcode0":0b0101011000001011,"pma":pma }

class xbanz277(adv32Instruction):
    tokens = [Token33]
    pma = Operand("pma",int)
    zero = Operand("zero",int)
    syntax = Syntax(['xbanz'," ",pma,',','*',zero,'+','+'])
    patterns = { "opcode0":0b0101011000001110,"pma":pma }

class xbanz278(adv32Instruction):
    tokens = [Token33]
    pma = Operand("pma",int)
    zero = Operand("zero",int)
    syntax = Syntax(['xbanz'," ",pma,',','*',zero,'-','-'])
    patterns = { "opcode0":0b0101011000001111,"pma":pma }

class xbanz279(adv32Instruction):
    tokens = [Token34]
    pma = Operand("pma",int)
    arpn = Operand("arpn",ARNRegisters,write = True)
    syntax = Syntax(['xbanz'," ",pma,',','*',',',arpn])
    patterns = { "opcode0":0b0011111000110,"arpn":arpn,"pma":pma }

class xbanz280(adv32Instruction):
    tokens = [Token34]
    pma = Operand("pma",int)
    arpn = Operand("arpn",ARPNRegisters,write = True)
    syntax = Syntax(['xbanz'," ",pma,',','*','+','+',',',arpn])
    patterns = { "opcode0":0b0011111000111,"arpn":arpn,"pma":pma }

class xbanz281(adv32Instruction):
    tokens = [Token34]
    pma = Operand("pma",int)
    arpn = Operand("arpn",ARPNRegisters,write = True)
    syntax = Syntax(['xbanz'," ",pma,',','*','-','-',',',arpn])
    patterns = { "opcode0":0b0011111001000,"arpn":arpn,"pma":pma }

class xbanz282(adv32Instruction):
    tokens = [Token34]
    pma = Operand("pma",int)
    arpn = Operand("arpn",ARPNRegisters,write = True)
    zero = Operand("zero",int)
    syntax = Syntax(['xbanz'," ",pma,',','*',zero,'+','+',',',arpn])
    patterns = { "opcode0":0b0011111001001,"arpn":arpn,"pma":pma }

class xbanz283(adv32Instruction):
    tokens = [Token34]
    pma = Operand("pma",int) 
    arpn = Operand("arpn",ARPNRegisters,write = True)
    zero = Operand("zero",int)
    syntax = Syntax(['xbanz'," ",pma,',','*',zero,'-','-',',',arpn])
    patterns = { "opcode0":0b0011111001010,"arpn":arpn,"pma":pma }

class xb285(adv32Instruction):
    tokens = [Token34]
    pma = Operand("pma",int)
    arpn = Operand("arpn",ARPNRegisters,write = True)
    syntax = Syntax(['xb'," ",pma,',','*',',',arpn])
    patterns = { "opcode0":0b0011111001110,"arpn":arpn,"pma":pma }

class uout287(adv32Instruction):
    tokens = [Token35]
    pa = Operand("pa",int)
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['uout'," ","*","(",pa,")",',',loc16])
    patterns = { "opcode0":0b10110000,"PA":pa }


class in433(adv32Instruction):
    tokens = [Token35]
    loc16 = Operand("loc16",loc_mode1)
    pa = Operand("pa",int)
    syntax = Syntax(['in'," ",loc16,',','*','(',pa,')'])
    patterns = { "opcode0":0b10110100,'PA':pa}


class tset288(adv32Instruction):
    tokens = [Token36]
    bit16 = Operand("bit16",int)
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['tset'," ",loc16,',',bit16])
    patterns = { "opcode0":0b01010110000011010000,"bit16":bit16 }

class tclr291(adv32Instruction):
    tokens = [Token38]
    loc16 = Operand("loc16",loc_mode1)
    int4 = Operand("int4",int)
    syntax = Syntax(['tclr'," ",loc16,',',int4])
    patterns = { "opcode0":0b01010110000010010000,"int4":int4 }

class sub454(adv32Instruction):
    tokens = [Token38]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)

    syntax = Syntax(['sub'," ","acc",',',loc16,'<<',int16])
    patterns = { "opcode0":0b01010110000000000000}

class out399(adv32Instruction):
    tokens = [Token44]
    PA = Operand("PA",int)
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['out'," ",'*','(',PA,')',',',loc16])
    patterns = { "opcode0":0b10111100,"PA":PA }

class or404(adv32Instruction):
    tokens = [Token45]
    loc16 = Operand("loc16",loc_mode1)
    int16 = Operand("int16",int)
    syntax = Syntax(['or'," ",loc16,',',int16])
    patterns = { "opcode0":0b00011010,"int16":int16 }

class or405(adv32Instruction):
    tokens = [Token46]
    int16 = Operand("int16",int)
    syntax = Syntax(['or'," ",'ifr',',',int16])
    patterns = { "opcode0":0b0111011000100111,"int16":int16 }

class or406(adv32Instruction):
    tokens = [Token46]
    int16 = Operand("int16",int)
    syntax = Syntax(['or'," ",'ier',',',int16])
    patterns = { "opcode0":0b0111011000100011,"int16":int16 }

class or410(adv32Instruction):
    tokens = [Token46]
    int16 = Operand("int16",int)
    syntax = Syntax(['or'," ",'acc',',',int16,'<<','shft16'])
    patterns = { "opcode0":0b0011011001001010,"int16":int16 }

class or409(adv32Instruction):
    tokens = [Token47]
    int16 = Operand("int16",int)
    shft = Operand("shft",int)
    syntax = Syntax(['or'," ",'acc',',',int16,'<<',shft])
    patterns = { "opcode0":0b001111100001,"shft":shft,"int16":int16 }

class mov439(adv32Instruction):
    tokens = [Token49]
    
    loc16 = Operand("loc16",loc_mode1)
    shf = Operand("shf",int)
    syntax = Syntax(['mov'," ",loc16,',','acc','<<',shf])
    patterns = { "opcode0":0b10110001,"shf":shf}

class MOV321001(adv32Instruction):
    tokens = [Token51]
    syntax = Syntax(['mov32'," ",'*',"sp","+","+",",","stf"])
    patterns = { "opcode0":0xe20000bd}

# class mov1029(adv32Instruction):
#     tokens = [Token51]     
#     syntax = Syntax(['mov'," ","acc",",","ar1","<<","shft3"])
#     patterns = { "opcode0":0x560303a1}

# class mov1030(adv32Instruction):
#     tokens = [Token51]     
#     syntax = Syntax(['mov'," ","acc",",","ar1","<<","shft3"])
#     patterns = { "opcode0":0x560303a1}

class setflg1(adv32Instruction):
    tokens = [Token51]
    syntax = Syntax(['setflg'," ","RNDF32=1",",","RNDF64=1"])
    patterns = { "opcode0":0xe6300600}

class setflg2(adv32Instruction):
    tokens = [Token51]
    syntax = Syntax(['setflg'," ","RNDF32=1"])
    patterns = { "opcode0":0xe6100200}





#-------------------------------------------------------------------------
#16位token
class aborti0(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['aborti'," ",])
    patterns = { "opcode0":0b0000000000000001 }

# class add23(adv32Instruction):
#     tokens = [Token3]
#     loc16 = Operand("loc16",loc_mode1)
#     syntax = Syntax(['add'," ",'acc',',',loc16])
#     patterns = { "opcode0":0b10000001 }


class lretr1(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['lretr'," ",])
    patterns = { "opcode0":0b0000000000000110 }

class cmpr2(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['cmpr2'," "])
    patterns = { "opcode0":0b0101011000011000 }

class cmpr3(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['cmpr1'," "])
    patterns = { "opcode0":0b0101011000011001 }

class cmpr4(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['cmpr3'," "])
    patterns = { "opcode0":0b0101011000011100 }

class cmpr5(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['cmpr0'," "])
    patterns = { "opcode0":0b0101011000011101 }

class lpaddr6(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['lpaddr'," ",])
    patterns = { "opcode0":0b0101011000011110 }

class iret7(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['iret'," ",])
    patterns = { "opcode0":0b0111011000000010 }

class lrete8(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['lrete'," ",])
    patterns = { "opcode0":0b0111011000010000 }

class lret9(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['lret'," ",])
    patterns = { "opcode0":0b0111011000010100 }

class edis10(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['edis'," ",])
    patterns = { "opcode0":0b0111011000011010 }

class asp11(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['asp'," ",])
    patterns = { "opcode0":0b0111011000011011 }

class idle12(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['idle'," ",])
    patterns = { "opcode0":0b0111011000100001 }

class eallow13(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['eallow'," ",])
    patterns = { "opcode0":0b0111011000100010 }

class estop114(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['estop1'," ",])
    patterns = { "opcode0":0b0111011000100100 }

class estop015(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['estop0'," ",])
    patterns = { "opcode0":0b0111011000100101 }

class zapa16(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['zapa'," ",])
    patterns = { "opcode0":0b0101011000110011 }

class xret17(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['xret'," ",])
    patterns = { "opcode0":0b0101011011111111 }

class nasp18(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['nasp'," ",])
    patterns = { "opcode0":0b0111011000010111 }

class abs19(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['abs'," ",'acc'])
    patterns = { "opcode0":0b1111111101010110 }

class abstc20(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['abstc'," ",'acc'])
    patterns = { "opcode0":0b0101011001011111 }







class add25(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['add'," ",'acc',',',loc16])
    patterns = { "opcode0":0b00000101 }

class add26(adv32Instruction):
    tokens = [Token5]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    shft = Operand("shft",int)
    
    syntax = Syntax(['add'," ",'acc',',',loc16,'<<',shft])
    patterns = { "opcode0":0b1010,"shft":shft }

class add27(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['add'," ",'al',',',loc16])
    patterns = { "opcode0":0b10010100 }

class add28(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['add'," ",'ah',',',loc16])
    patterns = { "opcode0":0b10010101 }

class add29(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['add'," ",loc16,',','al'])
    patterns = { "opcode0":0b01110010 }

class add30(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['add'," ",loc16,',','ah'])
    patterns = { "opcode0":0b01110011 }



class addb32(adv32Instruction):
    tokens = [Token7]
    int8 = Operand("int8",int)
    syntax = Syntax(['addb'," ",'acc',',',int8])
    patterns = { "opcode0":0b00001001,"int8":int8 }

class addb33(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['addb'," ",'al',',',int8])
    patterns = { "opcode0":0b10011100,"int8":int8 }

class addb34(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['addb'," ",'ah',',',int8])
    patterns = { "opcode0":0b10011101,"int8":int8 }

class addb35(adv32Instruction):
    tokens = [Token8]
    
    
    
    int7 = Operand("int7",int)
    
    syntax = Syntax(['addb'," ",'sp',',',int7])
    patterns = { "opcode0":0b111111100,"int7":int7 }

class addb36(adv32Instruction):
    tokens = [Token9]
    
    xarn = Operand("xarn",XARnRegisters,write = True)
    
    int7 = Operand("int7",int)
    
    syntax = Syntax(['addb'," ",xarn,',',int7])
    patterns = { "opcode0":0b11011,"xarn":xarn,"opcode2":0b0,"int7":int7 }

class addcu37(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['addcu'," ",'acc',',',loc16])
    patterns = { "opcode0":0b00001100 }

class addl38(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['addl'," ",'acc',',',loc32])
    patterns = { "opcode0":0b00000111 }



class addu40(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['addu'," ",'acc',',',loc16])
    patterns = { "opcode0":0b00001101 }



class adrk42(adv32Instruction):
    tokens = [Token0]
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['adrk'," ",int8])
    patterns = { "opcode0":0b1111110011111111 }




class and45(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['and'," ",'acc',',',loc16])
    patterns = { "opcode0":0b10001001 }


class and50(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['and'," ",loc16,',','al'])
    patterns = { "opcode0":0b11000000 }

class and51(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['and'," ",loc16,',','ah'])
    patterns = { "opcode0":0b11000001 }

class and52(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['and'," ",'al',',',loc16])
    patterns = { "opcode0":0b11001110 }

class and53(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['and'," ",'ah',',',loc16])
    patterns = { "opcode0":0b11001111 }



class andb55(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['andb'," ",'al',',',int8])
    patterns = { "opcode0":0b10010000,"int8":int8 }

class andb56(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['andb'," ",'ah',',',int8])
    patterns = { "opcode0":0b10010001,"int8":int8 }

class asr57(adv32Instruction):
    tokens = [Token12]
    
    
    
    shft = Operand("shft",int)
    
    syntax = Syntax(['asr'," ",'al',',',shft])
    patterns = { "opcode0":0b111111111010,"shft":shft }

class asr58(adv32Instruction):
    tokens = [Token12]
    
    
    
    shft = Operand("shft",int)
    
    syntax = Syntax(['asr'," ",'ah',',',shft])
    patterns = { "opcode0":0b111111111011,"shft":shft }

class asr59(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['asr'," ",'al',',','t'])
    patterns = { "opcode0":0b1111111101100100 }

class asr60(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['asr'," ",'ah',',','t'])
    patterns = { "opcode0":0b1111111101100101 }

class asrl61(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['asrl'," ",'acc',',','t'])
    patterns = { "opcode0":0b0101011000010000 }








class clrc67(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'amode'])
    patterns = { "opcode0":0b0101011000010110 }

class clrc68(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'m0m1map'])
    patterns = { "opcode0":0b0101011000111111 }

class clrc69(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'objmode'])
    patterns = { "opcode0":0b0101011000110110 }

class clrc70(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'ovc'])
    patterns = { "opcode0":0b0101011001011100 }

class clrc71(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'xf'])
    patterns = { "opcode0":0b0101011000011011 }

class clrc72(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'sxm'])
    patterns = { "opcode0":0b0010100100000001 }

class clrc73(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'ovm'])
    patterns = { "opcode0":0b0010100100000010 }

class clrc74(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'tc'])
    patterns = { "opcode0":0b0010100100000100 }

class clrc75(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'c'])
    patterns = { "opcode0":0b0010100100001000 }

class clrc76(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'intm'])
    patterns = { "opcode0":0b0010100100010000 }

class clrc77(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'dbgm'])
    patterns = { "opcode0":0b0010100100100000 }

class clrc78(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'page0'])
    patterns = { "opcode0":0b0010100101000000 }

class clrc79(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['clrc'," ",'vmap'])
    patterns = { "opcode0":0b0010100110000001 }

class cmp80(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['cmp'," ",'al',',',loc16])
    patterns = { "opcode0":0b01010100 }

class cmp81(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['cmp'," ",'ah',',',loc16])
    patterns = { "opcode0":0b01010101 }



class cmpb83(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['cmpb'," ",'al',',',int8])
    patterns = { "opcode0":0b01010010,"int8":int8 }

class cmpb84(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['cmpb'," ",'ah',',',int8])
    patterns = { "opcode0":0b01010011,"int8":int8 }

class cmpl85(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['cmpl'," ",'acc',',',loc32])
    patterns = { "opcode0":0b00001111 }

class csb86(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['csb'," ",'acc'])
    patterns = { "opcode0":0b0101011000110101 }

class dec87(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['dec'," ",loc16])
    patterns = { "opcode0":0b00001011 }

class dmov88(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['dmov'," ",loc16])
    patterns = { "opcode0":0b10100101 }


class flip90(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['flip'," ",'al'])
    patterns = { "opcode0":0b0101011001110000 }

class flip91(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['flip'," ",'ah'])
    patterns = { "opcode0":0b0101011001110001 }




class inc100(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['inc'," ",loc16])
    patterns = { "opcode0":0b00001010 }

class intr101(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int1'])
    patterns = { "opcode0":0b0000000000010000 }

class intr102(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int2'])
    patterns = { "opcode0":0b0000000000010001 }

class intr103(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int3'])
    patterns = { "opcode0":0b0000000000010010 }

class intr104(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int4'])
    patterns = { "opcode0":0b0000000000010011 }

class intr105(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int5'])
    patterns = { "opcode0":0b0000000000010100 }

class intr106(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int6'])
    patterns = { "opcode0":0b0000000000010101 }

class intr107(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int7'])
    patterns = { "opcode0":0b0000000000010110 }

class intr108(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int8'])
    patterns = { "opcode0":0b0000000000010111 }

class intr109(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int9'])
    patterns = { "opcode0":0b0000000000011000 }

class intr110(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int10'])
    patterns = { "opcode0":0b0000000000011001 }

class intr111(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int11'])
    patterns = { "opcode0":0b0000000000011010 }

class intr112(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int12'])
    patterns = { "opcode0":0b0000000000011011 }

class intr113(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int13'])
    patterns = { "opcode0":0b0000000000011100 }

class intr114(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'int14'])
    patterns = { "opcode0":0b0000000000011101 }

class intr115(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'dlogint'])
    patterns = { "opcode0":0b0000000000011110 }

class intr116(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'rtosint'])
    patterns = { "opcode0":0b0000000000011111 }

class intr117(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'nmi'])
    patterns = { "opcode0":0b0111011000010110 }

class intr118(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['intr'," ",'emuint'])
    patterns = { "opcode0":0b0111011000011100 }

class lb119(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['lb'," ",'*','xar7'])
    patterns = { "opcode0":0b0111011000100000 }



class lc121(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['lc'," ",'*','xar7'])
    patterns = { "opcode0":0b0111011000000100 }



class lcr124(adv32Instruction):
    tokens = [Token16]
    
    xarn = Operand("xarn",XARnRegisters,write = True)
    
    syntax = Syntax(['lcr'," ",'*',xarn])
    patterns = { "opcode0":0b0011111001100,"xarn":xarn }



class lsl127(adv32Instruction):
    tokens = [Token17]
    
    
    
    int4 = Operand("int4",int)
    
    syntax = Syntax(['lsl'," ",'acc',',',int4])
    patterns = { "opcode0":0b111111110011,"int4":int4 }

class lsl128(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['lsl'," ",'acc',',','t'])
    patterns = { "opcode0":0b1111111101010000 }

class lsl129(adv32Instruction):
    tokens = [Token17]
    int4 = Operand("int4",int)
    
    syntax = Syntax(['lsl'," ",'al',',',int4])
    patterns = { "opcode0":0b111111111000,"int4":int4 }

class lsl130(adv32Instruction):
    tokens = [Token17]
    
    
    
    int4 = Operand("int4",int)
    
    syntax = Syntax(['lsl'," ",'ah',',',int4])
    patterns = { "opcode0":0b111111111001,"int4":int4 }

class lsl131(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['lsl'," ",'al',',','t'])
    patterns = { "opcode0":0b1111111101100110 }

class lsl132(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['lsl'," ",'ah',',','t'])
    patterns = { "opcode0":0b1111111101100111 }

class lsll133(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['lsll'," ",'acc',',','t'])
    patterns = { "opcode0":0b0101011000111011 }

class lsr134(adv32Instruction):
    tokens = [Token17]
    
    
    
    int4 = Operand("int4",int)
    
    syntax = Syntax(['lsr'," ",'al',',',int4])
    patterns = { "opcode0":0b111111111100,"int4":int4 }

class lsr135(adv32Instruction):
    tokens = [Token17]
    
    
    
    int4 = Operand("int4",int)
    
    syntax = Syntax(['lsr'," ",'ah',',',int4])
    patterns = { "opcode0":0b111111111101,"int4":int4 }

class lsr136(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['lsr'," ",'al',',','t'])
    patterns = { "opcode0":0b1111111101100010 }

class lsr137(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['lsr'," ",'ah',',','t'])
    patterns = { "opcode0":0b1111111101100011 }

class lsrl138(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['lsrl'," ",'acc',',','t'])
    patterns = { "opcode0":0b0101011000100010 }



class mov150(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['mov'," ",'al',',',loc16])
    patterns = { "opcode0":0b10010010 }

class mov151(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",'ah',',',loc16])
    patterns = { "opcode0":0b10010011 }





class mov154(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    # loc = loc_mode1.
    #int4 = Operand("int4",int)
    syntax = Syntax(['mov'," ",'acc',',',loc16])
    # patterns = { "opcode0":0b10000101, "loccode":0b00000001 }
    patterns = { "opcode0":0b10000101 }




class mov156(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    #int4 = Operand("int4",int)
    
    syntax = Syntax(['mov'," ",'acc',',',loc16,'<<','shft16'])
    patterns = { "opcode0":0b00100101}

class mov157(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",'ar6',',',loc16])
    patterns = { "opcode0":0b01011110 }

class mov158(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",'ar7',',',loc16])
    patterns = { "opcode0":0b01011111 }

class mov159(adv32Instruction):
    tokens = [Token19]
    
    
    
    int10 = Operand("int10",int)
    
    syntax = Syntax(['mov'," ",'dp',',',int10])
    patterns = { "opcode0":0b111110,"int10":int10 }

class mov160(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",'ier',',',loc16])
    patterns = { "opcode0":0b00100011 }



class mov163(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    int0 = Operand("int0",int)
    
    syntax = Syntax(['mov0'," ",loc16,',',int0])
    patterns = { "opcode0":0b00101011 }

class mov164(adv32Instruction):
    tokens = [Token20]
    loc16 = Operand("loc16",loc_mode1)
    arn = Operand("arn",ARNRegisters_n_to_m,write = True)
    syntax = Syntax(['mov'," ",loc16,',',arn])
    patterns = { "opcode0":0b01111,"arn":arn }

class mov165(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['mov'," ",loc16,',','al'])
    patterns = { "opcode0":0b10010110 }

class mov166(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['mov'," ",loc16,',','ah'])
    patterns = { "opcode0":0b10010111 }



class mov169(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['mov'," ",loc16,',','ier'])
    patterns = { "opcode0":0b00100000 }

class mov170(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['mov'," ",loc16,',','p'])
    patterns = { "opcode0":0b00111111 }

class mov171(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['mov'," ",loc16,',','t'])
    patterns = { "opcode0":0b00100001 }


class mov173(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",'ph',',',loc16])
    patterns = { "opcode0":0b00101111 }

class mov174(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",'pl',',',loc16])
    patterns = { "opcode0":0b00100111 }

class mov175(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['mov'," ",'pm',',','al'])
    patterns = { "opcode0":0b0101011000111000 }

class mov176(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['mov'," ",'pm',',','ah'])
    patterns = { "opcode0":0b0010011000111001 }

class mov177(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mov'," ",'t',',',loc16])
    patterns = { "opcode0":0b00101101 }

class mov178(adv32Instruction):
    tokens = [Token0]
    
    
    
    int0 = Operand("int0",int)
    
    syntax = Syntax(['mov'," ",'tl',',',int0])
    patterns = { "opcode0":0b0101011001010110}

class mov179(adv32Instruction):
    tokens = [Token16]
    
    xarn = Operand("xarn",XARnRegisters,write = True)
    
    
    
    syntax = Syntax(['mov'," ",xarn,',','pc'])
    patterns = { "opcode0":0b0011111001011,"xarn":xarn }

class mova180(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mova'," ",'t',',',loc16])
    patterns = { "opcode0":0b00010000 }

class movad181(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['movad'," ",'t',',',loc16])
    patterns = { "opcode0":0b10100111 }

class movb182(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",'acc',',',int8])
    patterns = { "opcode0":0b00000010,"int8":int8 }

class movb183(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",'ar6',',',int8])
    patterns = { "opcode0":0b11010110,"int8":int8 }

class movb184(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",'ar7',',',int8])
    patterns = { "opcode0":0b11010111,"int8":int8 }

class movb185(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",'al',',',int8])
    patterns = { "opcode0":0b10011010,"int8":int8 }

class movb186(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",'ah',',',int8])
    patterns = { "opcode0":0b10011011,"int8":int8 }

class movb187(adv32Instruction):
    tokens = [Token22]
    
    ahlsb = Operand("ahlsb",axsbRegisters,write = True)
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['movb'," ",ahlsb,',',loc16])
    patterns = { "opcode0":0b1100011,"ahlsb":ahlsb }

class movb188(adv32Instruction):
    tokens = [Token23]
    
    ahmsb = Operand("ahmsb",axsbRegisters,write = True)
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['movb'," ",ahmsb,',',loc16])
    patterns = { "opcode0":0b0011100,"ahmsb":ahmsb }





class movb191(adv32Instruction):
    tokens = [Token26]
    
    loc16 = Operand("loc16",loc_mode1)
    
    almsb = Operand("almsb",axsbRegisters,write = True)
    
    syntax = Syntax(['movb'," ",loc16,',',almsb])
    patterns = { "opcode0":0b1100100,"almsb":almsb }

class movb192(adv32Instruction):
    tokens = [Token27]
    
    xarn = Operand("xarn",XARnRegisters,write = True)
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",xarn,',',int8])
    patterns = { "opcode0":0b11010,"xarn":xarn,"int8":int8 }

class movb193(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",'xar6',',',int8])
    patterns = { "opcode0":0b10111110,"int8":int8 }

class movb194(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['movb'," ",'xar7',',',int8])
    patterns = { "opcode0":0b10110110,"int8":int8 }

class movdl195(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movdl'," ",'xt',',',loc32])
    patterns = { "opcode0":0b10100110 }

class movh196(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    int1 = Operand("int1",int)
    
    syntax = Syntax(['movh'," ",loc16,',','acc','<<',int1])
    patterns = { "opcode0":0b10110011 }



class movh198(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['movh'," ",loc16,',','p'])
    patterns = { "opcode0":0b01010111 }

class movl199(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'acc',',',loc32])
    patterns = { "opcode0":0b00000110 }

class movl200(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",loc32,',','acc'])
    patterns = { "opcode0":0b00011110 }



class movl202(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','p'])
    patterns = { "opcode0":0b10101001 }

class movl203(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xar0'])
    patterns = { "opcode0":0b00111010 }

class movl204(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xar1'])
    patterns = { "opcode0":0b10110010 }

class movl205(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xar2'])
    patterns = { "opcode0":0b10101010 }

class movl206(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xar3'])
    patterns = { "opcode0":0b10100010 }

class movl207(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xar4'])
    patterns = { "opcode0":0b10101000 }

class movl208(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xar5'])
    patterns = { "opcode0":0b10100000 }

class movl209(adv32Instruction):
    tokens = [Token3]
    loc32 = Operand("loc32",loc_mode1)
    syntax = Syntax(['movl'," ",loc32,',','xar6'])
    patterns = { "opcode0":0b11000010 }

class movl210(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xar7'])
    patterns = { "opcode0":0b11000011 }

class movl211(adv32Instruction):
    tokens = [Token3]
    
    loc32 = Operand("loc32",loc_mode1)
    
    
    
    syntax = Syntax(['movl'," ",loc32,',','xt'])
    patterns = { "opcode0":0b10101011 }

class movl212(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['movl'," ",'p',',','acc'])
    patterns = { "opcode0":0b1111111101011010 }

class movl213(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'p',',',loc32])
    patterns = { "opcode0":0b10100011 }

class movl214(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar0',',',loc32])
    patterns = { "opcode0":0b10001110 }

class movl215(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar1',',',loc32])
    patterns = { "opcode0":0b10001011 }

class movl216(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar2',',',loc32])
    patterns = { "opcode0":0b10000110 }

class movl217(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar3',',',loc32])
    patterns = { "opcode0":0b10000010 }

class movl218(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar4',',',loc32])
    patterns = { "opcode0":0b10001010 }

class movl219(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar5',',',loc32])
    patterns = { "opcode0":0b10000011 }

class movl220(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar6',',',loc32])
    patterns = { "opcode0":0b11000100 }

class movl221(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xar7',',',loc32])
    patterns = { "opcode0":0b11000101 }



class movl230(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['movl'," ",'xt',',',loc32])
    patterns = { "opcode0":0b10000111 }

class movp231(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['movp'," ",'t',',',loc16])
    patterns = { "opcode0":0b00010110 }

class movs232(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['movs'," ",'t',',',loc16])
    patterns = { "opcode0":0b00010001 }

class movu233(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['movu'," ",'acc',',',loc16])
    patterns = { "opcode0":0b00001110 }





class movz237(adv32Instruction):
    tokens = [Token20]
    arn = Operand("arn",ARNRegisters_0_to_5,write = True)
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['movz'," ",arn,',',loc16])
    patterns = { "opcode0":0b01011,"arn":arn }

class movz238(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['movz'," ",'ar6',',',loc16])
    patterns = { "opcode0":0b10001000 }

class movz239(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['movz'," ",'ar7',',',loc16])
    patterns = { "opcode0":0b10000000 }

class movz240(adv32Instruction):
    tokens = [Token19]
    
    
    
    int10 = Operand("int10",int)
    
    syntax = Syntax(['movz'," ",'dp',',',int10])
    patterns = { "opcode0":0b101110,"int10":int10 }

class mpy242(adv32Instruction):
    tokens = [Token3]
    
    
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpy'," ",'acc',',','t',',',loc16])
    patterns = { "opcode0":0b00010010 }



class mpy244(adv32Instruction):
    tokens = [Token3]
    
    
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpy'," ",'p',',','t',',',loc16])
    patterns = { "opcode0":0b00110011 }

class mpya246(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpya'," ",'p',',','t',',',loc16])
    patterns = { "opcode0":0b00010111 }

class mpyb247(adv32Instruction):
    tokens = [Token7]
    
    
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['mpyb'," ",'acc',',','t',',',int8])
    patterns = { "opcode0":0b00110101,"int8":int8 }

class mpyb248(adv32Instruction):
    tokens = [Token7]
    
    
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['mpyb'," ",'p',',','t',',',int8])
    patterns = { "opcode0":0b00110001,"int8":int8 }

class mpys249(adv32Instruction):
    tokens = [Token3]
    
    
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpys'," ",'p',',','t',',',loc16])
    patterns = { "opcode0":0b00010011 }

class mpyu250(adv32Instruction):
    tokens = [Token3]
    
    
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpyu'," ",'p',',','t',',',loc16])
    patterns = { "opcode0":0b00110111 }

class mpyu251(adv32Instruction):
    tokens = [Token3]
    
    
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpyu'," ",'acc',',','t',',',loc16])
    patterns = { "opcode0":0b00110110 }

class mpyxu252(adv32Instruction):
    tokens = [Token3]
    
    
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpyxu'," ",'acc',',','t',',',loc16])
    patterns = { "opcode0":0b00110000 }

class mpyxu253(adv32Instruction):
    tokens = [Token3]
    
    
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['mpyxu'," ",'p',',','t',',',loc16])
    patterns = { "opcode0":0b00110010 }



class xretc255(adv32Instruction):
    tokens = [Token29]
    
    cond = Operand("cond",cond_mode)
    
    syntax = Syntax(['xretc'," ",cond])
    patterns = { "opcode0":0b010101101111 }




class xorb259(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['xorb'," ",'al',',',int8])
    patterns = { "opcode0":0b11110000,"int8":int8 }

class xorb260(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['xorb'," ",'ah',',',int8])
    patterns = { "opcode0":0b11110001,"int8":int8 }

class xor261(adv32Instruction):
    tokens = [Token6]
    
    loc16 = Operand("loc16",loc_mode1)
    
    int16 = Operand("int16",int)
    
    syntax = Syntax(['xor'," ",loc16,',',int16])
    patterns = { "opcode0":0b00011100,"int16":int16 }

class xor262(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['xor'," ",loc16,',','al'])
    patterns = { "opcode0":0b11110010 }

class xor263(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['xor'," ",loc16,',','ah'])
    patterns = { "opcode0":0b11110011 }

class xor264(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['xor'," ",'al',',',loc16])
    patterns = { "opcode0":0b01110000 }

class xor265(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['xor'," ",'ah',',',loc16])
    patterns = { "opcode0":0b01110001 }



class xor268(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['xor'," ",'acc',',',loc16])
    patterns = { "opcode0":0b10110111 }







class xcall273(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['xcall'," ",'*','al'])
    patterns = { "opcode0":0b0101011000110100 }




class xb286(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['xb'," ",'*','al'])
    patterns = { "opcode0":0b0101011000010100 }




class trap289(adv32Instruction):
    tokens = [Token37]
    
    vint = Operand("vint",int)
    
    syntax = Syntax(['trap'," ",vint])
    patterns = { "opcode0":0b00000000001,"vint":vint }

class test290(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['test'," ",'acc'])
    patterns = { "opcode0":0b1111111101011000 }




class tbit293(adv32Instruction):
    tokens = [Token39]
    
    loc16 = Operand("loc16",loc_mode1)
    
    int4 = Operand("int4",int)
    
    syntax = Syntax(['tbit'," ",loc16,',',int4])
    patterns = { "opcode0":0b0100,"int4":int4 }



class subu296(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['subu'," ",'acc',',',loc16])
    patterns = { "opcode0":0b00000001 }


class subr298(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['subr'," ",loc16,',','al'])
    patterns = { "opcode0":0b11101010 }

class subr299(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['subr'," ",loc16,',','ah'])
    patterns = { "opcode0":0b11101011 }


class subl301(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc32 = Operand("loc32",loc_mode1)
    
    syntax = Syntax(['subl'," ",'acc',',',loc32])
    patterns = { "opcode0":0b00000011 }



class subcu303(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['subcu'," ",'acc',',',loc16])
    patterns = { "opcode0":0b00011111 }



class subb305(adv32Instruction):
    tokens = [Token40]
    
    xarn = Operand("xarn",XARnRegisters,write = True)
    
    int7 = Operand("int7",int)
    
    syntax = Syntax(['subb'," ",xarn,',',int7])
    patterns = { "opcode0":0b11011,"xarn":xarn,"opcode2":0b1,"int7":int7 }


class subb306(adv32Instruction):
    tokens = [Token8]
    
    
    
    int7 = Operand("int7",int)
    
    syntax = Syntax(['subb'," ",'sp',',',int7])
    patterns = { "opcode0":0b111111101,"int7":int7 }

class subb307(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['subb'," ",'acc',',',int8])
    patterns = { "opcode0":0b00011001,"int8":int8 }

class sub308(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['sub'," ",loc16,',','al'])
    patterns = { "opcode0":0b01110100 }

class sub309(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['sub'," ",loc16,',','ah'])
    patterns = { "opcode0":0b01110101 }

class sub310(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['sub'," ",'al',',',loc16])
    patterns = { "opcode0":0b10011110 }

class sub311(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['sub'," ",'ah',',',loc16])
    patterns = { "opcode0":0b10011111 }




class spm315(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm1'," ",])
    patterns = { "opcode0":0b1111111101101000 }

class spm316(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm0'," "])
    patterns = { "opcode0":0b1111111101101001 }

class spm317(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm01'," "])
    patterns = { "opcode0":0b1111111101101010 }

class spm318(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm02'," "])
    patterns = { "opcode0":0b1111111101101011 }

class spm319(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm03'," "])
    patterns = { "opcode0":0b1111111101101100 }

class spm320(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm4'," "])
    patterns = { "opcode0":0b1111111101101101 }

class spm321(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm05'," "])
    patterns = { "opcode0":0b1111111101101110 }

class spm322(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['spm06'," "])
    patterns = { "opcode0":0b1111111101101111 }

class sfr323(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['sfr'," ",'acc',',','t'])
    patterns = { "opcode0":0b1111111101010001 }

class sfr324(adv32Instruction):
    tokens = [Token41]
    
    
    
    int16 = Operand("int16",int)
    
    syntax = Syntax(['sfr'," ",'acc',',',int16])
    patterns = { "opcode0":0b111111110100,"int16":int16 }

class setc325(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['setc'," ",'xf'])
    patterns = { "opcode0":0b0101011000100110 }

class setc326(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['setc'," ",'objmode'])
    patterns = { "opcode0":0b0101011000011111 }

class setc327(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['setc'," ",'m0m1map'])
    patterns = { "opcode0":0b0101011000011010 }

# class setc328(adv32Instruction):
#     tokens = [Token42]
    
#     Mode = Operand("Mode",int)
    
#     syntax = Syntax(['setc'," ",Mode])
#     patterns = { "opcode0":0b00111011,"Mode":Mode }

class sbrk329(adv32Instruction):
    tokens = [Token7]
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['sbrk'," ",int8])
    patterns = { "opcode0":0b11111101,"int8":int8 }

class sbf330(adv32Instruction):
    tokens = [Token7]
    
    int8 = Operand("int8",int)
    
    
    
    syntax = Syntax(['sbf'," ",int8,',','eq'])
    patterns = { "opcode0":0b11101100,"int8":int8 }

class sbf331(adv32Instruction):
    tokens = [Token7]
    
    int8 = Operand("int8",int)
    
    
    
    syntax = Syntax(['sbf'," ",int8,',','neq'])
    patterns = { "opcode0":0b11101101,"int8":int8 }

class sbf332(adv32Instruction):
    tokens = [Token7]
    
    int8 = Operand("int8",int)
    
    
    
    syntax = Syntax(['sbf'," ",int8,',','tc'])
    patterns = { "opcode0":0b11101110,"int8":int8 }

class sbf333(adv32Instruction):
    tokens = [Token7]
    
    int8 = Operand("int8",int)
    
    
    
    syntax = Syntax(['sbf'," ",int8,',','ntc'])
    patterns = { "opcode0":0b11101111,"int8":int8 }

class sbbu334(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['sbbu'," ",'acc',',',loc16])
    patterns = { "opcode0":0b00011101 }


class sat64336(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['sat64'," ",'acc',':','p'])
    patterns = { "opcode0":0b0101011000111110 }

class sat337(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['sat'," ",'acc'])
    patterns = { "opcode0":0b1111111101010111 }

class rpt338(adv32Instruction):
    tokens = [Token7]
    int8 = Operand("int8",int)
    syntax = Syntax(['rpt'," ",int8])
    patterns = { "opcode0":0b11110110,"int8":int8 }

class rpt339(adv32Instruction):
    tokens = [Token3]
    loc = Operand("loc",loc_mode1)
    syntax = Syntax(['rpt'," ",loc])
    patterns = { "opcode0":0b11110111 }



class pwrite349(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['pwrite'," ",'*','xar7',',',loc16])
    patterns = { "opcode0":0b00100110 }

class push350(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['push'," ",'xt'])
    patterns = { "opcode0":0b1010101110111101 }

class push351(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['push'," ",'xar0'])
    patterns = { "opcode0":0b0011101010111101 }

class push352(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'xar1'])
    patterns = { "opcode0":0b1011001010111101 }

class push353(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'xar2'])
    patterns = { "opcode0":0b1010101010111101 }

class push354(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'xar3'])
    patterns = { "opcode0":0b1010001010111101 }

class push355(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'xar4'])
    patterns = { "opcode0":0b1010100010111101 }

class push356(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'xar5'])
    patterns = { "opcode0":0b1010000010111101 }

class push357(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'xar6'])
    patterns = { "opcode0":0b1100001010111101 }

class push358(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['push'," ",'xar7'])
    patterns = { "opcode0":0b1100001110111101 }

class push359(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['push'," ",'t',':','st0'])
    patterns = { "opcode0":0b0111011000011001 }

class push360(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'st1'])
    patterns = { "opcode0":0b0111011000001000 }

class push361(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'st0'])
    patterns = { "opcode0":0b0111011000011000 }

class push362(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'rpc'])
    patterns = { "opcode0":0b0000000000000100 }

class push363(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'p'])
    patterns = { "opcode0":0b0111011000011101 }

class push364(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['push'," ",loc16])
    patterns = { "opcode0":0b00100010 }

class push365(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'ifr'])
    patterns = { "opcode0":0b0111011000001010 }

class push366(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['push'," ",'dp',':','st1'])
    patterns = { "opcode0":0b0111011000001001 }

class push367(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'dp'])
    patterns = { "opcode0":0b0111011000001011 }

class push368(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'dbgier'])
    patterns = { "opcode0":0b0111011000001110 }

class push369(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['push'," ",'ar1h',':','ar0h'])
    patterns = { "opcode0":0b0000000000000101 }

class push370(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['push'," ",'ar1',':','ar0'])
    patterns = { "opcode0":0b0111011000001101 }

class push371(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['push'," ",'ar3',':','ar2'])
    patterns = { "opcode0":0b0111011000001111 }

class push372(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['push'," ",'ar5',':','ar4'])
    patterns = { "opcode0":0b0111011000001100 }

class push373(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['push'," ",'acc'])
    patterns = { "opcode0":0b0001111010111101 }

class pread374(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    
    
    syntax = Syntax(['||pread'," ",loc16,',','*','xar7'])
    patterns = { "opcode0":0b00100100 }

class pop375(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xt'])
    patterns = { "opcode0":0b1000011110111110 }

class pop376(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar0'])
    patterns = { "opcode0":0b1000111010111110 }

class pop377(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar1'])
    patterns = { "opcode0":0b1000101110111110 }

class pop378(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar2'])
    patterns = { "opcode0":0b1000011010111110 }

class pop379(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar3'])
    patterns = { "opcode0":0b1000001010111110 }

class pop380(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar4'])
    patterns = { "opcode0":0b1000101010111110 }

class pop381(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar5'])
    patterns = { "opcode0":0b1000001110111110 }

class pop382(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar6'])
    patterns = { "opcode0":0b1100010010111110 }

class pop383(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'xar7'])
    patterns = { "opcode0":0b1100010110111110 }

class pop384(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['pop'," ",'t',':','st0'])
    patterns = { "opcode0":0b0111011000010101 }

class pop385(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'st1'])
    patterns = { "opcode0":0b0111011000000000 }

class pop386(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'st0'])
    patterns = { "opcode0":0b0111011000010011 }

class pop387(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'rpc'])
    patterns = { "opcode0":0b0000000000000111 }

class pop388(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'p'])
    patterns = { "opcode0":0b0111011000010001 }

class pop389(adv32Instruction):
    tokens = [Token3]
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['pop'," ",loc16])
    patterns = { "opcode0":0b00101010 }

class pop390(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'ifr'])
    patterns = { "opcode0":0b0000000000000010 }

class pop391(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['pop'," ",'dp',':','st1'])
    patterns = { "opcode0":0b0111011000000001 }

class pop392(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'dp'])
    patterns = { "opcode0":0b0111011000000011 }

class pop393(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'dbgier'])
    patterns = { "opcode0":0b0111011000010010 }

class pop394(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['pop'," ",'ar1h',':','ar0h'])
    patterns = { "opcode0":0b0000000000000011 }

class pop395(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['pop'," ",'ar1',':','ar0'])
    patterns = { "opcode0":0b0111011000000111 }

class pop396(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['pop'," ",'ar3',':','ar2'])
    patterns = { "opcode0":0b0111011000000101 }

class pop397(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['pop'," ",'ar5',':','ar4'])
    patterns = { "opcode0":0b0111011000000110 }

class pop398(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['pop'," ",'acc'])
    patterns = { "opcode0":0b0000011010111110 }



class orb400(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['orb'," ",'al',',',int8])
    patterns = { "opcode0":0b01010000,"int8":int8 }

class orb401(adv32Instruction):
    tokens = [Token7]
    
    
    
    int8 = Operand("int8",int)
    
    syntax = Syntax(['orb'," ",'ah',',',int8])
    patterns = { "opcode0":0b01010001,"int8":int8 }

class or402(adv32Instruction):
    tokens = [Token3]
    
    loc = Operand("loc",loc_mode1)
    
    
    
    syntax = Syntax(['or'," ",loc,',','al'])
    patterns = { "opcode0":0b10011000 }

class or403(adv32Instruction):
    tokens = [Token3]
    
    loc = Operand("loc",loc_mode1)
    
    
    
    syntax = Syntax(['or'," ",loc,',','ah'])
    patterns = { "opcode0":0b10011001 }





class or407(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['or'," ",'al',',',loc16])
    patterns = { "opcode0":0b11001010 }

class or408(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['or'," ",'ah',',',loc16])
    patterns = { "opcode0":0b11001011 }





class or411(adv32Instruction):
    tokens = [Token3]
    
    
    
    loc16 = Operand("loc16",loc_mode1)
    
    syntax = Syntax(['or'," ",'acc',',',loc16])
    patterns = { "opcode0":0b10101111 }

class not412(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['not'," ",'al'])
    patterns = { "opcode0":0b1111111101011110 }

class not413(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['not'," ",'ah'])
    patterns = { "opcode0":0b1111111101011111 }

class not414(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['not'," ",'acc'])
    patterns = { "opcode0":0b1111111101010101 }

class norm415(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['norm'," ",'acc',',','*'])
    patterns = { "opcode0":0b0101011000100100 }

class norm416(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['norm'," ",'acc',',','*','+','+'])
    patterns = { "opcode0":0b0101011001011010 }

class norm417(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['norm'," ",'acc',',','*','-','-'])
    patterns = { "opcode0":0b0101011000100000 }

class norm418(adv32Instruction):
    tokens = [Token0]
    zero = Operand("zero",int)
    
    
    
    
    syntax = Syntax(['norm'," ",'acc',',','*',zero,'+','+'])
    patterns = { "opcode0":0b0101011001110111 }

class norm419(adv32Instruction):
    tokens = [Token0]
    zero = Operand("zero",int)
    
    
    
    
    syntax = Syntax(['norm'," ",'acc',',','*',zero,'-','-'])
    patterns = { "opcode0":0b0101011000110000 }

class nop11035(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['nop'])
    patterns = { "opcode0":0x7700}

class nop420(adv32Instruction):
    tokens = [Token48]
    ind = Operand("ind",loc_mode1)
    arpn = Operand("arpn",ARPNRegisters,write = True)
    syntax = Syntax(['nop'," ","{",ind,"}","{",arpn,"}"])
    patterns = { "opcode0":0b01110111, }

class negtc421(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['negtc'," ",'acc'])
    patterns = { "opcode0":0b0101011000110010 }

class neg64422(adv32Instruction):
    tokens = [Token0]
    
    
    
    
    
    syntax = Syntax(['neg64'," ",'acc',':','p'])
    patterns = { "opcode0":0b0101011001011000 }

class neg423(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['neg'," ",'al'])
    patterns = { "opcode0":0b1111111101011100 }

class neg424(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['neg'," ",'ah'])
    patterns = { "opcode0":0b1111111101011101 }

class neg425(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['neg'," ",'acc'])
    patterns = { "opcode0":0b1111111101010100 }

#---------------------------------------------------------------------------------------------------------------#
class add426(adv32Instruction):
    tokens = [Token0]

    syntax = Syntax(['addl'," ",'acc',',','p',"<<","pm"])
    patterns = { "opcode0":0b0001000010101100 }

class asr427(adv32Instruction):
    tokens = [Token12]

    shft = Operand("shft",int)
    
    syntax = Syntax(['asr64'," ",'acc',':','p',",",shft])
    patterns = { "opcode0":0b010101101000,"shft":shft }

class asr428(adv32Instruction):
    tokens = [Token0]

    syntax = Syntax(['asr64'," ",'acc',':','p',",","t"])
    patterns = { "opcode0":0b0101011000101100}

class cmp429(adv32Instruction):
    tokens = [Token0]

    syntax = Syntax(['cmp64'," ",'acc',':','p',])
    patterns = { "opcode0":0b0101011001011110}

class cmp430(adv32Instruction):
    tokens = [Token0]

    syntax = Syntax(['cmpl'," ",'acc',',','p','<<','pm',])
    patterns = { "opcode0":0b1111111101011001}    




class lsl434(adv32Instruction):
    tokens = [Token12]
    shft = Operand("shft",int)
    syntax = Syntax(['lsl64'," ",'acc',':','p',',',shft])
    patterns = { "opcode0":0b010101101010,'shft':shft}  

class lsl435(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['lsl64'," ",'acc',':','p',',','t'])
    patterns = { "opcode0":0b0101011001010010}

class lsr436(adv32Instruction):
    tokens = [Token12]
    shft = Operand("shft",int)
    syntax = Syntax(['lsr64'," ",'acc',':','p',',',shft])
    patterns = { "opcode0":0b010101101001,'shft':shft}  

class lsr437(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['lsr64'," ",'acc',':','p',',','t'])
    patterns = { "opcode0":0b0101011001011011}








class movl441(adv32Instruction):
    tokens = [Token0]
    
    syntax = Syntax(['movl'," ",'acc',',','p','<<','pm'])
    patterns = { "opcode0":0b0001011010101100 }

class norm442(adv32Instruction):
    tokens = [Token16]
    
    xarn = Operand("xarn",XARnRegisters,write = True)
    syntax = Syntax(["norm"," ","acc",",",xarn,"+","+"])
    patterns = { "opcode0":0b1111111101111 }

class norm443(adv32Instruction):
    tokens = [Token16]
    
    xarn = Operand("xarn",XARnRegisters,write = True)
    syntax = Syntax(["norm"," ","acc",",",xarn,"-","-"])
    patterns = { "opcode0":0b1111111101110 }


class rorl444(adv32Instruction):
    tokens = [Token0]
    
    
    
    syntax = Syntax(['rol'," ",'acc'])
    patterns = { "opcode0":0b1111111101010011 }

class setc445(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'sxm'])
    patterns = { "opcode0":0b0011101100000001 }

class setc446(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'ovm'])
    patterns = { "opcode0":0b0011101100000010 }

class setc447(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'tc'])
    patterns = { "opcode0":0b0011101100000100 }

class setc448(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'c'])
    patterns = { "opcode0":0b0011101100001000 }

class setc449(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'intm'])
    patterns = { "opcode0":0b0011101100010000 }

class setc450(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'dbgm'])
    patterns = { "opcode0":0b0011101100100000}

class setc451(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'page0'])
    patterns = { "opcode0":0b0011101101000000}

class setc452(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['setc'," ",'vmap'])
    patterns = { "opcode0":0b0011101110000000}

class sub453(adv32Instruction):
    tokens = [Token48]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['sub'," ","acc",',',loc16,'<<',"shft0"])
    patterns = { "opcode0":0b10101110}



class sub455(adv32Instruction):
    tokens = [Token48]
    loc16 = Operand("loc16",loc_mode1)

    syntax = Syntax(['sub'," ","acc",',',loc16,'<<',"shft16"])
    patterns = { "opcode0":0b00000100}

class subl456(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['subl'," ",'acc',',','p','<<','pm'])
    patterns = { "opcode0":0b0001000110101100}

class zap457(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['zap'," ",'ovc'])
    patterns = { "opcode0":0b0101011001011100}

#---------------------------------------------------------------------------------------------------------------#
# 书上没有，但确实有的
class push1000(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['push'," ",'rb'])
    patterns = { "opcode0":0xfff0}


class CLRC1002(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['clrc'," ",'ovm|page0'])
    patterns = { "opcode0":0x2942}

# class nop1003(adv32Instruction):
#     tokens = [Token0]
#     syntax = Syntax(['||nop'])
#     patterns = { "opcode0":0x7700}

# class movb1004(adv32Instruction):
#     tokens = [Toekn50]
#     int1 = Operand("int1",int)
#     int2 = Operand("int2",int)
#     syntax = Syntax(['movb'," ",int1,',',int2,',',"unc"])
#     patterns = { "opcode0":0x56bf,"int1":int1,"int2":int2}

class movl1004(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['movl'," ","xar6",",","acc"])
    patterns = { "opcode0":0x1ea6}

class movz1005(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['movz'," ","ar7",",","al"])
    patterns = { "opcode0":0x80a9}

class movl1006(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['movl'," ","acc",",","xar6"])
    patterns = { "opcode0":0x06a6}

class cmpl1007(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['cmpl'," ","acc",",","xar7"])
    patterns = { "opcode0":0x0fa7}



class movz1011(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['movz'," ","ar4",",","sp"])
    patterns = { "opcode0":0x5cad}

class pread1012(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['movz'," ","ar4",",","sp"])
    patterns = { "opcode0":0x5cad}

class movl1013(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movl'," ","xar4",",","acc"])
    patterns = { "opcode0":0x8aa9}

class movl1014(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movl'," ","acc",",","xar4"])
    patterns = { "opcode0":0xa8a9}



class pread1017(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['pread'," ","al",",","*","xar7"])
    patterns = { "opcode0":0x24a9}

class pread1018(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['pread'," ","ah",",","*","xar7"])
    patterns = { "opcode0":0x24a8}

class rpt1019(adv32Instruction):
    tokens = [Token0]
    syntax = Syntax(['rpt'," ","ar1"])
    patterns = { "opcode0":0xf7a1}


class movl1020(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movl'," ","acc",",","xar7"])
    patterns = { "opcode0":0x06a7}

class add1021(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['add'," ","acc",",","ar1"])
    patterns = { "opcode0":0x81a1}

class movl1022(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movl'," ","xar7",",","acc"])
    patterns = { "opcode0":0x1ea7}

class movz1023(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movz'," ","ar1",",","al"])
    patterns = { "opcode0":0x59a9}




class cmpl1026(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['cmpl'," ","acc",",","p"])
    patterns = { "opcode0":0x0fab}

class mov1027(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['mov'," ","al",",","ar1"])
    patterns = { "opcode0":0x92a1}

class movl1028(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movl'," ","xar3",",","xar4"])
    patterns = { "opcode0":0x82a4}


    
class ADDL1031(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['addl'," ","acc",",","xar3"])
    patterns = { "opcode0":0x07a3}

class MOVL1032(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movl'," ","p",",","xar4"])
    patterns = { "opcode0":0xa8ab}

class MOVL1033(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movl'," ","xar7",",","xar4"])
    patterns = { "opcode0":0xc5a4}


class MOVLZ1033(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['movz'," ","ar6",",","al"])
    patterns = { "opcode0":0xc5a4}

class setc1034(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['setc'," ","intm|dbgm"])
    patterns = { "opcode0":0x3b30}

class add23(adv32Instruction):
    tokens = [Token3]
    loc16 = Operand("loc16",loc_mode1)
    syntax = Syntax(['add'," ",'acc',',',loc16])
    patterns = { "opcode0":0x81 }

class itrap1(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['itrap1',])
    patterns = { "opcode0":0xffff}

class itrap0(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['itrap0',])
    patterns = { "opcode0":0x0000}
class aborti(adv32Instruction):
    tokens = [Token0]     
    syntax = Syntax(['aborti',])
    patterns = { "opcode0":0x0001}

# class word(adv32Instruction):
#     tokens = [Token0]
#     imm = Operand("imm",int)
#     syntax = Syntax(['.word'," ",imm])
#     patterns = { "opcode0":imm}


#SB指令补充
class sb347(adv32Instruction):
    tokens = [Token57]
    syntax = Syntax(['sb'," ","C$L2|C$L4",',',"eq"])
    patterns = { "opcode0":0x61,"int8":0x03 }

class sb350(adv32Instruction):
    tokens = [Token57]
    syntax = Syntax(['sb'," ","C$L5",',',"eq"])
    patterns = { "opcode0":0x61,"int8":0x0f }

class sb352(adv32Instruction):
    tokens = [Token57]
    syntax = Syntax(['sb'," ","C$L3",',',"eq"])
    patterns = { "opcode0":0x61,"int8":0x04 }

class sb354(adv32Instruction):
    tokens = [Token57]
    syntax = Syntax(['sb'," ","C$L2",',',"eq"])
    patterns = { "opcode0":0x61,"int8":0x06 }

class sb355(adv32Instruction):
    tokens = [Token57]
    syntax = Syntax(['sb'," ","C$L1",',',"neq"])
    patterns = { "opcode0":0x60,"int8":0x04 }

class sb356(adv32Instruction):
    tokens = [Token57]
    syntax = Syntax(['sb'," ","C$L2",',',"unc"])
    patterns = { "opcode0":0x6f,"int8":0x05 }    

class sb338(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","start",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x0f }

class sb339(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","get_data",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x04 }

class sb340(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","get_addr",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x03 }

class sb341(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","do_pinit",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x05 }

class sb342(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","done_init",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x0e }

class sb343(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","start_pinit",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x06 }

class sb344(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","loop_pinit",',',cond])
    patterns = { "opcode0":0b0110,"int8":0xf7 }

class sb345(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","C$L1",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x0 }

class sb346(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","C$L2|C$L5",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x0d }

class sb348(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","C$L1",',',cond])
    patterns = { "opcode0":0b0110,"int8":0xea }

class sb349(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","C$L2",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x07 }

class sb353(adv32Instruction):
    tokens = [Token56]
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ","C$L3",',',cond])
    patterns = { "opcode0":0b0110,"int8":0x15 }



####通用SB
class sb335(adv32Instruction):
    tokens = [Token43]
    int8 = Operand("int8",int)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ",int8,',',cond])
    patterns = { "opcode0":0b0110,"int8":int8 }

class sb336(adv32Instruction):
    tokens = [Token43]
    int8 = Operand("int8",int)
    cond = Operand("cond",cond_mode)
    syntax = Syntax(['sb'," ",int8,',',cond])
    patterns = { "opcode0":0b0110,"int8":int8 }




###反汇编错误反馈
class error(adv32Instruction):
    tokens = [Token51]
    imm = Operand("imm",int)
    syntax = Syntax(['error32'])
    patterns = { "opcode0":imm}

class error(adv32Instruction):
    tokens = [Token0]
    imm = Operand("imm",int)
    syntax = Syntax(['error16'])
    patterns = { "opcode0":imm}



###浮点指令集
class absf32(adv32Instruction):
    tokens = [Token_fpu1]
    rah = Operand("rah", adv32fpuRaH_Register, read=True)
    rbh = Operand("rbh", adv32fpuRaH_Register, read=True)
    syntax = Syntax(['absf32', " ",rah, "," , rbh])
    patterns = { "opcode0":0b11100110100101010000000000, "rah":rah, "rbh":rbh}

class addf32(adv32Instruction):
    tokens = [Token_fpu2]
    rah = Operand("rah", adv32fpuRaH_Register, read=True)
    rbh = Operand("rbh", adv32fpuRaH_Register, read=True)
    int16 = Operand("int16",int)
    syntax = Syntax(['addf32', " ",rah, "," , "#" , int16 , ",",rbh])
    patterns = { "opcode0":0b1110100010, "int16":int16, "rah":rah, "rbh":rbh }



















######################################
#指令选择
######################################

@isa.pattern("stm", "MOVI16(reg)", size=2, cycles=1, energy=1)
@isa.pattern("stm", "MOVU16(reg)", size=2, cycles=1, energy=1)
@isa.pattern("stm", "MOVI32(reg)", size=2, cycles=1, energy=1)
@isa.pattern("stm", "MOVU32(reg)", size=2, cycles=1, energy=1)
def pattern_mov16(context, tree, c0):
    pass

@isa.pattern("stm", "JMP", size=4)
def pattern_jmp(context, tree):
    pass

flag1 = True
@isa.pattern("stm", "STRI8(memsrc, src8)", size=2)
@isa.pattern("stm", "STRU8(memsrc, src8)", size=2)
@isa.pattern("stm", "STRI16(memsrc, src16)", size=2)
@isa.pattern("stm", "STRU16(memsrc, src16)", size=2)
@isa.pattern("stm", "STRI32(memsrc, src32)", size=2)
@isa.pattern("stm", "STRU32(memsrc, src32)", size=2)
def pattern_str16(context, tree, c0, c1):
    pass

#---------------------------------------------------
@isa.pattern("src8", "cnst", size=2, cycles=0, energy=0)
@isa.pattern("src16", "cnst", size=2, cycles=0, energy=0)
@isa.pattern("src32", "cnst", size=2, cycles=0, energy=0)
def pattern_cnst_src(context, tree, c0):
    print("583 =", c0)
    return c0

@isa.pattern("src8", "LDRI8(memsrc)", size=4, cycles=1, energy=1)
@isa.pattern("src16", "LDRI16(memsrc)", size=4, cycles=1, energy=1)
@isa.pattern("src32", "LDRI32(memsrc)", size=4, cycles=1, energy=1)
def pattern_LDRI16(context, tree, c0):
    print("1281", context, tree.value)
    return c0

@isa.pattern("src8", "reg", size=2, cycles=0, energy=0)
@isa.pattern("src16", "reg", size=2, cycles=0, energy=0)
@isa.pattern("src32", "reg", size=2, cycles=0, energy=0)
def pattern_src_reg(context, tree, c0):
    print("583 =", c0)
    return c0

@isa.pattern("reg", "LDRI8(memsrc)", size=2, cycles=0, energy=0)
@isa.pattern("reg", "LDRI16(memsrc)", size=2, cycles=0, energy=0)
@isa.pattern("reg", "LDRI32(memsrc)", size=2, cycles=0, energy=0)
def pattern_reg_src(context, tree, c0):
    print("583 =", c0)
    return c0

#--------------------------------------------------------------

@isa.pattern("cnst", "CONSTI8", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTU8", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTI16", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTU16", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTI32", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTU32", size=0, cycles=0, energy=0)
def pattern_cnst(context, tree):
    print("576 = ", tree.value)
    return tree.value

@isa.pattern("memsrc", "FPRELU16", size=2, cycles=0, energy=0)
def pattern_mem_src_fprel(context, tree):
    print("1266 = ", tree.value)
    return tree.value

@isa.pattern("memdst", "FPRELU16", size=2, cycles=0, energy=0)
def pattern_mem_dst_fprelu16(context, tree):
    print("1270 = ", tree.value)
    return tree.value

@isa.pattern("reg", "CONSTI16", size=4, cycles=1, energy=1)
def pattern_fill_reg16(context, tree):
    pass


@isa.pattern("reg", "src16", size=4, cycles=1, energy=1)
def pattern_src16(context, tree, c0):
    print("1274", context, tree.value, c0)
    return c0

@isa.pattern("reg", "ADDI8(reg, src8)", size=4, cycles=1, energy=1)
@isa.pattern("reg", "ADDU8(reg, src8)", size=4, cycles=1, energy=1)
@isa.pattern("reg", "ADDI16(reg, src16)", size=4, cycles=1, energy=1)
@isa.pattern("reg", "ADDU16(reg, src16)", size=4, cycles=1, energy=1)
@isa.pattern("reg", "ADDI32(reg, src32)", size=4, cycles=1, energy=1)
@isa.pattern("reg", "ADDU32(reg, src32)", size=4, cycles=1, energy=1)
def pattern_add16(context, tree, c0, c1):
    pass 

@isa.pattern("reg", "SUBI8(reg, src8)", size=4)
@isa.pattern("reg", "SUBU8(reg, src8)", size=4)
@isa.pattern("reg", "SUBI16(reg, src16)", size=4)
@isa.pattern("reg", "SUBU16(reg, src16)", size=4)
def pattern_sub16(context, tree, c0, c1):
    d = context.new_reg(adv32Register32)
    context.emit(subb306(c1))
    return d

@isa.pattern("reg", "DIVI8(reg, src8)", size=4)
@isa.pattern("reg", "DIVU8(reg, src8)", size=4)
@isa.pattern("reg", "DIVI16(reg, src16)", size=4)
@isa.pattern("reg", "DIVU16(reg, src16)", size=4)
def pattern_div16(context, tree, c0, c1):
    pass



@isa.pattern("reg", "MULI8(reg, src8)", size=10)
@isa.pattern("reg", "MULU8(reg, src8)", size=10)
@isa.pattern("reg", "MULI16(reg, src16)", size=10)
@isa.pattern("reg", "MULU16(reg, src16)", size=10)
def pattern_mul16(context, tree, c0, c1):
    pass

#------------------------------------------------------------------------
@isa.pattern("reg", "REGI8", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU8", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGI16", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU16", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGI32", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU32", size=0, cycles=0, energy=0)
def pattern_regi16(context, tree):
    print("1310 =", tree.value)
    return tree.value
#----------------------------------------------------------------
class c240x_dubug_JumpToken(adv3216token):
    opcode = bit_range(13, 16)
    condition = bit_range(10, 13)
    offset = bit_range(0, 10)

class JumpInstruction(adv32Instruction):
    tokens = [c240x_dubug_JumpToken]


# Relocation functions:
@isa.register_relocation
class Rel10Relocation(Relocation):
    """ Apply 10 bit signed relocation """

    name = "rel10"
    token = c240x_dubug_JumpToken
    field = "offset"

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        offset = (sym_value - (align(reloc_value, 2)) - 2) >> 1
        assert offset in range(-511, 511, 1), str(offset)
        return offset



