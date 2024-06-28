""" adv32 architecture description."""
# from build.lib.ppci.arch.adv32.instructions import ConstSrc7,PtrMode0,  PtrMode3
import io
from pickletools import uint1
from re import A
# from ppci.arch.avr import instructions
# from ... import ir
from ...binutils.assembler import BaseAssembler
from ...utils.reporting import DummyReportGenerator
from ..arch import Architecture
from ..arch_info import ArchInfo, TypeInfo
from ..stack import StackLocation, FramePointerLocation
from ..generic_instructions import Label, Alignment, RegisterUseDef
from ..data_instructions import Db, Dw2, data_isa
from ..runtime import get_runtime_files
from .registers import *
from . import instructions, registers
from .instructions import isa
from .instruction_fpu import isa_fpu

# from .instructions import create_popdi

class adv32Arch(Architecture):
    """ Texas Instruments adv32 target architecture """

    name = "adv32"

    ### 定义C语言数据类型与c28x机器内存字节对应关系，
    ### 见文档：工程总结/PPCI/架构描述/C语言存储模型
    ### （书TMS320C28X处理器优化的C_C++编译器用户指南第6.4节）
    ### TypeInfo()参数1表示c类型对应的字节大小，参数2表示该类型的对齐大小
    def __init__(self, options=None):
        super().__init__(options=options)
        self.info = ArchInfo(
            type_infos={
                ir.i8: TypeInfo(1, 1),
                ir.u8: TypeInfo(1, 1),
                ir.i16: TypeInfo(2, 2),
                ir.u16: TypeInfo(2, 2),
                ir.i32: TypeInfo(4, 2),
                ir.u32: TypeInfo(4, 2),
                ir.i64: TypeInfo(8, 2),
                ir.u64: TypeInfo(8, 2),
                ir.f32: TypeInfo(4, 4),
                ir.f64: TypeInfo(8, 8),
                "char": ir.i8,
                "int": ir.i16,
                "long": ir.i32,
                "ptr": ir.u16,
                ir.ptr: ir.u16,
                # ir.ptr: TypeInfo(2, 2),
            },
            register_classes=register_classes,
        )

        self.isa = isa + data_isa + isa_fpu

        ### 实例化底层汇编器，初始化词法语法解析规则并在汇编文本文件中添加对齐align、段section
        ### 和全局变量global等标签
        self.assembler = BaseAssembler()

        ### 调用底层汇编解析器解析isa.py中定义的所有汇编指令
        self.assembler.gen_asm_parser(self.isa)

        ### 寄存器使用约定，现场保护和恢复相关,见文档：工程总结/PPCI/架构描述/寄存器使用约定
        ### （书TMS320C28X处理器优化的C_C++编译器用户指南第7.2.1节）
        ### 可分配的寄存器集合
        ### 调用者保存的寄存器
        self.callee_save = (Al,Ah)
        ### 被调用者保存的寄存器
        self.caller_save = (Ah,Al)

        # self.caller_save = (AR2, AR3, AR4, AR5,  TREG)

        ### 帧指针fp
        # Frame pointer is located at the bottom of stack frame:
        self.fp_location = FramePointerLocation.BOTTOM


    def rvframe(self,frame):
        return frame.stacksize

    @staticmethod
    def round_upwards(value):
        """ Round value upwards to multiple of 2 """
        return value + (value % 2)

    ### 生成函数序言模块，即函数调用刚开始进入函数体之前所需要的准备工作，对于C28x而言
    ### 具体流程为： 
    ###     1、 开辟相应字节的局部栈帧空间，具体开辟多少字节数由局部变量数目和大小决定，如：
    ### 函数体内定义了一个int型变量a，一个long型变量b，则需要开辟1*1 + 1*2 = 3字节的栈空间
    ###     2、
    ### 因为对于开栈的汇编指令而言，所需要的操作数已经记录在了IR的FRAME节点中，可直接从该节点获取value
    ### 由于ppci框架对栈帧空间的计算进行了底层封装，只需通过帧对象frame的stacksize成员便可自动获取需要开辟的字节空间，
    ### 但这里需要注意，C28内存地址宽度为16bit一个，通用语言模型的一字节宽度为32Bit,因此这里要除以2。
    def gen_prologue(self, frame):
        """ Returns prologue instruction sequence """
        ########### Label indication function:
        yield Alignment(2)  
        yield Label(frame.name)

        ### 对于C28而言，开栈操作默认选择addb指令,SP作为栈指针
        if frame.stacksize:
            #yield instructions.addb(SP,int(frame.stacksize/2))
            # yield instructions.addb(int(frame.stacksize/2))
            #yield Movarn(loc16(Xar0),C16(1))
            pass


    ### 生成函数尾声模块，即函数调用结束离开函数体之前所需要的准备工作，对于C28x而言
    ### 具体流程为： 释放相应字节的局部栈帧空间（具体释放多少字节数与序言开辟的字节数一致）--->返回
    ### 
    def gen_epilogue(self, frame):
        """Return epilogue sequence for a frame. Adjust frame pointer
        and add constant pool
        """
        if frame.stacksize:
            ### 释放栈帧默认选择subb指令
            #yield instructions.subb(SP,int(frame.stacksize/2)) 
            yield instructions.subb307(int(frame.stacksize/2)) 
            # ### 函数调用后的返回操作默认选择lretr指令
            # yield instructions.lretr()
            # pass
    
    def get_callee_saved(self, frame):
        saved_registers = []
        for reg in self.callee_save:
            if frame.is_used(reg, self.info.alias):
                saved_registers.append(reg)
        return saved_registers

    ### 数据搬移，此处的定义为了满足子类继承基类而必须的函数重载，删除会导致编译错误
    def move(self, dst, src,n):
        """ Generate a move from src to dst """
        #if isinstance(src,int) and ((src > -1) and (src < 256)):
        #     return instructions.MovbAL(C8(src))
        # else:
        #     return instructions.MovSP(loc16(Sp),C16(src))
        #return instructions.Movlocal(loc16(Sp,n))
        #return instructions.MovSP(loc16(dst,n),C16(src))
        pass

    ### 生成调用进入函数体的主要逻辑
    ### 
    def gen_call(self, frame, label, args, rv):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)
        n = frame.stacksize
        arg_regs = []
        saved_space = 0
        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, adv32Register):
                arg_regs.append(arg_loc)
                yield self.move(arg_loc,arg,n)
            #elif isinstance(arg_loc, StackLocation):
              #  yield instructions.Movtomem(arg)
               # saved_space += 2
            else:  # pragma: no cover
                # raise NotImplementedError("Parameters in memory not impl")
                pass
        yield RegisterUseDef(uses=arg_regs)

        if isinstance(label, int):
            #yield instructions.Lcr(label)
            pass
        elif isinstance(label, str):
            # yield instructions.Lcrm(label)
            pass
        else:
            # yield instructions.Lcrl(label)
            pass

        if rv:
            retval_loc = self.determine_rv_location(rv[0])
            yield RegisterUseDef(defs=(retval_loc,))
            yield self.move(retval_loc,rv[1],frame )

    def gen_function_enter(self, args):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)

        arg_regs = set(l for l in arg_locs if isinstance(l, adv32Register))
        yield RegisterUseDef(defs=arg_regs)

        ofs = 0
        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, adv32Register):
               # yield self.move(arg, arg_loc)
               pass
            # elif isinstance(arg_loc, StackLocation):
            #     yield Mov(MemSrcOffset(2, SP), RegDst(arg))
            #     ofs += 2
            else:  # pragma: no cover
                # raise NotImplementedError("Parameters in memory not impl")
                pass
    def gen_function_exit(self, rv):
        live_out = set()
        # if rv:
        #     retval_loc = self.determine_rv_location(rv[0])
        #     yield self.move1(retval_loc, rv[1])
        #     live_out.add(retval_loc)
        yield RegisterUseDef(uses=live_out)
        pass

    def litpool(self, frame):
        """ Generate instruction for the current literals """
        # Align at 2 bytes
        if frame.constants:
            yield Alignment(2)

        # Add constant literals:
        while frame.constants:
            label, value = frame.constants.pop(0)
            yield Label(label)
            if isinstance(value, str):
                yield Dw2(value)
            elif isinstance(value, bytes):
                for byte in value:
                    yield Db(byte)
                yield Alignment(2)  # Align at 2 bytes
            else:  # pragma: no cover
                raise NotImplementedError("Constant of type {}".format(value))

    #def determine_local_varia_locations():

    ### 函数调用时的传参规则，对于C28而言遵循C99标准，参数按从右往左的顺序依次入栈，并被视为局部变量
    ### AR2、AR3、AR4、AR5被视为传参专用寄存器，参数的寄存器分配顺序
    def determine_arg_locations(self, arg_types):
        """
        Given a set of argument types, determine location for argument
        ABI:
        param1 = AR2
        param2 = AR3
        param3 = AR4
        param4 = AR5
        further parameters are put on stack.
        retval = ACC
        """
        locations = []
        regs = [Al,Ah]
        offset = 0
        for arg_type in arg_types:
            if regs:
                reg = regs.pop(0)
                locations.append(reg)
            else:
                locations.append(StackLocation(offset, 2))
                offset += 2
        return locations

    ### 对于带返回值的函数调用，返回值
    def determine_rv_location(self, ret_type):
        rv = Al
        # rv = AR2
        return rv

    ###　Ｃ２８的运行时环境，对于有符号高位浮点乘除法运算对应的节点，
    ### 目前C28基本的指令不能满足，需要调用通用的乘除法算法库 ，
    ### 如果不指明将导致IR印射中断，编译报错。
    def get_runtime(self):
        """Compiles the runtime support for adv32. It takes some c3 code and
        some assembly helpers.
        """
        # Circular import, but this is possible!
        from ...api import asm, c3c, link

        march = "adv32"
        # c3_sources = get_runtime_files(["divsi3", "mulsi3"])
        c3_sources = get_runtime_files(["divsi3"])
        # report_generator = HtmlReportGenerator(
        # open('adv32.html', 'wt', encoding='utf8'))
        with DummyReportGenerator() as reporter:
            # obj1 = asm(io.StringIO(RT_ASM_SRC), march)
            # obj2 = cc(c3_sources, [], march, reporter=reporter)
            # obj = link([obj1, obj2], partial_link=True)
         obj = c3c(c3_sources, [], march,reporter=reporter)
        return obj
        

### C28X编译器的C语言内联（内嵌）汇编的运行时环境，目前尚未可知，此处默认使用ARM的环境，具体可通过参考
### （书TMS320C28X处理器优化的C_C++编译器用户指南第7.5.5节，表7-6. TMS320C28x C/C++ Compiler Intrinsics）
### 并借助CCS尝试出来
###  Ｃ／Ｃ＋＋访问汇编语言变量／常量，
RT_ASM_SRC = """
                     ; Shift left helper:
    __shl_a:
      add.w r12, r12 ; shift 1 bit left
      sub.w #1, r13  ; decrement counter
    global __shl
    __shl:           ; Shift r12 left by r13 bits
      cmp.w #0, r13
      jne __shl_a
      ret

                     ; Shift right helper:
    __shr_a:
      clrc           ; clear carry
      rrc r12        ; shift 1 bit right through carry
      sub.w #1, r13  ; decrement counter
    global __shr
    __shr:           ; Shift r12 right by r13 bits
      cmp.w #0, r13
      jne __shr_a
      ret
"""
