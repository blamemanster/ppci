""" Definitions of c240x instruction set. """

import opcode
from re import X
from webbrowser import Opera
from ..encoding import Instruction, Operand, Syntax, Constructor, Transform
from ..generic_instructions import ArtificialInstruction
from ..generic_instructions import RegisterUseDef, Global
from ..isa import Relocation, Isa
from ..token import Token, bit_range, bit
from .registers import c240xRegister,c240xStackFrameRegister,c240xARnRegister
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

class c240x32Token(Token):
    class Info:
        size = 32

class c240xInstruction(Instruction):
    isa = isa


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

class RegDst(Dst):
    is_reg_target = True
    syntax = Syntax([Dst.reg])
    patterns = {"destination": Dst.reg}

class SrcImm8Token(c240xTokenbit7):
    srcimm = bit_range(0, 8)

class DstImm8Token(c240xTokenbit7):
    dstimm = bit_range(0, 8)

class SrcImm7Token(c240xTokenbit7):
    srcimm = bit_range(0, 7)

class DstImm7Token(c240xTokenbit7):
    dstimm = bit_range(0, 7)

class Imm16Token(c240xToken):
    imm16 = bit_range(0,16)


################   imm  src/dst operand ############

# class imm8Src(Constructor):
#     tokens = [SrcImm8Token]
#     syntax = Syntax(["#",Src.imm])
#     is_special = True
#     patterns = {"source": 0, "srcimm": Src.imm}

########## dma address src/dst #############

# class AdrSrc7(Constructor):
#     """ absolute address """

#     is_special = True
#     addr = Operand("addr", str) 
#     tokens = [SrcImm7Token]
#     syntax = Syntax([addr])
#     patterns = { "source": 2}

class AdrDst7(Constructor):
    """ absolute address """

    is_special = True
    addr = Operand("addr", str)
    tokens = [DstImm7Token]
    syntax = Syntax([addr])
    patterns = { "destination": 2}

###### pma adrress operand###########
# class PMAaddress(Constructor):
#     """ absolute address """

#     is_special = True
#     addr = Operand("addr", str)
#     tokens = [Imm16Token]
#     syntax = Syntax([addr])
#     patterns = { "destination": 2 }


######## used for pointer mode operands for indirect address mode ##########
class PtrMode1(Constructor):
        is_special = True
        syntax = Syntax(["*"])

class PtrMode2(Constructor):
        is_special = True
        syntax = Syntax(["*", "-"])

class PtrMode3(Constructor):
        is_special = True
        syntax = Syntax(["*", "+"])
    
# class PtrMode4(Constructor):
#         is_special = True
#         syntax = Syntax(["*", "B","R","0", "-"])

# class PtrMode5(Constructor):
#         is_special = True
#         syntax = Syntax(["*", "0", "-"])

# class PtrMode6(Constructor):
#         is_special = True
#         syntax = Syntax(["*", "0", "+"])

# class PtrMode7(Constructor):
#         is_special = True
#         syntax = Syntax(["*", "BR0", "+"])

Ptr_modes = (
    PtrMode1,
    PtrMode2,
    PtrMode3,
    # PtrMode4,
    # PtrMode5,
    # PtrMode6,
    # PtrMode7,
)

def p1():
    return Operand("Op1", PtrMode1)
     
def p2():
    return Operand("Op1", PtrMode2)

def p3():
    return Operand("Op1", PtrMode3)

# def p4():
#     return Operand("Op1", PtrMode4)

# def p5():
#     return Operand("Op1", PtrMode5)

# def p6():
#     return Operand("Op1", PtrMode6)

# def p7():
#     return Operand("Op1", PtrMode7)


def switch_case(ARU):pass
"""
                return {
                    0:  p1(),          
                    1:  p2(),
                    2:  p3(),
                    # 4:  p4(),
                    # 5:  p5(),
                    # 6:  p6(),
                    # 7:  p7(),
            }.get(ARU, lambda: None)()
"""

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
    Op2 = bit_range(8, 11)
    F1 = bit(7)
    Op1 = bit_range(0,7)
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

"""         RET           """
class c240xRETToken(c240xToken):
    Func4 = bit_range(12,16)
    opcode = bit_range(8, 12)
    Func8 = bit_range(0,8)

"""       8bit imm      Format          """
class  c240ximm8ModeToken(c240xToken):
    Func4 = bit_range(12,16)
    opcode = bit_range(8, 12)
    Op = bit_range(0,8)

"""      8bit imm and ARX Format     """
class  c240ximm8ARxToken(c240xToken):
    opcode = bit_range(11,16)
    Op2 = bit_range(8, 11)
    Op1 = bit_range(0,8)

class c240xPMAToken(c240x32Token):
    Func4 = bit_range(12,16)
    opcode = bit_range(8, 12)
    F1 = bit(7)
    Op = bit_range(0,7)
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
    imm = bit_range(0,8)
#5  (32bit)
class c240x_lkshift_Token(c240x32Token):
    lk = bit_range(16, 32)
    opcode = bit_range(4,16)
    imm = bit_range(0,4)



############################# define instructions ###########################

####  ARx DIMode Instructions #####

# class OpARxInstruction(c240xInstruction):
#     tokens = [c240xLSARxDImodeToken]
   
# def  create_OpARx_instruction(mne, opcode, F1=0,dst_read=True, dst_write=True):
#     """ Factory function to define a Operating ARx Instruction """

#     Op2 = Operand("Op2", c240xARnRegister,read=True, write=True)
#     Aru = c240xLSARxDImodeToken.ARU
#     n = c240xLSARxDImodeToken.N
#     Nar = c240xLSARxDImodeToken.NAR
#     Op1 = Operand(" ",str)
#     syntax = Syntax([mne, " ", Op2, ",", " ", Op1])
#     if F1 :
#         Op1 = Operand("Op1", AdrSrc7)
#         syntax = Syntax([mne, " ", Op2, ",", " ", Op1])    
#     else :
#         if n == 0 :
#             Op1 = switch_case(Aru).get(Aru, lambda: None)()
#             # Op1 = switch_case(Aru)()
#             syntax = Syntax([mne, " ", Op2, ",", " ", Op1])    

#         elif n == 1 :
#             ARn = switch_case1(Nar).get(Nar, lambda: None)()
#             Op1 = switch_case(Aru).get(Aru, lambda: None)()
#             # Op1 = switch_case(Aru)()
#             syntax = Syntax([mne, " ", Op2, ",", " ", Op1, ARn]) 

#     patterns = {"opcode": opcode, "Op2": Op2, "F1": F1, "Op1": Op1}
#     members = {
#         "opcode": opcode,
#         "syntax": syntax,
#         "Op1": Op1,
#         "Op2": Op2,
#         "patterns": patterns,
#     }
#     return type(mne.title(), (OpARxInstruction,), members)

# LARd = create_OpARx_instruction("lar",0 )
# LARi = create_OpARx_instruction("lar",0, F1=1)
# SARd = create_OpARx_instruction("sar",16)
# #SARi = create_OpARx_instruction("SAR",16,0)


class SARi(c240xInstruction):
    tokens = [c240xLSARxDImodeToken]
    ARU = bit_range(4,7)
    N = bit(3)
    NAR = bit_range(0,3)
    F1 = 0
    Op1 = Operand(" ",str)
    Op2 = Operand("Op2", c240xStackFrameRegister,read=True, write=True)
    syntax = Syntax(["sari", " ", Op2, ",", " ", Op1]) 
    if N == 0 :
            Op1 = switch_case(ARU).get(ARU, lambda: None)()
            syntax = Syntax(["sari", " ", Op2, ",", " ", Op1])    
    elif N == 1 :
            ARn = switch_case1(NAR).get(NAR, lambda: None)()
            Op1 = switch_case(ARU).get(ARU, lambda: None)()
            syntax = Syntax(["sari", " ", Op2, ",", " ", Op1, ARn]) 
    patterns = {"opcode":16,"F1":0}

# class LARk(c240xInstruction):
#     tokens = [c240ximm8ARxToken]
#     Op2 = Operand("Op2", c240xARnRegister,read=True, write=True)
#     Op1 = Operand("Op1",imm8Src)
#     syntax = Syntax(["lar", " ", Op2, ",", " ", Op1])
#     patterns = {"opcode":22}

# def mov(src, dst):
#     """ Move src into dst register """
#     return SARi()

######## POPD/PSHD  #########
# class OpStackMemDIModeInstruction(c240xInstruction):
#     tokens = [c240xOpStackMemToken]

# def  create_StackMemDIMode_instruction(mne,Func4, opcode,F1=0, dst_read=True, dst_write=True):
#     """ Factory function to define a opStack Instruction """
#     Aru = c240xOpStackMemToken.ARU
#     n = c240xOpStackMemToken.N
#     Nar = c240xOpStackMemToken.NAR
#     Op = Operand(" ",str)
#     syntax = Syntax([mne, " ", ",", " ", Op])
#     if F1 :
#         Op = Operand("Op", AdrSrc7)
#         syntax = Syntax([mne, " ", ",", " ", Op])    
#     else :
#         if n == 0 :
#             Op = switch_case(Aru).get(Aru, lambda: None)()
#             syntax = Syntax([mne, " ",  ",", " ", Op])    

#         elif n == 1 :
#             ARn = switch_case1(Nar).get(Nar, lambda: None)()
#             Op = switch_case(Aru).get(Aru, lambda: None)()
#             syntax = Syntax([mne, " ",  ",", " ", Op, ARn]) 
#     patterns = {"Func4": Func4,"opcode": opcode,  "F1": F1,"Op": Op }
  
#     members = {
#         "Func4": Func4,
#         "opcode": opcode,
#         "syntax": syntax,
#         "Op": Op,
#         "patterns": patterns,
#     }
#     return type(mne.title(), (OpStackMemDIModeInstruction,), members)

# POPDd = create_StackMemDIMode_instruction("popd",8,10)
# POPDi = create_StackMemDIMode_instruction("popd",8,10,F1=1)
# PSHDd = create_StackMemDIMode_instruction("pshd",7,6)
# PSHDi = create_StackMemDIMode_instruction("pshd",7,6,F1=1)


# def pop(reg):
#     """ Push register helper """
#     return POPD(RegSrc(reg))

######## RET #########

class RET(c240xInstruction):
    tokens = [c240xRETToken]
    syntax = Syntax(["ret"])
    patterns = {"Func4":14, "opcode":15, "Func8":0}

######## imm8 address mode instructions #########

class imm8AdrModeInstruction(c240xInstruction):
    tokens =[c240ximm8ModeToken]

# def create_imm8AdrMode_instruction(mne,Func4,opcode):
#     Op = Operand("Op",imm8Src)
#     patterns = {"Func4": Func4,"opcode": opcode,"Op": Op}
#     syntax = Syntax([mne, " ", Op  ])
#     members = {
#         "Func4": Func4,
#         "opcode": opcode,
#         "syntax": syntax,
#         "Op": Op,
#         "patterns": patterns,
#     }
#     return type(mne.title(), (imm8AdrModeInstruction,), members)

# SBRk = create_imm8AdrMode_instruction("sbrk",7,12)
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
Popd_dma = create_dma_instruction("popd", 0b100010100)
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
    imm = Operand("imm", int)
    patterns = {"opcode":opcode, "imm":imm}
    syntax = Syntax([mne, " ","#", imm])
    members = {
        "opcode": opcode,
        "imm":imm,
        "patterns": patterns,
        "syntax": syntax
    }
    return type(mne.title(), (imm8kInstruction,), members)

Add_k = create_imm8k_instruction("add", 0b10111000)
Adrk_k = create_imm8k_instruction("adrk", 0b01111000)
Lacl_k = create_imm8k_instruction("lacl", 0b10111001)
Sub_k = create_imm8k_instruction("sub", 0b10111010)

#5 (32bit)
class lkshfitInstruction(c240xInstruction):
    tokens = [c240x_lkshift_Token]

def create_lkshift_instruction(mne,opcode):
    lk = Operand("lk", int)
    imm = Operand("imm", int)
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

@isa.pattern("stm", "STRI16(memdst, src)", size=1)
@isa.pattern("stm", "STRU16(memdst, src)", size=1)
def pattern_str16(context, tree, c0, c1):
    d = context.new_reg(c240xARnRegister)   #Arn寄存器组
    context.emit(mov(c1, d))
    context.emit(SARd(c1, c0))


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





