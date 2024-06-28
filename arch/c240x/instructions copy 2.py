""" Definitions of c240x instruction set. """

import abc
from ast import If
from atexit import register
from calendar import c

from filecmp import cmp
import opcode
from platform import architecture
from pyexpat import model
from re import A, X
from webbrowser import Opera

from ppci.arch.c240x.registers import SP,AR0
from ppci.arch.msp430.instructions import Bit
from ..encoding import Instruction, Operand, Syntax, Constructor, Transform
from ..generic_instructions import ArtificialInstruction
from ..generic_instructions import RegisterUseDef, Global
from ..isa import Relocation, Isa
from ..token import Token, bit_range, bit
from .registers import AR2, AR3, c240xRegister,c240xStackFrameRegister,c240xARnRegister,c240x_Memtoreg_dma_Registers
from ...utils.bitfun import align

# pylint: disable=no-member,invalid-name


isa = Isa()

############################# define Base Class #############################
class c240xToken(Token):
    class Info:
        size = 16

class c240xTokenbit7(Token):
    class Info:
        size = 7

class c240xTokenbit8(Token):
    class Info:
        size = 8

class c240x32Token(Token):
    class Info:
        size = 32

class c240xInstruction(Instruction):
    isa = isa

################################################
class SrcImm8Token(c240xTokenbit8):
    srcimm = bit_range(0, 8)

class DstImm8Token(c240xTokenbit8):
    dstimm = bit_range(0, 8)

class SrcImm7Token(c240xTokenbit7):
    srcimm = bit_range(0, 7)

class DstImm7Token(c240xTokenbit7):
    dstimm = bit_range(0, 7)

class Imm16Token(c240xToken):
    imm16 = bit_range(0,16)

############################## Operands define #############################

class Src(Constructor):
    reg = Operand("reg", c240xRegister, read=True)
    imm = Operand("imm", int)
    is_reg_target = False
    is_special = False

class Dst(Constructor):
    reg = Operand("reg", c240xRegister, write=True)
    imm = Operand("imm", int)
    is_reg_target = False
    is_special = False

##########  Src
class RegSrc(Src):
    """ Simply refer to a register """

    is_reg_target = True
    syntax = Syntax([Src.reg])
    # patterns = {"ARU": Src.reg}

class imm8Src(Src):
    is_special = True
    tokens = [SrcImm8Token]
    syntax = Syntax(["#", Src.imm])
    patterns = { "NAR": Src.imm}

    def gitsrcimm(self):
        return Src.imm

class imm_Src(Src):
    tokens = [SrcImm8Token]
    syntax = Syntax(["#", Src.imm])
    is_special = True
    patterns = {"NAR": Src.imm}

class AdrSrc7(Src):
    """ absolute address (dma)"""

    is_special = True
    addr = Operand("addr", str) 
    tokens = [SrcImm7Token]
    syntax = Syntax([addr])
    patterns = { "source": 2}

class PMAaddress(Src):
    """ absolute address """

    is_special = True
    addr = Operand("addr", str)
    tokens = [Imm16Token]
    syntax = Syntax([addr])
    patterns = { "NAR": 2 }

##########  Dst
class RegDst(Dst):
    is_reg_target = True
    syntax = Syntax([Dst.reg])
    patterns = {"NAR": Dst.reg}

class AdrDst7(Dst):
    """ absolute address """

    is_special = True
    addr = Operand("addr", str)
    tokens = [DstImm7Token]
    syntax = Syntax([addr])
    patterns = { "NAR": 2}

class MemDst(Dst):
    """  要舍弃  """

    tokens = [Imm16Token]
    # syntax = Syntax([Dst.imm, "(", Dst.reg, ")"])
    syntax = Syntax([ Dst.reg ])
    patterns = { "NAR": Dst.reg }

src_modes = ( imm8Src, imm_Src, AdrSrc7, PMAaddress, RegSrc, MemDst)
dst_modes = ( AdrDst7, RegDst, MemDst)

######## used for pointer mode operands for indirect address mode ##########

class PtrMode1(Constructor):
        is_special = True
        syntax = Syntax(["*"])

# class PtrMode1(Dst):
#         is_special = True
#         addr = Operand("addr", str)
#         syntax = Syntax([addr])
#         patterns = {"destination": 2}


class PtrMode2(Constructor):
        is_special = True
        syntax = Syntax(["*", "-"])


class PtrMode3(Constructor):
        is_special = True
        syntax = Syntax(["*", "+"])
    
class PtrMode4(Constructor):
        is_special = True
        syntax = Syntax(["*", "b","r","o", "-"])

class PtrMode5(Constructor):
        is_special = True
        syntax = Syntax(["*", "0", "-"])

class PtrMode6(Constructor):
        is_special = True
        syntax = Syntax(["*", "0", "+"])

class PtrMode7(Constructor):
        is_special = True
        syntax = Syntax(["*", "b","r","o", "+"])

Ptr_modes = (
    PtrMode1,
    PtrMode2,
    PtrMode3,
    PtrMode4,
    PtrMode5,
    PtrMode6,
    PtrMode7,
)

# def p1():
#     return Operand("Op1", PtrMode1)
     
# def p2():
#     return Operand("Op1", PtrMode2)

# def p3():
#     return Operand("Op1", PtrMode3)

# def p4():
#     return Operand("Op1", PtrMode4)

# def p5():
#     return Operand("Op1", PtrMode5)

# def p6():
#     return Operand("Op1", PtrMode6)

# def p7():
#     return Operand("Op1", PtrMode7)


# def switch_case(ARU):
#         if ARU==0:
#             return p1()
#         elif ARU == 1:
#             return p2()



######## used for ARn operands for indirect address mode ##########
# class AR0(Constructor):
#         is_special = True
#         syntax = Syntax(["AR0"])

# class AR1(Constructor):
#         is_special = True
#         syntax = Syntax(["AR1"])

# class AR2(Constructor):
#         is_special = True
#         syntax = Syntax(["AR2"])
    
# class AR3(Constructor):
#         is_special = True
#         syntax = Syntax(["AR3"])

# class AR4(Constructor):
#         is_special = True
#         syntax = Syntax(["AR4"])

# class AR5(Constructor):
#         is_special = True
#         syntax = Syntax(["AR5"])

# class AR6(Constructor):
#         is_special = True
#         syntax = Syntax(["AR6"])

# class AR7(Constructor):
#         is_special = True
#         syntax = Syntax(["AR7"])

def f0():
    return Operand("AR0", c240xARnRegister)
     
def f1():
    return Operand("AR1", c240xARnRegister)

def f2():
    return Operand("AR2", c240xARnRegister)

def f3():
    return Operand("AR3", c240xARnRegister)

def f4():
    return Operand("AR4", c240xARnRegister)

def f5():
    return Operand("AR5", c240xARnRegister)

def f6():
    return Operand("AR6", c240xARnRegister)

def f7():
    return Operand("AR7", c240xARnRegister)

def switch_case1(NAR):pass
"""                return {
                    0:  f1(),          
                    1:  f2(),
                    2:  f3(),
                    3:  f4(),
                    4:  f5(),
                    5:  f6(),
                    6:  f7(),
            }.get(NAR, lambda: None)()
"""
############################## End  Operands define #############################



############################# instruction format ###########################

""" (SAR)LAR ARx,dma / (SAR)LAR ARx, ind[,ARn]     """
class c240xLSARxDImodeToken(c240xToken):
    opcode = bit_range(11,16)
    X = bit_range(8, 11)
    F1 = bit(7)
    dst = bit_range(0,7)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)

"""  POPD/PSHD    between stack and data memory         """
class c240xOpStackMemToken(c240xToken):
    Func4 = bit_range(12,16)
    opcode = bit_range(8, 12)
    F1 = bit(7)
    Op = bit_range(0,7)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)

# class c240xOpStackMemToken_debug(c240xToken):
#     Func4 = bit_range(12,16)
#     opcode = bit_range(8, 12)
#     F1 = bit(7)
#     F2 = bit_range(0,7)


"""         RET           """
class c240xRETToken(c240xToken):
    Func4 = bit_range(12,16)
    opcode = bit_range(8, 12)
    Func8 = bit_range(0,8)

"""       8bit imm      Format          """
class  c240ximm8ModeToken(c240xToken):
    Func4 = bit_range(12,16)
    opcode = bit_range(8, 12)
    NAR = bit_range(0,8)

"""      8bit imm and ARX Format     """
class  c240ximm8ARxToken(c240xToken):
    opcode = bit_range(11,16)
    Op2 = bit_range(8, 11)
    Op1 = bit_range(0,8)

class c240xPMAToken(c240xToken):
    Func4 = bit_range(12,16)
    opcode = bit_range(8, 12)
    F1 = bit(7)
    Op = bit_range(0,7)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)

class c240xCMPRToken(c240xToken):
    opcode = bit_range(2,16)
    cm = bit_range(0,2)

class c240x_b_pma_Token(c240x32Token):
    pma = bit_range(16, 32)
    opcode = bit_range(7, 16)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)


######################
##2022/12/12   

""" dma """
#1
class c240xdmaToken(c240xToken):
    opcode = bit_range(7,16)
    imm = bit_range(0,7)
#2
class c240xshiftdmaToken(c240xToken):
    opcode = bit_range(12,16)
    shift = bit_range(8,12)
    imm1 = bit(7)
    imm2 = bit_range(0,7)
#3
class c240x_con16(c240xToken):
    opcode = bit_range(0,16)
#4
class c240x_imm8k(c240xToken):
    opcode = bit_range(8,16)
    NAR = bit_range(0,8)

#4_1
class c240x_imm13k(c240xToken):
    opcode = bit_range(13,16)
    imm = bit_range(0,13)

#5  (32bit)
class c240x_lkshift_Token(c240x32Token):
    lk = bit_range(16, 32)
    opcode = bit_range(4,16)
    imm = bit_range(0,4)


#test
class c240x_dma_shift_Token(c240xToken):
    opcode = bit_range(12,16)
    shift = bit_range(8,12)
    imm1 = bit(7)
    dma = bit_range(0,7)

#sar arx,k
class c240x_arx_k(c240xToken):
    opcode = bit_range(11,16)
    arx = bit_range(8,11)
    k = bit_range(0,8)

#sar arx,ind,arn
class c240x_arx_ind_arn(c240xToken):
    opcode = bit_range(11,16)
    arx = bit_range(8,11)
    a = bit(7)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)
#sacl ind,shift2,ARn
class c240x_ind_shift2_arn(c240xToken):
    opcode = bit_range(11,16)
    shift2 = bit_range(8,11)
    a = bit(7)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)



############################# define instructions ###########################

####  ARx DIMode Instructions #####

class OpARxInstruction(c240xInstruction):
    tokens = [c240xLSARxDImodeToken]

# sar arx,ind
def  create_OpARx_instruction(mne, opcode, S=0, F1=0, NAR=0, N=0, dst_read=True, dst_write=True):
    """ Factory function to define a Operating ARx Instruction """

    arx = Operand("arx", src_modes) #一个ARn寄存器
    ARU = Operand("ARU", Ptr_modes) #就是ind
    if  S == 1 : ARU =  Operand("ARU", dst_modes)
    syntax = Syntax([mne, " ", arx, ",", " ", ARU])
    # patterns = {"opcode": opcode,   "ARU":1 ,"F1": F1, "N":N, "NAR":0}
    patterns = { "opcode": opcode,  "ARU":1 ,"F1": F1, "N":N, "NAR":0}
    members = {
        "opcode": opcode,
        "syntax": syntax,
        "ARU": ARU,
        "arx":arx,
        "patterns": patterns,
        "dst_read": dst_read,
        "dst_write": dst_write,
    }
    return type(mne.title(), (OpARxInstruction,), members)

# # LARd = create_OpARx_instruction("lar",0 )
# # LARi = create_OpARx_instruction("lar",0, F1=1)
# # SARd = create_OpARx_instruction("sar",16)
SARi = create_OpARx_instruction("sar",0b10000)
SARi1 = create_OpARx_instruction("sar",0b1000, S=1)
LARi = create_OpARx_instruction("lar", 0)

#sar arx,#k
class ARx_k_Instruction(OpARxInstruction):
    tokens = [c240x_arx_k]
def create_arx_k_instruction(mne, opcode):
    arx = Operand("arx", src_modes)
    k = Operand("k", src_modes)
    patterns = {"opcode":opcode}
    syntax = Syntax([mne, " ", arx, ",", " ",k])
    members = {
        "arx":arx,
        "k":k,
        "opcode":opcode,
        "syntax":syntax,
        "patterns":patterns,
    }
    return type(mne.title(), (ARx_k_Instruction,), members)

LARk = create_arx_k_instruction("lark", 0b10110)

#lar arx,ind,arn
class ARx_ind_arn_Instruction(OpARxInstruction):
    tokens = [c240x_arx_ind_arn]

def create_arx_ind_arn_instruction(mne, opcode, A=0 , N=1):
    arx = Operand("arx", src_modes)
    ind = Operand("ind", Ptr_modes)
    arn = Operand("arn", dst_modes)
    patterns = {"opcode":opcode }
    syntax = Syntax([mne, " ", arx, ",",ind, ","," ",arn])
    members = {
        "arx":arx,
        "ind":ind,
        "arn":arn,
        "opcode":opcode,
        "A":A,
        "N":N,
        "syntax":syntax,
        "patterns":patterns,
    }
    return type(mne.title(), (ARx_ind_arn_Instruction,), members)

LARi_arn = create_arx_ind_arn_instruction("lar", 0)

#-------------------------------------------------
class B_pma_Instruction(c240xInstruction):
    tokens = [c240x_b_pma_Token]

    opcode = bit_range(7, 16)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)
def create_b_pma_instruction(mne, opcode):
    pma = Operand("pma", src_modes)
    ARU = Operand("ARU", Ptr_modes)
    NAR = Operand("NAR", dst_modes)
    syntax = Syntax([mne, " ", pma, ",", " ",ARU, ","," ", NAR])
    patterns = { "opcode":opcode,  "N":1, "NAR":1}
    members ={ 
        "pma":pma, 
        "opcode":opcode,  
        "ARU":ARU, 
        "N":1, 
        "NAR":NAR, 
        "syntax":syntax, 
        "patterns":patterns}
    return type(mne.title(), (B_pma_Instruction,), members)

B = create_b_pma_instruction("b", 0b011110011)
# def  create_OpARx_instruction(mne, opcode, F1=0,dst_read=True, dst_write=True):
#     """ Factory function to define a Operating ARx Instruction """

#     Op2 = Operand("Op2", c240xRegister,read=True, write=True)
#     Aru = c240xLSARxDImodeToken.ARU
#     n = c240xLSARxDImodeToken.N
#     Nar = c240xLSARxDImodeToken.NAR
#     Op1 = Operand("Op1",str)
#     syntax = Syntax([mne, " ", Op2, ",", " ", Op1])
#     Op1 = switch_case(Aru)
#     syntax = Syntax([mne, " ", Op2, ",", " ", Op1])    
#     patterns = {"opcode": opcode, "Op2": Op2, "F1": F1, "Op1": Op1}
#     members = {
#         "opcode": opcode,
#         "syntax": syntax,
#         "Op1": Op1,
#         "Op2": Op2,
#         "patterns": patterns,
#     }
#     return type(mne.title(), (OpARxInstruction,), members)
# SARi = create_OpARx_instruction("sar",16,0)


# class SARi(c240xInstruction):
#     tokens = [c240xLSARxDImodeToken]
#     ARU = bit_range(4,7)
#     N = bit(3)
#     NAR = bit_range(0,3)
#     F1 = 0
#     Op1 = Operand(" ",str)
#     Op2 = Operand("Op2", c240xStackFrameRegister,read=True, write=True)
#     syntax = Syntax(["sari", " ", Op2, ",", " ", Op1]) 
#     # if N == 0 :
#     #         Op1 = switch_case(ARU).get(ARU, lambda: None)()
#     #         syntax = Syntax(["sari", " ", Op2, ",", " ", Op1])    
#     # elif N == 1 :
#     #         ARn = switch_case1(NAR).get(NAR, lambda: None)()
#     #         Op1 = switch_case(ARU).get(ARU, lambda: None)()
#     #         syntax = Syntax(["sari", " ", Op2, ",", " ", Op1, ARn]) 
#     patterns = {"opcode":16,"F1":0}

# class LARk(c240xInstruction):
#     tokens = [c240ximm8ARxToken]
#     Op2 = Operand("Op2", c240xARnRegister,read=True, write=True)
#     Op1 = Operand("Op1",imm8Src)
#     syntax = Syntax(["lar", " ", Op2, ",", " ", Op1])
#     patterns = {"opcode":22}

def mov(src, dst):
    """ Move src into dst register """
    return SARi1(RegSrc(src),  RegDst(dst), ismove=True)

######## POPD/PSHD  #########
class c240xOpStackMemToken_debug(c240xToken):
    opcode = bit_range(8, 16)
    F1 = bit(7)
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)

class OpStackMemDIMode_debug_Instruction(c240xInstruction):
    tokens = [c240xOpStackMemToken_debug]

def  create_StackMemDIMode_debug_instruction(mne, opcode,F1=0b1, N=0b0, NAR=0b0):
    """ Factory function to define a opStack Instruction """
    ARU = Operand("ARU", Ptr_modes)
    NAR = Operand("NAR", dst_modes)
    syntax = Syntax([mne, " ",ARU,",", NAR])
    patterns = {"opcode": opcode,  "F1": F1, "N":N, "NAR":1}
    members = {"opcode": opcode, "syntax": syntax, "ARU": ARU, "NAR":NAR, "patterns": patterns}
    return type(mne.title(), (OpStackMemDIMode_debug_Instruction,), members)

# # POPDd = create_StackMemDIMode_instruction("popd",8,10)
POPDi = create_StackMemDIMode_debug_instruction("popd", 0b10001010)
# # PSHDd = create_StackMemDIMode_instruction("pshd",7,6)
# # PSHDi = create_StackMemDIMode_instruction("pshd",7,6,F1=1)
# def  create_StackMemDIMode_instruction(mne,Func4, opcode,F1=0, dst_read=True, dst_write=True):
#     """ Factory function to define a opStack Instruction """
#     Aru = c240xOpStackMemToken.ARU
#     n = c240xOpStackMemToken.N
#     Nar = c240xOpStackMemToken.NAR

#     Op = Operand("Op",str)
#     syntax = Syntax([mne, " ", ",", " ", Op])
#     if F1 :
#         Op = Operand("Op", AdrSrc7)
#         syntax = Syntax([mne, " ", ",", " ", Op])    
#     else :
#         if n == 0 :
#             Op = switch_case(Aru)
#             syntax = Syntax([mne, " ",  ",", " ", Op])    

#         elif n == 1 :
#             ARn = switch_case1(Nar)
#             Op = switch_case(Aru)
#             syntax = Syntax([mne, " ",  ",", " ", Op, ARn]) 
#     patterns = {"Func4": Func4,"opcode": opcode,  "F1": F1,"Op": Op }
  
#     members = {
#         "Func4": Func4,
#         "opcode": opcode,
#         "syntax": syntax,
#         "Op": Op,
#         "patterns": patterns,
#     }
#     return type(mne.title(), (OpStackMemDIMode_debug_Instruction,), members)

# POPDd = create_StackMemDIMode_instruction("popd",8,10)
# POPDi = create_StackMemDIMode_instruction("popd",8,10,F1=1)
# PSHDd = create_StackMemDIMode_instruction("pshd",7,6)
# PSHDi = create_StackMemDIMode_instruction("pshd",7,6,F1=1)


def pop(reg):
    # """ Push register helper """
    # return POPD(RegSrc(reg))
    pass
######## RET #########

class RET(c240xInstruction):
    tokens = [c240xRETToken]
    syntax = Syntax(["ret"])
    patterns = {"Func4":14, "opcode":15, "Func8":0}

######## imm8 address mode instructions #########

class imm8AdrModeInstruction(c240xInstruction):
    tokens =[c240ximm8ModeToken]

def create_imm8AdrMode_instruction(mne,Func4,opcode):
    modes = Operand("modes", src_modes)
    # imm = Operand("imm",int)
    patterns = {"Func4": Func4, "opcode": opcode}
    syntax = Syntax([mne, " ", modes])
    # syntax = Syntax([mne, " ", imm])
    members = {
        # "imm": imm,
        "modes":modes,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (imm8AdrModeInstruction,), members)


SBRk = create_imm8AdrMode_instruction("sbrk",7,12)
##  to   do  do  




######################  PMA address Mode  instruction  #####################

# class PMAModeInstruction(c240xInstruction):
#     tokens = [c240xPMAToken]
    
# def  create_PMAMode_instruction(mne,Func4, opcode, F1=1, dst_read=True, dst_write=True):
#     """ Factory function to define a opStack Instruction """
#     pma = Operand("pma", PMAaddress)
#     Aru = c240xPMAToken.ARU
#     n = c240xPMAToken.N
#     Nar = c240xPMAToken.NAR
#     Op = Operand(" ",str)
#     syntax = Syntax([mne, " ", pma, ",", " ", Op])
#     if n == 0 :
#             Op = switch_case(Aru).get(Aru, lambda: None)()
#             syntax = Syntax([mne, " ", pma, ",", " ", Op])    

#     elif n == 1:
#             ARn = switch_case1(Nar).get(Nar, lambda: None)()
#             Op = switch_case(Aru).get(Aru, lambda: None)()
#             syntax = Syntax([mne, " ", pma, ",", " ", Op, ARn]) 
#     patterns = {"Func4": Func4,"opcode": opcode,  "F1": F1,"Op": Op }
#     members = {
#         "Func4": Func4,
#         "opcode": opcode,
#         "syntax": syntax,
#         "Op": Op,
#         "patterns": patterns,
       
#     }
#     return type(mne.title(), (PMAModeInstruction,), members)

# CAll = create_PMAMode_instruction("call",7,10)
   




############################################################
# 2022/12/12
############################################################

########################################
#####指令定义
########################################
#1
class dmaInstruction(c240xInstruction):
    tokens = [c240xdmaToken]

def create_dma_instruction(mne,opcode):
    imm = Operand("imm", int)
    patterns = {"opcode":opcode, "imm":imm}
    syntax = Syntax([mne, " ", imm])
    members = {
        "opcode": opcode,
        "imm": imm,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (dmaInstruction,), members)
Addc_dma = create_dma_instruction("addc", 0b011111110)
Adds_dma = create_dma_instruction("adds", 0b011000100)
Addt_dma = create_dma_instruction("addt", 0b011000110)
And_dma = create_dma_instruction("and", 0b011011100)
Lacl_dma = create_dma_instruction("lacl", 0b011010010)
Lact_dma = create_dma_instruction("lact", 0b011010110)
Or_dma = create_dma_instruction("or", 0b011011010)
Subb_dma = create_dma_instruction("subb", 0b011001000)
Subc_dma = create_dma_instruction("subc", 0b000010100)
Subs_dma = create_dma_instruction("subs", 0b011001100)
Subt_dma = create_dma_instruction("subt", 0b011001110)
Xor_dma = create_dma_instruction("xor", 0b011011000)
Zalr_dma = create_dma_instruction("zalr", 0b011010000)
Lph_dma = create_dma_instruction("lph", 0b011101010)
Lt_dma = create_dma_instruction("lt", 0b011100110)
Lta_dma = create_dma_instruction("lta", 0b011100000)
Ltd_dma = create_dma_instruction("ltd", 0b011100100)
Ltp_dma = create_dma_instruction("ltp", 0b011100010)
Lts_dma = create_dma_instruction("lts", 0b011101000)
Mpy_dma = create_dma_instruction("mpy", 0b010101000)
Mpya_dma = create_dma_instruction("mpya", 0b010100000)
Mpys_dma = create_dma_instruction("mpys", 0b010100010)
MPyu_dma = create_dma_instruction("mpyu", 0b010101010)
Sph_dma = create_dma_instruction("sph", 0b100011010)
Spl_dma = create_dma_instruction("spl", 0b100011000)
Sqra_dma = create_dma_instruction("sqra", 0b010100100)
Sqrs_dma = create_dma_instruction("sqrs", 0b010100110)
Mar_dma = create_dma_instruction("mar", 0b100010110)
Bitt_dma = create_dma_instruction("bitt", 0b011011110)
Ldp_dma = create_dma_instruction("ldp", 0b000011010)
# Popd_dma = create_dma_instruction("popd", 0b100010100)
Pshd_dma = create_dma_instruction("pshd", 0b011101100)
Rpt_dma = create_dma_instruction("rpt", 0b000010110)
Dmov_dma = create_dma_instruction("dmov", 0b011101110)
Tblr_dma = create_dma_instruction("tblr", 0b101001100)
Tblw_dma = create_dma_instruction("tblw", 0b101001110)
Add_dma = create_dma_instruction("add", 0b001000000)
Lacc_dma = create_dma_instruction("lacc", 0b000100000)



#2
class shiftdmaInstruction(c240xInstruction):
    tokens = [c240xshiftdmaToken]

def create_shiftdma_instruction(mne,opcode,imm1):
    shift = Operand("shift", int)
    imm2 = Operand("imm2", int)
    patterns = {"opcode":opcode, "shift":shift, "imm1":imm1, "imm2":imm2}
    syntax = Syntax([mne, " ",imm2, ",", shift])
    members = {
        "opcode": opcode,
        "imm1":imm1,
        "imm2": imm2,
        "shift":shift,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (shiftdmaInstruction,), members)

Add_dma_shift = create_shiftdma_instruction("add", 0b0010, 0)
Lacc_dma_shift = create_shiftdma_instruction("lacc", 0b0001, 0)

#3
class Abs(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["abs"])
    patterns = {"opcode":0b1011111000000000}

class And_lk(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["and", " ", "#", "lk", ",", "sixteen"])
    patterns = {"opcode":0b1011111010000001}

class Cmpl(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["cmpl"])
    patterns = {"opcode":0b1011111000000001}

class Or_lk(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["or", " ", "#", "lk", ",", "sixteen"])
    patterns = {"opcode":0b1011111010000010}

class Rol(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["rol"])
    patterns = {"opcode":0b1011111000001100}

class Ror(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["ror"])
    patterns = {"opcode":0b1011111000001101}

class Sfl(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["sfl"])
    patterns = {"opcode":0b101111100001001}

class Sfr(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["sfr"])
    patterns = {"opcode":0b1011111000001010}

class Xor_lk(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["xor", " ", "#", "lk", ",", "sixteen"])
    patterns = {"opcode":0b1011111010000011}

class Apac(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["apac"])
    patterns = {"opcode":0b1011111000000100}

class Pac(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["pac"])
    patterns = {"opcode":0b1011111000000011}

class Spac(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["spac"])
    patterns = {"opcode":0b1011111000000101}

class Bacc(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["bacc"])
    patterns = {"opcode":0b1011111000100000}

class Cala(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["cala"])
    patterns = {"opcode":0b1011111000110000}

class Nmi(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["nmi"])
    patterns = {"opcode":0b1011111001010010}

class Ret(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["ret"])
    patterns = {"opcode":0b1110111100000000}

class Clrc_c(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["clrc", " ", "c"])
    patterns = {"opcode":0b1011111001001110}

class Clrc_cnf(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["clrc", " ", "cnf"])
    patterns = {"opcode":0b1011111001000100}

class Clrc_intm(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["clrc", " ", "intm"])
    patterns = {"opcode":0b1011111001000000}

class Clrc_ovm(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["clrc", " ", "ovm"])
    patterns = {"opcode":0b1011111001000010}

class Clrc_sxm(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["clrc", " ", "sxm"])
    patterns = {"opcode":0b1011111001000110}

class Clrc_tc(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["clrc", " ", "tc"])
    patterns = {"opcode":0b1011111001001010}

class Clrc_xf(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["clrc", " ", "xf"])
    patterns = {"opcode":0b1011111001001100}

class Idle(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["idle"])
    patterns = {"opcode":0b1011111000100010}

class Nop(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["nop"])
    patterns = {"opcode":0b1000101100000000}

class Pop(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["pop"])
    patterns = {"opcode":0b1011111000110010}

class Push(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["push"])
    patterns = {"opcode":0b1011111000111100}

class Setc_c(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["setc", " ", "c"])
    patterns = {"opcode":0b1011111001001111}

class Setc_cnf(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["setc", " ", "cnf"])
    patterns = {"opcode":0b1011111001000101}

class Setc_intm(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["setc", " ", "intm"])
    patterns = {"opcode":0b1011111000100001}

class Setc_ovm(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["setc", " ", "ovm"])
    patterns = {"opcode":0b1011111001000011}

class Setc_sxm(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["setc", " ", "sxm"])
    patterns = {"opcode":0b1011111001000111}

class Setc_tc(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["setc", " ", "tc"])
    patterns = {"opcode":0b1011111001001011}

class Setc_xf(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["setc", " ", "xf"])
    patterns = {"opcode":0b1011111001001101}

class ADD_lk(c240xInstruction):
    tokens = [c240x_con16]
    syntax = Syntax(["add", " ","#", "lk"])
    patterns = {"opcode":0b1011111110010000}

#4
class imm8kInstruction(c240xInstruction):
    tokens = [c240x_imm8k]
#ADD #k                                              1011 1000 K
def create_imm8k_instruction(mne,opcode):
    NAR = Operand("NAR", src_modes)
    patterns = { "opcode":opcode }
    syntax = Syntax([mne, " ",NAR])
    members = {
        "opcode": opcode,
        "NAR":NAR,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (imm8kInstruction,), members)

Add_k = create_imm8k_instruction("add", 0b10111000)
Adrk_k = create_imm8k_instruction("adrk", 0b01111000)
Lacl_k = create_imm8k_instruction("lack", 0b10111001)
Sub_k = create_imm8k_instruction("sub", 0b10111010)

#4_1
#mpy ind,ARn
class imm13kInstruction(c240xInstruction):
    tokens = [c240xLSARxDImodeToken]


def create_imm13k_instruction(mne,opcode,X,F1,N=1):
    Aru = Operand("Aru", Ptr_modes)
    NAR = Operand("NAR", dst_modes)
    # ARU = Operand("ARU", c240xRegister, write=True)
    # NAR = Operand("NAR", c240xRegister, read=True)
    syntax = Syntax([mne, " ", Aru, ",",NAR])
    patterns = {"opcode":opcode,  "X":X,  "F1":F1,  "N":N}
    members = {
        "opcode": opcode,
        "Aru":Aru,
        "NAR":NAR,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (imm13kInstruction,), members)

mpy_ind_ARn = create_imm13k_instruction("mpy", 0b0101,0b0100,1)
SUBC_ind_ARn = create_imm13k_instruction("subc", 0,0b1010,1)
PSHD_ind_ARn = create_imm13k_instruction("pshd", 0b0111, 0b0110, 1)
mar_ind_arn = create_imm13k_instruction("mar", 0b1000,0b1011,1)
#4_1_2
#sacl ind
class ind_shift2_arn_Instruction(c240xInstruction):
    tokens = [c240x_ind_shift2_arn]

def create_ind_shift2_arn_instruction(mne,opcode,shift2=0,a=1,N=1,NAR=0):
    NAR = Operand("NAR", Ptr_modes)
    # ARU = Operand("ARU", c240xRegister, write=True)
    # NAR = Operand("NAR", c240xRegister, read=True)
    syntax = Syntax([mne, " ",NAR])
    patterns = {"opcode":opcode,  "shift2":shift2,  "a":a,  "N":N, "NAR":NAR}
    members = {
        "opcode": opcode,
        "NAR":NAR,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (ind_shift2_arn_Instruction,), members)

SACl = create_ind_shift2_arn_instruction("sacl", 0b10010)

#4_2 
#CMPR CM
class cmprcm_Instruction(c240xInstruction):
    tokens = [c240xCMPRToken]

def create_cmprcm_instruction(mne, opcode):
    cm = Operand("cm", int)
    syntax = Syntax([mne, " ",cm])
    patterns = {"opcode":opcode, "cm":cm}
    members  = { "opcode":opcode, "cm":cm, "syntax":syntax, "patterns":patterns}
    return type(mne.title(), (cmprcm_Instruction,), members)

Cmpr = create_cmprcm_instruction("cmpr", 0b10111111010001)




#5 (32bit)
class lkshfitInstruction(c240xInstruction):
    tokens = [c240x_lkshift_Token]

def create_lkshift_instruction(mne,opcode):
    lk = Operand("lk", int)
    imm = Operand("imm",  c240xARnRegister,write = True)
    #imm = Operand("imm", int)
    patterns = {"lk":lk, "opcode":opcode, "imm":imm}
    syntax = Syntax([mne, " ","#", lk, ",", imm])
    members = {
        "opcode": opcode,
        "lk":lk,
        "imm":imm,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (lkshfitInstruction,), members)

Add_lkshift = create_lkshift_instruction("add", 0b101111111001)
And_lkshift = create_lkshift_instruction("and", 0b101111111011)
Lacc_lkshift = create_lkshift_instruction("lacc", 0b101111111000)
Or_lkshift = create_lkshift_instruction("or", 0b101111111100)
Sub_lkshift = create_lkshift_instruction("sub", 0b101111111010)
Xor_lkshift = create_lkshift_instruction("xor", 0b101111111101)


########################################
#####指令选择
########################################

###############################  Instruction selection #######################

# @isa.pattern("stm", "STRI16(memdst, src)", size=1)
# @isa.pattern("stm", "STRU16(memdst, src)", size=1)
# def pattern_str16(context, tree, c0, c1):
#     d = context.new_reg(c240xARnRegister)   #Arn寄存器组
#     context.emit(mov(c1, d))
#     context.emit(SARd(c1, c0))


# @isa.pattern("stm", "STRI16(memdst, src)", size=1)
# @isa.pattern("stm", "STRU16(memdst, src)", size=1)
# def pattern_str16(context, tree, c0, c1):
#     =c0
#     =c0
#     context.emit(SARd(c1, c0))



# Relocation functions:
# @isa.register_relocation
# class Rel10Relocation(Relocation):
#     """ Apply 10 bit signed relocation """

#     name = "rel10"
#     token = c240xJumpToken
#     field = "offset"

#     def calc(self, sym_value, reloc_value):
#         assert sym_value % 2 == 0
#         offset = (sym_value - (align(reloc_value, 2)) - 2) >> 1
#         assert offset in range(-511, 511, 1), str(offset)
#         return offset




#---------指令选择补充-------2023/1/30#

# class DstImmToken(c240xToken):
#     dstimm = bit_range(0, 16)

# class ConstSrc(Src):
#     """ Equivalent to @PC+ """

#     tokens = [Imm16Token]
#     syntax = Syntax(["#", Src.imm])
#     is_special = True
#     patterns = {"source": 0, "srcimm": Src.imm}

# class MemDst(Dst):
#     """  register offset memory access, for example: 0x88(R8) """

#     tokens = [DstImmToken]
#     syntax = Syntax([Dst.imm, "(", Dst.reg, ")"])
#     patterns = {"Ad": 1, "destination": Dst.reg, "dstimm": Dst.imm}

# @isa.pattern("cnst", "CONSTI8", size=0, cycles=0, energy=0)
# @isa.pattern("cnst", "CONSTU8", size=0, cycles=0, energy=0)
# @isa.pattern("cnst", "CONSTI16", size=0, cycles=0, energy=0)
# @isa.pattern("cnst", "CONSTU16", size=0, cycles=0, energy=0)
# def pattern_cnst(context, tree):
#     return tree.value
# #----------------------
# @isa.pattern("memdst", "reg", size=2, cycles=0, energy=0)
# def pattern_mem_dst(context, tree, c0):
#     return MemDst(0, c0)

# @isa.pattern("memdst", "ADDU16(reg, cnst)", size=2, cycles=0, energy=0)
# def pattern_mem_dst_const(context, tree, c0, c1):
#     return MemDst(c1, c0)

# @isa.pattern("memdst", "FPRELU16", size=2, cycles=0, energy=0)
# def pattern_memdst_fprel(context, tree):
#     offset = tree.value.offset
#     # frame pointer is not used, use stack pointer
#     return MemDst(offset, SP)
# #-----------------------------
# @isa.pattern("reg", "src16", size=4, cycles=1, energy=1)
# def pattern_fill_reg16(context, tree, c0):
#     dst = context.new_reg(c240xARnRegister)
#     context.emit(mov(c0, RegDst(dst)))
#     return dst

# @isa.pattern("src16", "cnst", size=2, cycles=0, energy=0)
# def pattern_cnst_src(context, tree, c0):
#     return ConstSrc(c0)


# @isa.pattern("stm", "STRI16(FPRELU16, cnst)", size=2)
# @isa.pattern("stm", "STRU16(cnst, cnst)", size=2)
# def pattern_str16(context, tree, c0, c1):
#     return mov(c1, c0)


# @isa.pattern("stm", "STRI16(memdst, src16)", size=2)
# @isa.pattern("stm", "STRU16(memdst, src16)", size=2)
# def pattern_str16(context, tree, c0, c1):
#     context.emit(mov(c1, c0))

#-----------------------------------------------------
# mem已经定义成reg，接下来是如何让reg寄存器的内容指向mem地址的问题
#-----------------------------------------------------



#-----------------------------------------------------
# 简单的指令选择
#-----------------------------------------------------

@isa.pattern("stm", "JMP", size=4)
def pattern_jmp(context, tree):
    print("1078", )
    d = context.new_reg(c240xRegister)
    tgt = tree.value
    context.emit(B( RegSrc(d), PtrMode2(), RegDst(d)))

@isa.pattern("stm", "CJMPI16(reg, reg)", size=10)
def pattern_cjmp_i16(context, tree, lhs, rhs):
    print("1084")
    op, true_tgt, false_tgt = tree.value
    emit_cmp(context, Cmpr, lhs, rhs, op, true_tgt, false_tgt)


@isa.pattern("stm", "CJMPI8(reg, reg)", size=10)
def pattern_cjmp_i8(context, tree, lhs, rhs):
    print("1090")
    pass


def emit_cmp(context, cmp_ins, lhs, rhs, op, true_tgt, false_tgt):
    opnames = {
        "<": (Jl, False, 1),
        ">": (Jl, True, 2),
        "==": (Jz, False, 0),
        "!=": (Jne, False, 3),
        ">=": (Jge, False, 4),
        "<=": (Jge, True, 5),
    }
    op_ins, swap_ops, cm = opnames[op]
    if swap_ops:
        # Swap operands here!
        # This is really hairy code, but it should work!
        lhs, rhs = rhs, lhs
    print("1108", false_tgt.name, [false_tgt])
    d = context.new_reg(c240xRegister)
    jmp_ins = B(false_tgt.name, PtrMode2(), RegDst(d),jumps=[false_tgt])
    # cmp does a dummy dst - src
    context.emit(cmp_ins(cm))
    context.emit(op_ins(true_tgt.name, jumps=[true_tgt, jmp_ins]))
    context.emit(jmp_ins)


@isa.pattern("stm", "MOVI16(reg)", size=2, cycles=1, energy=1)
@isa.pattern("stm", "MOVU16(reg)", size=2, cycles=1, energy=1)
def pattern_mov16(context, tree, c0):
    print("1119 =", tree.value, c0)
    dst = tree.value
    # c0 = AR0
    context.emit(SACl(PtrMode1()))
    # pass


@isa.pattern("stm", "MOVI8(reg)", size=2)
@isa.pattern("stm", "MOVU8(reg)", size=2)
def pattern_mov8(context, tree, c0):
    print("1129")
    dst = tree.value
    # c0 = AR0
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # pass

@isa.pattern("cnst", "CONSTI8", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTU8", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTI16", size=0, cycles=0, energy=0)
@isa.pattern("cnst", "CONSTU16", size=0, cycles=0, energy=0)
def pattern_cnst(context, tree):
    print("1140  =", tree.value)
    return tree.value


@isa.pattern("src8", "cnst", size=2, cycles=0, energy=0)
@isa.pattern("src16", "cnst", size=2, cycles=0, energy=0)
def pattern_cnst_src(context, tree, c0):
    print("1147 =", imm_Src(c0), c0)
    return imm_Src(c0)
    # return int(c0)

# TODO: this would be good for small constant values:
# @isa.pattern(
#     "src", "cnst", size=0, cycles=0, energy=0,
#     condition=lambda t: t in small_const_src_values
# )
# def pattern_small_cnst_src(context, tree, c0):
#     return small_const_src(c0)


@isa.pattern("src8", "reg", size=0, cycles=0, energy=0)
@isa.pattern("src16", "reg", size=0, cycles=0, energy=0)
def pattern_reg_src(context, tree, c0):
    # c0 =  AR2
    print("1164 =", tree.value, c0, RegSrc(c0))
    return RegSrc(c0)



@isa.pattern("reg", "src16", size=4, cycles=1, energy=1)
def pattern_fill_reg16(context, tree, c0):
    dst = context.new_reg(c240xRegister)
    # c0 = AR0
    print("1173", context, tree.value, c0, dst)
    # context.emit(SARi(c0, RegDst(dst)))
    #把值放入reg
    context.emit(LARk(c0, imm8Src(1)))
    return dst



@isa.pattern("reg", "src8", size=4, cycles=1, energy=1)
def pattern_fill_reg8(context, tree, c0):
    print("1182")
    dst = context.new_reg(c240xRegister)
    context.emit(SARi(c0, PtrMode2 ))
    return dst


@isa.pattern("reg", "REGI8", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU8", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGI16", size=0, cycles=0, energy=0)
@isa.pattern("reg", "REGU16", size=0, cycles=0, energy=0)
def pattern_reg16(context, tree):
    print("1193 =", tree.value)
    return tree.value


@isa.pattern("reg", "I16TOI8(reg)", size=0, cycles=0, energy=0)
@isa.pattern("reg", "I16TOU8(reg)", size=0, cycles=0, energy=0)
def pattern_i16toi8(context, tree, c0):
    print("1200")
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Andw(ConstSrc(0xFF), RegDst(d)))
    return tree.value


@isa.pattern("reg", "I8TOI16(reg)", size=0, cycles=0, energy=0)
def pattern_i8toi16(context, tree, c0):
    print("1209")
    """ Sign extend signed byte to signed short """
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Sxt(RegSrc(d)))
    return d


@isa.pattern("reg", "U8TOI16(reg)", size=0, cycles=0, energy=0)
def pattern_u8toi16(context, tree, c0):
    print("1219")
    """ byte to signed short """
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Andw(ConstSrc(0xFF), RegDst(d)))
    return d


def call_intrinsic(context, label, args, clobbers=()):
    """ Generate a call to an intrinsic function """
    pass


@isa.pattern("reg", "MULI16(reg, reg)", size=10)
def pattern_mul_i16(context, tree, c0, c1):
    d = context.new_reg(c240xRegister)
    print("1234 =", tree.value, c0, c1)  
    # context.emit(mpy_ind_ARn(RegSrc(c0),RegDst(c1)))
    return d
    # context.emit(mpy_ind_ARn(RegSrc(c0),RegDst(c1)))

@isa.pattern("reg", "MULU16(reg, reg)", size=10)
def pattern_mul_u16(context, tree, c0, c1):
    print("1240 =", tree.value, c0, c1)  
    # context.emit(mpy_ind_ARn(RegSrc(c0),RegDst(c1)))


@isa.pattern("reg", "DIVI16(reg, reg)", size=10)
def pattern_div_i16(context, tree, c0, c1):
    d = context.new_reg(c240xRegister)
    print("1234 =", tree.value, c0, c1)  
    # context.emit(SUBC_ind_ARn(RegSrc(c0),RegDst(c1)))
    return d


@isa.pattern("reg", "DIVU16(reg, reg)", size=10)
def pattern_div_u16(context, tree, c0, c1):
    print("1252 =", tree.value, c0, c1)  
    d = context.new_reg(c240xRegister) 
    # context.emit(SUBC_ind_ARn(RegSrc(c0),RegDst(c1)))
    return d


@isa.pattern("reg", "REMI16(reg, reg)", size=10)
def pattern_rem_i16(context, tree, c0, c1):
    print("1257 =", tree.value, c0, c1)  
    return tree.value

@isa.pattern("reg", "REMU16(reg, reg)", size=10)
def pattern_rem_u16(context, tree, c0, c1):
    print("1262 =", tree.value, c0, c1)  
    return tree.value

@isa.pattern("reg", "ANDI16(reg, src16)", size=4)
@isa.pattern("reg", "ANDU16(reg, src16)", size=4)
def pattern_and16(context, tree, c0, c1):
    print("1268 =", tree.value, c0, c1)  
    dst = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Andw(c1, RegDst(dst)))
    return dst

@isa.pattern("reg", "ANDI8(reg, src8)", size=4)
@isa.pattern("reg", "ANDU8(reg, src8)", size=4)
def pattern_and8(context, tree, c0, c1):
    print("1277 =", tree.value, c0, c1)  
    dst = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Andb(c1, RegDst(dst)))
    return dst

@isa.pattern("reg", "ORI16(reg, src16)", size=4)
@isa.pattern("reg", "ORU16(reg, src16)", size=4)
def pattern_or16(context, tree, c0, c1):
    print("1286 =", tree.value, c0, c1)  
    dst = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Bisw(c1, RegDst(dst)))
    return dst


@isa.pattern("reg", "ORI8(reg, src8)", size=4)
@isa.pattern("reg", "ORU8(reg, src8)", size=4)
def pattern_or8(context, tree, c0, c1):
    print("1296 =", tree.value, c0, c1)  
    dst = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Bisb(c1, RegDst(dst)))
    return dst

@isa.pattern("reg", "SHRI16(reg, reg)", size=4)
@isa.pattern("reg", "SHRU16(reg, reg)", size=4)
@isa.pattern("reg", "SHRI8(reg, reg)", size=4)
@isa.pattern("reg", "SHRU8(reg, reg)", size=4)
def pattern_shr16(context, tree, c0, c1):
    print("1307 =", tree.value, c0, c1)  
    return tree.value



@isa.pattern("reg", "SHLI16(reg, reg)", size=4)
@isa.pattern("reg", "SHLU16(reg, reg)", size=4)
def pattern_shl16(context, tree, c0, c1):
    print("1315 =", tree.value, c0, c1)  
    return tree.value


@isa.pattern("reg", "SHLI8(reg, reg)", size=4)
@isa.pattern("reg", "SHLU8(reg, reg)", size=4)
def pattern_shl8(context, tree, c0, c1):
    print("1322 =", tree.value, c0, c1)  
    return tree.value



@isa.pattern("reg", "ADDI8(reg, src8)", size=4, cycles=1, energy=1)
@isa.pattern("reg", "ADDU8(reg, src8)", size=4, cycles=1, energy=1)
def pattern_add8(context, tree, c0, c1):
    print("1330 =", tree.value, c0, c1)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    context.emit(Add_k(imm8Src(c1)))
    return d

@isa.pattern("reg", "ADDI16(reg, src16)", size=4, cycles=1, energy=1)
@isa.pattern("reg", "ADDU16(reg, src16)", size=4, cycles=1, energy=1)
def pattern_add16(context, tree, c0, c1):
    print("1339 =", tree.value, c0, c1)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    context.emit(Add_k(c1))
    return d
    # pass


@isa.pattern("reg32", "ADDI32(reg32, reg32)", size=8, cycles=2, energy=2)
@isa.pattern("reg32", "ADDU32(reg32, reg32)", size=8, cycles=2, energy=2)
def pattern_add32(context, tree, c0, c1):
    print("1350 =", tree.value, c0, c1)  
    # dl = context.new_reg(c240xRegister)
    # c1l = c1
    # context.emit(Addw(RegSrc(c1l), RegDst(dl)))
    # return dl    
    pass



@isa.pattern("reg", "SUBI8(reg, src8)", size=4)
@isa.pattern("reg", "SUBU8(reg, src8)", size=4)
def pattern_sub8(context, tree, c0, c1):
    print("1362 =", tree.value, c0, c1)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    context.emit(Sub_k(c1))
    return d



@isa.pattern("reg", "SUBI16(reg, src16)", size=4)
@isa.pattern("reg", "SUBU16(reg, src16)", size=4)
def pattern_sub16(context, tree, c0, c1):
    print("1373 =", tree.value, c0, c1)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    print("1336=", c1)
    context.emit(Sub_k(c1))
    return d



@isa.pattern("reg32", "SUBI32(reg32, reg32)", size=8)
@isa.pattern("reg32", "SUBU32(reg32, reg32)", size=8)
def pattern_sub32(context, tree, c0, c1):
    print("1385 =", tree.value, c0, c1)  
    return tree.value



@isa.pattern("reg", "NEGI8(src8)", size=4)
@isa.pattern("reg", "NEGU8(src8)", size=4)
def pattern_neg8(context, tree, c0):
    print("1393 =", tree.value, c0)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(imm8Src(0), PtrMode2() ))
    context.emit(Sub_k(c0))
    return d


@isa.pattern("reg", "NEGI16(src16)", size=4)
@isa.pattern("reg", "NEGU16(src16)", size=4)
def pattern_neg16(context, tree, c0):
    print("1403 =", tree.value, c0)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(imm8Src(0), PtrMode2() ))
    context.emit(Sub_k(c0))
    return d


@isa.pattern("reg", "INVU8(reg)", size=4)
def pattern_inv8(context, tree, c0):
    print("1412 =", tree.value, c0)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Xorb(SmallConstSrc(-1), RegDst(d)))
    return d



@isa.pattern("reg", "INVU16(reg)", size=4)
def pattern_inv16(context, tree, c0):
    print("1422 =", tree.value, c0)  
    d = context.new_reg(c240xRegister)
    context.emit(SARi(RegSrc(c0), PtrMode2()))
    # context.emit(Xorw(SmallConstSrc(-1), RegDst(d)))
    return d




@isa.pattern("memdst", "reg", size=2, cycles=0, energy=0)
def pattern_mem_dst(context, tree, c0):
    print("1433 =", tree.value, c0)  
    return RegDst(c0)


@isa.pattern("memdst", "ADDU16(reg, cnst)", size=2, cycles=0, energy=0)
def pattern_mem_dst_const(context, tree, c0, c1):
    print("1439 =", tree.value, c0, c1)  
    return MemDst( c0 )



@isa.pattern("memdst", "FPRELU16", size=2, cycles=0, energy=0)
def pattern_memdst_fprel(context, tree):
    offset = tree.value.offset
    print("1447 =", tree.value, offset, MemDst( AR2 )) 
    # frame pointer is not used, use stack pointer
    return MemDst( AR2 )



@isa.pattern("stm", "STRI16(memdst, src16)", size=2)
@isa.pattern("stm", "STRU16(memdst, src16)", size=2)
def pattern_str16(context, tree, c0, c1):
    print("1456 =",c0,c1)
    context.emit(Lacl_k(c1))



@isa.pattern("stm", "STRI8(memdst, src8)", size=2)
@isa.pattern("stm", "STRU8(memdst, src8)", size=2)
def pattern_str8(context, tree, c0, c1):
    print("1462 =", tree.value, c0, c1) 
    context.emit(SARi(c1, PtrMode2() ))


class MemSrc(Src):
    """ Memory content """
    syntax = Syntax(["@", Src.reg])
    patterns = {"As": 2, "source": Src.reg}

@isa.pattern("memsrc", "reg", size=0, cycles=0, energy=0)
def pattern_mem_src(context, tree, c0):
    print("1473 =", tree.value, c0) 
    return MemSrc(c0)


@isa.pattern("memsrc", "ADDU16(reg, cnst)", size=2, cycles=0, energy=0)
def pattern_mem_src_offset(context, tree, c0, c1):
    print("1479 =", tree.value, c0, c1) 
    return tree.value


@isa.pattern("memsrc", "FPRELU16", size=2, cycles=0, energy=0)
def pattern_mem_src_fprel(context, tree):
    offset = tree.value.offset
    print("1485 =", tree.value, MemDst( AR2 ))
    return MemDst( AR2 )

@isa.pattern("src16", "LDRI16(memsrc)", size=2, cycles=3, energy=2)
@isa.pattern("src16", "LDRU16(memsrc)", size=2, cycles=3, energy=2)
def pattern_ldr16(context, tree, c0):
    print("1491 =", tree.value, c0) 
    return c0


@isa.pattern("src8", "LDRI8(memsrc)", size=2)
@isa.pattern("src8", "LDRU8(memsrc)", size=2)
def pattern_ldr8(context, tree, c0):
    print("1498 =", tree.value, c0) 
    return c0


@isa.pattern("reg", "FPRELU16", size=8, cycles=2, energy=2)
def pattern_fprel(context, tree):
    print("1504 =", tree.value) 
    d = context.new_reg(c240xRegister)
    offset = tree.value.offset
    # frame pointer is r4:
    context.emit(SARi(RegSrc(SP), PtrMode2() ))
    context.emit(Add_k(offset))
    return d


@isa.pattern("reg", "LABEL", size=2)
def pattern_label(context, tree):
    print("1515 =", tree.value) 
    d = context.new_reg(c240xRegister)
    # ln = context.frame.add_constant(tree.value)
    # context.emit(SARi(AdrSrc(ln), RegDst(d)))
    return d






#----------------------------------------------------------------
class c240x_dubug_JumpToken(c240xToken):
    opcode = bit_range(13, 16)
    condition = bit_range(10, 13)
    offset = bit_range(0, 10)

class JumpInstruction(c240xInstruction):
    tokens = [c240x_dubug_JumpToken]

    def gen_relocations(self):
        yield Rel10Relocation(self.target)


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
    
#------------------------临时使用
def create_jump_instruction(name, condition):
    target = Operand("target", str)
    syntax = Syntax([name, " ", target])
    patterns = {"condition": condition, "opcode": 1}
    members = {"syntax": syntax, "target": target, "patterns": patterns}
    return type(name.title(), (JumpInstruction,), members)

Jne = create_jump_instruction("jne", 0)
Jnz = create_jump_instruction("jnz", 0)
Jeq = create_jump_instruction("jeq", 1)
Jz = create_jump_instruction("jz", 1)
Jnc = create_jump_instruction("jnc", 2)
Jc = create_jump_instruction("jc", 3)
Jn = create_jump_instruction("jn", 4)
Jge = create_jump_instruction("jge", 5)
Jl = create_jump_instruction("jl", 6)
Jmp = create_jump_instruction("jmp", 7)

################################################################
# POPDi = create_jump_instruction("popdi", 8)
# SARi = create_jump_instruction("sari", 9)
# addb = create_jump_instruction("addb", 10)
# SBRk = create_jump_instruction("sbrk", 11)
# LARi = create_jump_instruction("lari", 12)
# PSHDi = create_jump_instruction("pshdi", 13)
# LARk =  create_jump_instruction("lark", 14)
CAll =  create_jump_instruction("call", 14)

