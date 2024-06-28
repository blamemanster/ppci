from ppci.arch.arch_info import Endianness
from ..token import Token, bit_range, bit
from ..isa import Isa

isa = Isa()

class adv3216token(Token):
    class Info:
        size = 16


class Base0(Token):
    class Info:
        size = 16


class Base1(Token):
    class Info:
        size = 32

class Token0(Base0):
    opcode0 = bit_range(0,16)


class Token1(Base1):
    opcode0 = bit_range(20,32)
    shft = bit_range(16,20)
    int16 = bit_range(0,16)
    

class Token2(Base1):
    opcode0 = bit_range(8,32)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)

class Token3(Base0):
    opcode0 = bit_range(8,16)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token4(Base1):
    opcode0 = bit_range(12,32)
    shft = bit_range(8,12)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token5(Base0):
    opcode0 = bit_range(12,16)
    shft = bit_range(8,12)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token6(Base1):
    opcode0 = bit_range(24,32)
    loccode = bit_range(16,24)
    int16 = bit_range(0,16)
    imm = bit_range(22,24)
    loccode_con3 = bit_range(19,22)
    loccode_reg  = bit_range(16,19)
    

class Token7(Base0):
    opcode0 = bit_range(8,16)
    int8 = bit_range(0,8)
    

class Token8(Base0):
    opcode0 = bit_range(7,16)
    int7 = bit_range(0,7)
    

class Token9(Base0):
    opcode0 = bit_range(11,16)
    xarn = bit_range(8,11)
    opcode2 = bit_range(7,8)
    int7 = bit_range(0,7)
    

class Token10(Base1):
    opcode0 = bit_range(20,32)
    int4 = bit_range(16,20)
    int16 = bit_range(0,16)
    

class Token11(Base1):
    opcode0 = bit_range(16,32)
    int16 = bit_range(0,16)
    

class Token12(Base0):
    opcode0 = bit_range(4,16)
    shft = bit_range(0,4)
    

class Token13(Base1):
    opcode0 = bit_range(20,32)
    cond = bit_range(16,20)
    int16 = bit_range(0,16)
    

class Token14(Base1):
    opcode0 = bit_range(22,32)
    arn = bit_range(19,22)
    arm = bit_range(16,19)
    int16 = bit_range(0,16)
    

class Token15(Base1):
    opcode0 = bit_range(22,32)
    int22 = bit_range(0,22)
    # opcode0 = bit_range(6, 16)
    # int22 = bit_range(0,6) + bit_range(16, 32)

class Token16(Base0):
    opcode0 = bit_range(3,16)
    xarn = bit_range(0,3)


class Token17(Base0):
    opcode0 = bit_range(4,16)
    int4 = bit_range(0,4)
    

class Token18(Base1):
    opcode0 = bit_range(24,32)
    loccode = bit_range(16,24)
    pma = bit_range(0,16)
    imm = bit_range(22,24)
    loccode_con3 = bit_range(19,22)
    loccode_reg  = bit_range(16,19)
    

class Token19(Base0):
    opcode0 = bit_range(10,16)
    int10 = bit_range(0,10)
    

class Token20(Base0):
    opcode0 = bit_range(11,16)
    arn = bit_range(8,11)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token21(Base1):
    opcode0 = bit_range(12,32)
    cond = bit_range(8,12)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token22(Base0):
    opcode0 = bit_range(9,16)
    ahlsb = bit_range(8,9)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token23(Base0):
    opcode0 = bit_range(9,16)
    ahmsb = bit_range(8,9)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token24(Base1):
    opcode0 = bit_range(20,32)
    cond = bit_range(16,20)
    int8 = bit_range(8,16)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token25(Base0):
    opcode0 = bit_range(9,16)
    allsb = bit_range(8,9)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token26(Base0):
    opcode0 = bit_range(9,16)
    almsb = bit_range(8,9)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token27(Base0):
    opcode0 = bit_range(11,16)
    xarn = bit_range(8,11)
    int8 = bit_range(0,8)
    
    

class Token28(Base1):
    opcode0 = bit_range(11,32)
    shf = bit_range(8,11)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token29(Base0):
    opcode0 = bit_range(4,16)
    cond = bit_range(0,4)
    

class Token30(Base1):
    opcode0 = bit_range(24,32)
    pma = bit_range(16,24)
    loccode = bit_range(0,16)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token31(Base1):
    opcode0 = bit_range(20,32)
    cond = bit_range(16,20)
    pma = bit_range(0,16)
    

class Token32(Base1):
    opcode0 = bit_range(19,32)
    xarn = bit_range(16,19)
    pma = bit_range(0,16)
    

class Token33(Base1):
    opcode0 = bit_range(16,32)
    pma = bit_range(0,16)
    

class Token34(Base1):
    opcode0 = bit_range(19,32)
    arpn = bit_range(16,19)
    pma = bit_range(0,16)
    

class Token35(Base1):
    opcode0 = bit_range(24,32)
    loccode = bit_range(16,24)
    PA = bit_range(0,16)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token36(Base1):
    opcode0 = bit_range(12,32)
    bit16 = bit_range(8,12)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token37(Base0):
    opcode0 = bit_range(5,16)
    vint = bit_range(0,5)
    

class Token38(Base1):
    opcode0 = bit_range(12,32)
    int4 = bit_range(8,12)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token39(Base0):
    opcode0 = bit_range(12,16)
    int4 = bit_range(8,12)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)
    

class Token40(Base0):
    opcode0 = bit_range(11,16)
    xarn = bit_range(8,11)
    opcode2 = bit_range(7,8)
    int7 = bit_range(0,7)
    

class Token41(Base0):
    opcode0 = bit_range(4,16)
    int16 = bit_range(0,4)
    

class Token42(Base0):
    opcode0 = bit_range(8,16)
    Mode = bit_range(0,8)
    

class Token43(Base0):
    opcode0 = bit_range(12,16)
    cond = bit_range(8,12)
    int8 = bit_range(0,8)
    

class Token44(Base1):
    opcode0 = bit_range(24,32)
    loccode = bit_range(16,24)
    PA = bit_range(0,16)
    imm = bit_range(22,24)
    loccode_con3 = bit_range(19,22)
    loccode_reg  = bit_range(16,19)
    

class Token45(Base1):
    opcode0 = bit_range(24,32)
    loccode = bit_range(16,24)
    int16 = bit_range(0,16)
    imm = bit_range(22,24)
    loccode_con3 = bit_range(19,22)
    loccode_reg  = bit_range(16,19)

class Token46(Base1):
    opcode0 = bit_range(16,32)
    int16 = bit_range(0,16)
    

class Token47(Base1):
    opcode0 = bit_range(20,32)
    shft = bit_range(16,20)
    int16 = bit_range(0,16)
    

class Token48(Base0):
    opcode0 = bit_range(8,16)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)

class Token49(Base1):
    opcode0 = bit_range(11,32)
    shf = bit_range(8,11)
    loccode = bit_range(0,8)
    imm = bit_range(6,8)
    loccode_con3 = bit_range(3,6)
    loccode_reg  = bit_range(0,3)

class Token50(Base1):
    opcode0 = bit_range(16,32)
    int2 = bit_range(8,16)
    int1 = bit_range(0,8)

class Token51(Base1):
    opcode0 = bit_range(0,32)

class Token52(Base0):
    opcode0 = bit_range(3,16)
    reg = bit_range(0,3)

class Token53(Base1):
    opcode0 = bit_range(3,32)
    reg = bit_range(0,3)

class Token54(Base1):
    opcode0 = bit_range(19,32)
    reg = bit_range(16,19)
    int16 = bit_range(0,16)


class Token55(Base0):
    opcode0 = bit_range(3,16)
    reg = bit_range(0,3)

class Token56(Base0):
    opcode0 = bit_range(12,16)
    cond = bit_range(8, 12)
    int8 = bit_range(0, 8)

class Token57(Base0):
    opcode0 = bit_range(8,16)
    int8 = bit_range(0, 8)

#浮点

class Token_fpu1(Base1):
    opcode0 = bit_range(6,32)
    rah = bit_range(3, 6)
    rbh = bit_range(0, 3)


class Token_fpu2(Base1):
    opcode0 = bit_range(22,32)
    int16 = bit_range(6, 22)
    rah = bit_range(3, 6)
    rbh = bit_range(0, 3)
