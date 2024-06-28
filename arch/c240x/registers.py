""" ADV16 DSP TI c240x registers """
from ..registers import Register, RegisterClass
from ... import ir

# 以下描述目标 ADV16 寄存器定义
"""
1. 通用寄存器
2. 堆栈寄存器
3. 数据寄存器
4. 状态寄存器
5. MAC寄存器
6. 特殊的运算用的寄存器（可选的）
7. 存储单元的寄存器
8. 浮点单元寄存器（可选的）
以上寄存器不一定都需要定义，即便是宽度相同的，也要按用途不同对寄存
器进行定义，以便在指令描述中进行引用，以免造成资源在指令运行时的混
叠现象（冲突的可能性）
命名规则:xxxxyyyyyRegister(Register)
分别为:xxxx = 目标名:yyyy = 目标功能寄存器名
对流水线寄存器及其受影响的中间寄存器暂时无需定义，均以各指令受影响
的寄存器定义为基准，进行状态控制或调度进行定义。
"""
# 通用寄存器定义
class c240xRegister(Register):
    bitsize = 16
    @classmethod
    def from_num(cls, num):
        return num_reg_map1[num]
# 双字节寄存器定义
class c240xWordRegister(Register):
    bitsize = 32
    @classmethod
    def from_num(cls, num):
        return num_reg_map2[num]

# 堆栈结构寄存器定义
class c240xStackFrameRegister(Register):
    bitsize = 16
# ARn寄存器组的定义
class c240xARnRegister(Register):
    bitsize = 16
# Args寄存器定义
class c240xArgsRegister(Register):
    bitsize = 16
#-----------------------------------------------
# mem -> reg
#-----------------------------------------------
class c240x_Memtoreg_dma_Registers(Register):
    bitsize =  7
    @classmethod
    def from_num(cls, num):
        return num_reg_map3[num]

# class c240x_Memtoreg_ind_Registers(Register):
#     bitsize =  4
#     def from_num(cls, num):
#         return num_reg_map4[num]

#num就是对应的寄存器的编码
PC = c240xRegister("PC", num=0)

AR0 = c240xRegister("AR0", num=1)
 # Frame pointer
AR1 = c240xRegister("AR1", num=2)
SP = AR1
  # Stack pointer
ST0 = c240xRegister("ST0", num=3)
 # State control register 1
ST1 = c240xRegister("ST1", num=4)  
 # State control register 2
AR2 = c240xRegister("AR2", num=5)

AR3 = c240xRegister("AR3", num=6)

AR4 = c240xRegister("AR4", num=7)

AR5 = c240xRegister("AR5", num=8)

AR6 = c240xRegister("AR6", num=9)

AR7 = c240xRegister("AR7", num=10)

TREG = c240xRegister("TREG", num=11)

# 32 bit registers:
# r12 = c240xRegister32("r12", num=12, aka=("ACC",))
# Acc = r12
# r13= c240xRegister32("r13", num=13, aka=("PREG",))
# Preg = r13
ACC = c240xWordRegister("ACC", num=0)

PREG= c240xWordRegister("PREG", num=1)
#--------------------------------------------------
#DMA,IND,这里只是
#--------------------------------------------------
DMA = c240x_Memtoreg_dma_Registers("DMA", num=0)
# ind = c240x_Memtoreg_ind_Registers("ind", num=1)



c240xStackFrameRegister.registers = [
    AR0,
    AR1,
]

c240xArgsRegister.registers = [
    AR2,
    AR3,
    AR4,
    AR5,
]

c240xARnRegister.registers = [
    AR0,
    AR1,
    AR2,
    AR3,
    AR4,
    AR5,
    AR6,
    AR7,
]


c240x_bit7Register = [DMA]
#c240x_bit4Register = [ind]
c240x_bit16Register = [PC,AR0,AR1,ST0,ST1,AR2,AR3,AR4,AR5,AR6,AR7,TREG]
c240x_bit32Register = [ACC,PREG]
num_reg_map1= {r.num: r for r in c240x_bit16Register}
num_reg_map2 = {r.num: r for r in c240x_bit32Register}
num_reg_map3= {r.num: r for r in c240x_bit7Register}
#num_reg_map4 = {r.num: r for r in c240x_bit4Register}

c240xRegister.registers = c240x_bit16Register
c240xWordRegister.registers = c240x_bit32Register
c240x_Memtoreg_dma_Registers.registers = c240x_bit7Register

# all_registers = c240x_bit16Register + c240x_bit32Register
# all_registers = c240x_bit16Register
register_classes = [
    RegisterClass(
        "reg16",
        [ir.i16, ir.u16, ir.ptr],
        c240xRegister,
        c240x_bit16Register,
        #c240xRegister16,
    #    [PC,AR0, AR1,ST0,ST1,AR0,AR2,AR3,AR4,AR5,AR6,AR7,TREG,]
        #c240x_bit16Register
        #c240xRegister16.registers
    ),
    RegisterClass(
        "reg32",
        [ir.i32,ir.u32],
        c240xWordRegister,
        c240x_bit32Register,
        #c240xRegister32,
        #[ACC,PREG]
        #c240x_bit32Register
        #c240xRegister32.registers
    ),
    RegisterClass(
        "reg7",
        [ir.i7,ir.u7],
        c240x_Memtoreg_dma_Registers,
        c240x_bit7Register,
    ),

]

