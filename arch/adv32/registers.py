""" Description of adv32 registers """


from ..registers import Register, RegisterClass
from ... import ir




class adv32Register16(Register):
    bitsize = 16

    @classmethod
    def from_num(cls, num):
        return num_reg_map1[num]

class adv32Register32(Register):
    bitsize = 32

    @classmethod
    def from_num(cls, num):
        return num_reg_map2[num]


class XARnRegisters(Register):
    bitsize = 32
    @classmethod
    def from_num(cls, num):
        return num_reg_map3[num]

class adv32Register(Register):
    bitsize = 16

    @classmethod
    def from_num(cls, num):
        return num_reg_map4[num]

class ARNRegisters(Register):
    bitsize = 16

    @classmethod
    def from_num(cls, num):
        return num_reg_map5[num]

class AXRegisters(Register):
    bitsize = 16

    @classmethod
    def from_num(cls, num):
        return num_reg_map6[num]

class ARPNRegisters(Register):
    bitsize = 16

    @classmethod
    def from_num(cls, num):
        return num_reg_map7[num]

class axsbRegisters(Register):
    bitsize = 8
    @classmethod
    def from_num(cls, num):
        return num_reg_map8[num]

#手动添加
class ARNRegisters_n_to_m(Register):
    bitsize = 16
    @classmethod
    def from_num(cls, num):
        return num_reg_map9[num]
    
class ARNRegisters_0_to_5(Register):
    bitsize = 16
    @classmethod
    def from_num(cls, num):
        return num_reg_map9[num]

#浮点寄存器
class adv32fpuRaH_Register(Register):
    bitsize = 32

    @classmethod
    def from_num(cls, num):
        return adv32_fpuRaH_Register[num]

class adv32fpuRaL_Register(Register):
    bitsize = 32

    @classmethod
    def from_num(cls, num):
        return adv32_fpuRaL_Register[num]

class adv32fpuSTF_Register(Register):
    bitsize = 32

    @classmethod
    def from_num(cls, num):
        return adv32_fpuSTF_Register[num]

#-------------------------------------
SP = adv32Register("SP",num = 0)
ACC = adv32Register("ACC",num = 1)

XT = adv32Register("XT",num = 4)
T = adv32Register("T",num = 5)
AR0 = adv32Register("AR0",num = 6)
AR1 = adv32Register("AR1",num = 7)
AR2 = adv32Register("AR2",num = 8)
AR3 = adv32Register("AR3",num = 9)
AR4 = adv32Register("AR4",num = 10)
AR5 = adv32Register("AR5",num = 11)
AR6 = adv32Register("AR6",num = 12)
AR7 = adv32Register("AR7",num = 13)

XAR0 = adv32Register("XAR0",num = 14)
XAR1 = adv32Register("XAR1",num = 15)
XAR2 = adv32Register("XAR2",num = 16)
XAR3 = adv32Register("XAR3",num = 17)
XAR4 = adv32Register("XAR4",num = 18)
XAR5 = adv32Register("XAR5",num = 19)
XAR6 = adv32Register("XAR6",num = 20)
XAR7 = adv32Register("XAR7",num = 21)
PH = adv32Register("PH",num = 22)
PL = adv32Register("PL",num = 23)
TH = adv32Register("TH",num = 24)
TL = adv32Register("TL",num = 25)
P = adv32Register("p",num = 26)
IER = adv32Register("TL",num = 27)
IFR = adv32Register("IFR",num = 28)
OVC = adv32Register("OVC",num = 29)


#---------------------------------------
Xar0 = XARnRegisters("XAR0",num = 0)
Xar1 = XARnRegisters("XAR1",num = 1)
Xar2 = XARnRegisters("XAR2",num = 2)
Xar3 = XARnRegisters("XAR3",num = 3)
Xar4 = XARnRegisters("XAR4",num = 4)
Xar5 = XARnRegisters("XAR5",num = 5)
Xar6 = XARnRegisters("XAR6",num = 6)
Xar7 = XARnRegisters("XAR7",num = 7)


al = AXRegisters("AL",num =0)
ah = AXRegisters("AH",num =0)

"""      16bit          """
Al = adv32Register16("AL", num=0)
Ah = adv32Register16("AH", num=1)
Sp = adv32Register16("SP", num=2)
DP = adv32Register16("DP",num=3)
""" ARPN"""
ARP0 = ARPNRegisters("ARP0",num=0)
ARP1 = ARPNRegisters("ARP0",num=1)
ARP2 = ARPNRegisters("ARP0",num=2)
ARP3 = ARPNRegisters("ARP0",num=3)
ARP4 = ARPNRegisters("ARP0",num=4)
ARP5 = ARPNRegisters("ARP0",num=5)
ARP6 = ARPNRegisters("ARP0",num=6)
ARP7 = ARPNRegisters("ARP0",num=7)
"""      32bit          """

Acc = adv32Register32("ACC", num=0 )
p= adv32Register32("P", num=1)

"""         ARN           """
ar0 = ARNRegisters("AR0",num = 14)
ar1 = ARNRegisters("AR1",num = 15)
ar2 = ARNRegisters("AR2",num = 16)
ar3 = ARNRegisters("AR3",num = 17)
ar4 = ARNRegisters("AR4",num = 18)
ar5 = ARNRegisters("AR5",num = 19)
ar6 = ARNRegisters("AR6",num = 20)
ar7 = ARNRegisters("AR7",num = 21)


#手动添加
ahmsb = axsbRegisters("AH.MSB",num=1)
almsb = axsbRegisters("AL.MSB",num=0)
ahlsb = axsbRegisters("AH.LSB",num=1)
allsb = axsbRegisters("AL.LSB",num=0)


"""         ARN           """
ar00 = ARNRegisters_n_to_m("AR0",num = 0)
ar11 = ARNRegisters_n_to_m("AR1",num = 1)
ar22 = ARNRegisters_n_to_m("AR2",num = 2)
ar33 = ARNRegisters_n_to_m("AR3",num = 3)
ar44 = ARNRegisters_n_to_m("AR4",num = 4)
ar55 = ARNRegisters_n_to_m("AR5",num = 5)
ar66 = ARNRegisters_n_to_m("AR6",num = 6)
ar77 = ARNRegisters_n_to_m("AR7",num = 7)

ar000 = ARNRegisters_0_to_5("AR0",num = 0)
ar111 = ARNRegisters_0_to_5("AR1",num = 1)
ar222 = ARNRegisters_0_to_5("AR2",num = 2)
ar333 = ARNRegisters_0_to_5("AR3",num = 3)
ar444 = ARNRegisters_0_to_5("AR4",num = 4)
ar555 = ARNRegisters_0_to_5("AR5",num = 5)

"""         FPU reg           """
R0H = adv32fpuRaH_Register("R0H", num = 0)
R1H = adv32fpuRaH_Register("R1H", num = 1)
R2H = adv32fpuRaH_Register("R2H", num = 2)
R3H = adv32fpuRaH_Register("R3H", num = 3)
R4H = adv32fpuRaH_Register("R4H", num = 4)
R5H = adv32fpuRaH_Register("R5H", num = 5)
R6H = adv32fpuRaH_Register("R6H", num = 6)
R7H = adv32fpuRaH_Register("R7H", num = 7)

R0L = adv32fpuRaL_Register("R0L", num = 0)
R1L = adv32fpuRaL_Register("R1L", num = 1)
R2L = adv32fpuRaL_Register("R2L", num = 2)
R3L = adv32fpuRaL_Register("R3L", num = 3)
R4L = adv32fpuRaL_Register("R4L", num = 4)
R5L = adv32fpuRaL_Register("R5L", num = 5)
R6L = adv32fpuRaL_Register("R6L", num = 6)
R7L = adv32fpuRaL_Register("R7L", num = 7)

STF = adv32fpuSTF_Register("STF", num = 0)
RB = adv32fpuSTF_Register("RB", num = 1)


adv32_xarnRegister = [Xar0,Xar1,Xar2,Xar3,Xar4,Xar5,Xar6,Xar7]
adv32_bit16Register = [Al,Ah,Sp,DP]
adv32_bit32Register = [Acc,p, R0H, R1H, R2H, R3H, R4H, R5H, R6H, R7H, R0L, R1L, R2L, R3L, R4L, R5L, R6L, R7L, STF, RB]
adv32_arnRegister = [ar0,ar1,ar2,ar3,ar4,ar5,ar6,ar7]
adv32_ArgsRegister = [Al,Ah]
adv32_AXRegister = [al,ah]
adv32_Register = [P,ACC,XT,T,PH,PL,TH,TL,AR0,AR1,AR2,AR3,AR4,AR5,AR6,AR7,XAR0,XAR1,XAR2,XAR3,XAR4,XAR5,XAR6,XAR7]
adv32_ARPNRegister = [ARP0,ARP1,ARP2,ARP3,ARP4,ARP5,ARP6,ARP7]
#手动添加
adv32_axsbRegisters = [ahmsb,almsb,ahlsb,allsb]
# adv32_ARnRegister = [AR0,AR1,AR2,AR3,AR4,AR5,AR6,AR7]
adv_32_ARNRegisters_n_to_m =[ar00,ar11,ar22,ar33,ar44,ar55,ar66,ar77] 
adv_32_ARNRegisters_0_to_5 =[ar000,ar111,ar222,ar333,ar444,ar555] 
adv32_fpuRaH_Register = [R0H, R1H, R2H, R3H, R4H, R5H, R6H, R7H]
adv32_fpuRaL_Register = [R0L, R1L, R2L, R3L, R4L, R5L, R6L, R7L]
adv32_fpuSTF_Register = [ STF, RB]

num_reg_map1= {r.num: r for r in adv32_bit16Register}
num_reg_map2 = {r.num: r for r in adv32_bit32Register}
num_reg_map3 = {r.num: r for r in adv32_xarnRegister}
num_reg_map4 = {r.num: r for r in adv32_Register}
num_reg_map5 = {r.num: r for r in adv32_ArgsRegister}
num_reg_map6 = {r.num: r for r in adv32_AXRegister}
num_reg_map7 = {r.num: r for r in adv32_ARPNRegister}
#手动添加
num_reg_map8 = {r.num: r for r in adv32_axsbRegisters}
num_reg_map9 = {r.num: r for r in adv_32_ARNRegisters_n_to_m}
num_reg_map_fpuRaH  = {r.num: r for r in adv32_fpuRaH_Register }
num_reg_map_fpuRaL  = {r.num: r for r in adv32_fpuRaL_Register }
num_reg_map_fpuSTF  = {r.num: r for r in adv32_fpuSTF_Register }

adv32Register16.registers = adv32_bit16Register
adv32Register32.registers = adv32_bit32Register
XARnRegisters.registers = adv32_xarnRegister
adv32Register.registers = adv32_Register
ARNRegisters.registers = adv32_arnRegister
AXRegisters.registers = adv32_AXRegister
ARPNRegisters.registers = adv32_ARPNRegister
#手动添加
axsbRegisters.registers = adv32_axsbRegisters
ARNRegisters_n_to_m.registers = adv_32_ARNRegisters_n_to_m
ARNRegisters_0_to_5.registers = adv_32_ARNRegisters_0_to_5
adv32fpuRaH_Register.registers = adv32_fpuRaH_Register
adv32fpuRaL_Register.registers = adv32_fpuRaL_Register
adv32fpuSTF_Register.registers = adv32_fpuSTF_Register

# adv32StackFrameRegister.registers = adv32_SFRegister
# adv32ArgsRegister.registers = adv32_ArgsRegister
# adv32ARnRegister.registers = adv32_ARnRegister

# all_registers = adv32_bit16Register + adv32_bit32Register
# all_registers = adv32_bit16Register

register_classes = [
    RegisterClass(
        "reg16",
        #  [],
         [ir.i16,ir.u16,ir.i8,ir.u8,ir.ptr],
        adv32Register,
    #    [PC,AR0, AR1,ST0,ST1,AR0,AR2,AR3,AR4,AR5,AR6,AR7,TREG,]
        adv32_Register
        #adv32_bit16Register
        #adv32Register16.registers
    ),

    # RegisterClass(
    #     "reg16",
    #     #  [],
    #      [],
    #     AXRegisters,
    # #    [PC,AR0, AR1,ST0,ST1,AR0,AR2,AR3,AR4,AR5,AR6,AR7,TREG,]
    #     adv32_AXRegister
    #     #adv32_bit16Register
    #     #adv32Register16.registers
    # ),

    RegisterClass(
        "reg32",
        [ir.i32,ir.u32],
        adv32Register,
        #  [ACC,PREG]
        adv32_bit32Register,
        #adv32Register32.registers
    )
    
]
