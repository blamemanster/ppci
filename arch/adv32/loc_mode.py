"""定义了全部的间接寻址及其编码解码方法"""
from ppci.arch.adv32.registers import ARNRegisters_n_to_m, ARPNRegisters, XARnRegisters
from ppci.arch.encoding import Constructor, Operand, Syntax, Transform

# @6bit √
class ADV32Expand_lon_con(Transform):
    def forwards(self, value):
        return value
    def backwards(self, value):
        if 0 <= value <= 63  :
            return value
        else:
            raise ValueError
class loc_con(Constructor):
    con = Operand("con",int)
    syntax = Syntax(["@",con])
    patterns = { "loccode":ADV32Expand_lon_con(con) } 

#*-SP[6bit] √
class ADV32Expand_loc_sp_con6(Transform):
    def forwards(self, value):
        return value + 64
    def backwards(self, value):
        if 64 <= value <= 127:
            return value - 64
        else:
            raise ValueError
class loc_sp_con6(Constructor):
    con6 = Operand("con6",int)
    syntax = Syntax(["*","-","sp","[",con6,"]"])
    patterns = { "loccode":ADV32Expand_loc_sp_con6(con6) }

# *SP++ √
class loc_sp_plus_plus(Constructor):
    syntax = Syntax(["*","sp","+","+"])
    patterns = { "loccode":0xbd }

# *--SP √
class loc_sp_sub_sub(Constructor):
    syntax = Syntax(["*","-","-","sp"])
    patterns = { "loccode":0xbe }

#*XARn++ √
class ADV32Expand_loc_xarn_plus(Transform):
    def forwards(self, value):
        return value + 128
    def backwards(self, value):
        if 128 <= value <= 135:
            return value - 128
        else:
            raise ValueError
class loc_xarn_plus(Constructor):
    reg = Operand("reg",XARnRegisters,write = True)
    syntax = Syntax(["*",reg,"+","+"])
    patterns = { "loccode":ADV32Expand_loc_xarn_plus(reg) }

#*--XARn √
class ADV32Expand_loc_sub_xarn(Transform):
    def forwards(self, value):
        return value + 136
    def backwards(self, value):
        if 136 <= value <= 143:
            return value - 136
        else:
            raise ValueError
class loc_sub_xarn(Constructor):
    reg = Operand("reg",XARnRegisters,write = True)
    syntax = Syntax(["*","-","-",reg])
    patterns = { "loccode":ADV32Expand_loc_sub_xarn(reg) }

#*+XARn[AR0] √
class ADV32Expand_loc_xarn_ar0(Transform):
    def forwards(self, value):
        return value + 144
    def backwards(self, value):
        if 144 <= value <= 151:
            return value - 144
        else:
            raise ValueError
class loc_xarn_ar0(Constructor):
    reg = Operand("reg",XARnRegisters,write = True)
    syntax = Syntax(["*","+",reg,"[","ar0","]"])
    patterns = { "loccode":ADV32Expand_loc_xarn_ar0(reg) }

#*+XARn[AR1] √
class ADV32Expand_loc_xarn_ar1(Transform):
    def forwards(self, value):
        return value + 152
    def backwards(self, value):
        if 152 <= value <= 159:
            return value - 152
        else:
            raise ValueError
class loc_xarn_ar1(Constructor):
    reg = Operand("reg",XARnRegisters,write = True)
    syntax = Syntax(["*","+",reg,"[","ar1","]"])
    patterns = { "loccode":ADV32Expand_loc_xarn_ar1(reg) }

#*+XARn[3bit] 有问题
class ADV32Expand_loc_plus_xarn_3bit(Transform):
    def forwards(self, value):
        return value
    def backwards(self, value):
        if 0 <= value <= 7:
            return value
        else:
            raise ValueError
class loc_plus_xarn_3bit(Constructor):
    reg = Operand("reg",XARnRegisters, write = True)   
    con3 = Operand("con3",int)
    syntax = Syntax(["*","+",reg,"[",con3,"]"])
    patterns = { "imm": 0b11, "loccode_reg":ADV32Expand_loc_plus_xarn_3bit(reg), "loccode_con3":ADV32Expand_loc_plus_xarn_3bit(con3)}

# *  √
class loc_star(Constructor):
    syntax = Syntax(["*"])
    patterns = { "loccode": 0xb8 }

# *++  √
class loc_star_plus(Constructor):
    syntax = Syntax(["*","+","+"])
    patterns = { "loccode": 0xb9 }


# *--  √
class loc_star_sub(Constructor):
    syntax = Syntax(["*","-","-"])
    patterns = { "loccode": 0xba }


# *0++  √
class loc_star_zero_plus(Constructor):
    syntax = Syntax(["*","0","+","+"])
    patterns = { "loccode": 0xbb }


# *0--  √
class loc_star_zero_sub(Constructor):
    syntax = Syntax(["*","0","-","-"])
    patterns = { "loccode": 0xbc }


# *BR0++  √
class loc_star_br0_plus(Constructor):
    syntax = Syntax(["*","br0","+","+"])
    patterns = { "loccode": 0xae }


#*BR0--  √
class loc_star_br0_sub(Constructor):
    syntax = Syntax(["*","br0","-","-"])
    patterns = { "loccode": 0xaf }


#*,ARPn  √
class ADV32Expand_loc_star_arpn(Transform):
    def forwards(self, value):
        return value + 176
    def backwards(self, value):
        if 176 <= value <= 183:
            return value - 176
        else:
            raise ValueError
class loc_star_arpn(Constructor):
    reg = Operand("reg",ARPNRegisters,write = True)
    syntax = Syntax(["*",",",reg])
    patterns = { "loccode": ADV32Expand_loc_star_arpn(reg) }


#*AR6%++  √
class loc_star_ar6(Constructor):
    syntax = Syntax(["*","ar6","%","+","+"])
    patterns = { "loccode": 0xbf }


#@XARn  √
class ADV32Expand_loc_xarn(Transform):
    def forwards(self, value):
        return value + 160
    def backwards(self, value):
        if 160 <= value <= 167:
            return value - 160
        else:
            raise ValueError

class loc_xarn(Constructor):
    reg = Operand("reg",XARnRegisters,write = True)
    syntax = Syntax(["@",reg])
    patterns = { "loccode": ADV32Expand_loc_xarn(reg) }


#@ACC  √
class loc_acc(Constructor):
    syntax = Syntax(["@","acc"])
    patterns = { "loccode": 0xa9 }


#@P  √
class loc_p(Constructor):
    syntax = Syntax(["@","p"])
    patterns = { "loccode": 0xab }


#@XT  √
class loc_xt(Constructor):
    syntax = Syntax(["@","xt"])
    patterns = { "loccode": 0xac }


#@ARn  √
class ADV32Expand_loc_arn(Transform):
    def forwards(self, value):
        return value + 160
    def backwards(self, value):
        if 160 <= value <= 167:
            return value - 160
        else:
            raise ValueError
class loc_arn(Constructor):
    reg = Operand("reg",ARNRegisters_n_to_m,write = True)
    syntax = Syntax(["@",reg])
    patterns = { "loccode": ADV32Expand_loc_arn(reg) }


#@AH  √
class loc_ah(Constructor):
    syntax = Syntax(["@","ah"])
    patterns = { "loccode": 0xa8 }


#@AL  √
class loc_al(Constructor):
    syntax = Syntax(["@","al"])
    patterns = { "loccode": 0xa9 }


#@PH  √
class loc_ph(Constructor):
    syntax = Syntax(["@","ph"])
    patterns = { "loccode": 0xaa }


#@PL  √
class loc_pl(Constructor):
    syntax = Syntax(["@","pl"])
    patterns = { "loccode": 0xab }


#@TH  √
class loc_th(Constructor):
    syntax = Syntax(["@","th"])
    patterns = { "loccode": 0xac }


#@SP  √
class loc_sp(Constructor):
    syntax = Syntax(["@","sp"])
    patterns = { "loccode": 0xad }



### 间接寻址的35种模式的集合，用于指令定义和指令选择
loc_mode1 = (
loc_con, loc_sp_con6, loc_sp_plus_plus, loc_sp_sub_sub, loc_xarn_plus,
loc_sub_xarn, loc_xarn_ar0, loc_xarn_ar1, loc_plus_xarn_3bit, loc_star, 
loc_star_plus, loc_star_sub, loc_star_zero_plus, loc_star_zero_sub,
loc_star_br0_plus, loc_star_br0_sub, loc_star_arpn, loc_star_ar6, 
loc_xarn, loc_acc, loc_p,loc_xt, loc_arn, loc_ah, loc_al, loc_ph,
loc_pl, loc_th, loc_sp)



# #*++,ARPn，仅AMODE=1有效
# class loc_star_plus_arpn(Constructor):
#     reg = Operand("reg",ARPNRegisters,write = True)
#     syntax = Syntax(["*","+","+",",",reg])
#     def set_user_patterns(self,tokens):
#         bit = 192
#         final_code = bit + self.reg.num
#         tokens.set_field("loccode", final_code)

# #*--,ARPn，仅AMODE=1有效
# class loc_star_sub_arpn(Constructor):
#     reg = Operand("reg",ARPNRegisters,write = True)
#     syntax = Syntax(["*","-","-",",",reg])
#     def set_user_patterns(self,tokens):
#         bit = 200
#         final_code = bit + self.reg.num
#         tokens.set_field("loccode", final_code)

# #*0++,ARPn，仅AMODE=1有效
# class loc_star_zeroplus_arpn(Constructor):
#     reg = Operand("reg",ARPNRegisters,write = True)
#     syntax = Syntax(["*","0","+","+",",",reg])
#     def set_user_patterns(self,tokens):
#         bit = 208
#         final_code = bit + self.reg.num
#         tokens.set_field("loccode", final_code)

# #*0--,ARPn，仅AMODE=1有效
# class loc_star_zerosub_arpn(Constructor):
#     reg = Operand("reg",ARPNRegisters,write = True)
#     syntax = Syntax(["*","0","-","-",",",reg])
#     def set_user_patterns(self,tokens):
#         bit = 216
#         final_code = bit + self.reg.num
#         tokens.set_field("loccode", final_code)

# #*BR0++,ARPn，仅AMODE=1有效
# class loc_star_br0_plus_arpn(Constructor):
#     reg = Operand("reg",ARPNRegisters,write = True)
#     syntax = Syntax(["*","br0","+","+",",",reg])
#     def set_user_patterns(self,tokens):
#         bit = 224
#         final_code = bit + self.reg.num
#         tokens.set_field("loccode", final_code)


# #*BR0--,ARPn，仅AMODE=1有效
# class loc_star_br0_sub_arpn(Constructor):
#     reg = Operand("reg",ARPNRegisters,write = True)
#     syntax = Syntax(["*","br0","-","-",",",reg])
#     def set_user_patterns(self,tokens):
#         bit = 232
#         final_code = bit + self.reg.num
#         tokens.set_field("loccode", final_code)

#*+XAR6[AR1%++], 仅AMODE=1有效
# class loc_star_plus_xar6(Constructor):
#     syntax = Syntax(["*","+","xar6","[","ar1","%","+","+","]"])
#     def set_user_patterns(self,tokens):
#         tokens.set_field("loccode", 0xBF)