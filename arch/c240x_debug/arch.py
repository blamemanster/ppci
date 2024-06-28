""" c240x architecture description."""
import io
from ... import ir
from ...binutils.assembler import BaseAssembler
from ...utils.reporting import DummyReportGenerator
from ..arch import Architecture
from ..arch_info import ArchInfo, TypeInfo
from ..stack import StackLocation, FramePointerLocation
from ..generic_instructions import Label, Alignment, RegisterUseDef
from ..data_instructions import Db, Dw2, data_isa
from ..runtime import get_runtime_files
from .registers import c240xArgsRegister,register_classes
from .registers import AR0,AR1,AR2,AR3,AR4,AR5,AR6,AR7,ACC,TREG,PREG
from . import instructions, registers
from .instructions import  isa
from .instructions import RegDst


class ArmCallingConvention:
    pass


class c240xArch(Architecture):
    """ Texas Instruments c240x target architecture """
    name = "c240x"
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
                "int": ir.i16,
                "long": ir.i32,
                "ptr": ir.u16,
                ir.ptr: ir.u16,
            },
            register_classes=register_classes, #里边有两个RegisterClass
        )

        self.isa = isa + data_isa
        self.assembler = BaseAssembler()
        self.assembler.gen_asm_parser(self.isa)
        # Allocatable registers:
        self.callee_save = (AR0, AR1, AR6, AR7)
        self.caller_save = (AR2, AR3, AR4, AR5, PREG, TREG, ACC)

        # Frame pointer is located at the bottom of stack frame:
        self.fp_location = FramePointerLocation.BOTTOM

    def move(self, dst, src):
        """ Generate a move from src to dst """
        return instructions.mov(src, dst)

    @staticmethod
    def round_upwards(value):
        """ Round value upwards to multiple of 2 """
        return value + (value % 2)

    def gen_prologue(self, frame):
        """ Returns prologue instruction sequence """
        ########### Label indication function:
        yield Alignment(2)
        yield Label(frame.name)
        
        ########### pop return address from hard stack to software stack
        yield instructions.POPDi(2,0,0)

        ########### Frame Pointer into stack
        yield instructions.SARi(AR0,2,0,0)

        ########### Stack Pointer into stack
        yield instructions.SARi(AR1,0,0,0)
        
        ########### Adjust stack: Open up stack frame space
        # if frame.stacksize:
        #     yield instructions.LARk(
        #         imm8Src(self.round_upwards(frame.stacksize)), RegDst(Ar0)
        #     )

        frame.stacksize = 1 
        yield instructions.LARk(
               AR0, imm8Src(self.round_upwards(frame.stacksize))
            )
        yield instructions.LARi(AR0,2,0,0)

         ########## Push Callee saved registers:
        # for reg in self.get_callee_saved(frame):
        #     yield instructions.SARi(reg,PtrMode2)

    def gen_epilogue(self, frame):
        """Return epilogue sequence for a frame. Adjust frame pointer
        and add constant pool
        """
         ######### Pop saved registers back:
        # for reg in reversed(self.get_callee_saved(frame)):
        #     yield instructions.LARi(reg,PtrMode2)

        ########## Adjust stack:  free stack space
        frame.stacksize = 1 
        # if frame.stacksize:
        yield instructions.SBRk(
               imm8Src(self.round_upwards(frame.stacksize)+1)
            )

        ##########  FP output stack
        yield instructions.LARi(AR0,1,0,0)
        
        ########## Return from hardware Stack
        yield instructions.PSHDi(0,0,0)

        ########### Return from function:
        yield instructions.RET

        ########### Add final literal pool:
        for instruction in self.litpool(frame):
            yield instruction

    def get_callee_saved(self, frame):
        saved_registers = []
        for reg in self.callee_save:
            if frame.is_used(reg, self.info.alias):
                saved_registers.append(reg)
        return saved_registers

    def gen_call(self, frame, label, args, rv):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)

        arg_regs = []
        saved_space = 0
        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, c240xArgsRegister):
                arg_regs.append(arg_loc)
                yield self.move(arg_loc, arg)
            # elif isinstance(arg_loc, StackLocation):
            #     yield push(arg)
            #     saved_space += 2
            else:  # pragma: no cover
                raise NotImplementedError("Parameters in memory not impl")

        yield RegisterUseDef(uses=arg_regs)

        yield instructions.CAll(label, clobbers=self.caller_save)

        if saved_space:
            yield LARk(imm8Src(saved_space), RegDst(AR1))

        if rv:
            retval_loc = self.determine_rv_location(rv[0])
            yield RegisterUseDef(defs=(retval_loc,))
            yield self.move(rv[1], retval_loc)

    def gen_function_enter(self, args):
        arg_types = [a[0] for a in args]
        arg_locs = self.determine_arg_locations(arg_types)

        arg_regs = set(l for l in arg_locs if isinstance(l, c240xArgsRegister))
        yield RegisterUseDef(defs=arg_regs)

        ofs = 0
        for arg_loc, arg2 in zip(arg_locs, args):
            arg = arg2[1]
            if isinstance(arg_loc, c240xArgsRegister):
                yield self.move(arg, arg_loc)
            # elif isinstance(arg_loc, StackLocation):
            #     yield Mov(MemSrcOffset(2, SP), RegDst(arg))
            #     ofs += 2
            else:  # pragma: no cover
                raise NotImplementedError("Parameters in memory not impl")

    def gen_function_exit(self, rv):
        live_out = set()
        if rv:
            retval_loc = self.determine_rv_location(rv[0])
            yield self.move(retval_loc, rv[1])
            live_out.add(retval_loc)
        yield RegisterUseDef(uses=live_out)

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
        regs = [AR2,AR3,AR4,AR5]
        offset = 0
        for arg_type in arg_types:
            if regs:
                reg = regs.pop(0)
                locations.append(reg)
            else:
                locations.append(StackLocation(offset, 2))
                offset += 2
        return locations

    def determine_rv_location(self, ret_type):
        rv = ACC
        return rv

    def get_runtime(self):
        """Compiles the runtime support for c240x. It takes some c3 code and
        some assembly helpers.
        """
        # Circular import, but this is possible!
        from ...api import asm, c3c, link

        march = "c240x"
        c3_sources = get_runtime_files(["divsi3", "mulsi3"])
        # report_generator = HtmlReportGenerator(
        # open('c240x.html', 'wt', encoding='utf8'))
        with DummyReportGenerator() as reporter:
            obj1 = asm(io.StringIO(RT_ASM_SRC), march)
            obj2 = c3c(c3_sources, [], march, reporter=reporter)
            obj = link([obj1, obj2], partial_link=True)
        return obj






def round_up(s):
    return s + (4 - s % 4)














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
