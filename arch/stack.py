""" 该模块包含描述堆栈的所有类 """

import enum
from .encoding import Instruction
from .registers import Register
from .generic_instructions import Label


class FramePointerLocation(enum.Enum):
    """ 定义帧指针指向的位置 """

    TOP = 1     # 表示帧指针指向帧的  顶部位置。
    BOTTOM = 2  # 表示帧指针指向帧的  底部位置


class StackLocation:
    """ 堆栈位置可以像寄存器一样存储数据 """

    def __init__(self, offset: int, size: int):
        # self.frame = frame  # The frame in which this location lives
        self.offset = offset
        self.size = size

    def __repr__(self):
        return "Stack[{} bytes at {}]".format(self.size, self.offset)


def generate_temps():
    n = 0
    while True:
        yield "vreg{}".format(n)
        n = n + 1


class Frame:
    """
        活动记录抽象。这个类包含一个扁平的函数。指令在这个阶段被选择和安排。
        每台机器的帧不同。唯一要做的就是寄存器分配.
    """

    def __init__(
        self, name, debug_db=None, fp_location=FramePointerLocation.TOP
    ):
        self.name = name
        self.debug_db = debug_db  # 最终调试信息
        self.fp_location = fp_location
        self.instructions = []
        self.used_regs = set()
        self.is_leaf = False  # TODO: detect leaf functions
        self.out_calls = []
        self.temps = generate_temps()

        # 本地堆栈:
        self.stacksize = 0
        self.alignment = 1

        # 文字池:
        self.constants = []
        self.literal_number = 0

    def __repr__(self):
        return "Frame {}".format(self.name)

    def alloc(self, size: int, alignment: int):
        """ 在堆栈框架上分配空间并返回堆栈位置 """
        # 确定整个堆栈帧的对中作为最大对中
        self.alignment = max(self.alignment, alignment)

        # 调用带有0的alloc表示某个地方有问题。
        if size == 0:
            raise ValueError("Trying to allocate 0 bytes")

        # 向下还是向上?
        if self.fp_location == FramePointerLocation.TOP:
            # 从帧指针创建一个负偏移量:
            # 向下
            self.stacksize += size
            misalign = self.stacksize % alignment
            if misalign:
                self.stacksize = self.stacksize - misalign + alignment
            # 当帧指针位于堆栈帧的顶部时，偏移量为负:
            offset = -self.stacksize
        else:
            # 向上
            misalign = self.stacksize % alignment
            if misalign:
                self.stacksize += size - misalign
            offset = self.stacksize
            self.stacksize += size
        location = StackLocation(offset, size)
        return location

    def add_out_call(self, size):
        """
        记录我们调用了这个函数。
        size形参决定了我们需要在堆栈上保留多少字节来传递实参。
        """
        self.out_calls.append(size)

    def new_name(self, salt):
        """ 生成一个新的唯一名称 """
        name = "{}_{}_{}".format(self.name, salt, self.literal_number)
        self.literal_number += 1
        return name

    def add_constant(self, value):
        """ 向常量池中添加常量文字 """
        for lab_name, val in self.constants:
            if value == val:
                return lab_name
        assert isinstance(value, (str, int, bytes)), str(value)
        lab_name = self.new_name("literal")
        self.constants.append((lab_name, value))
        return lab_name

    def is_used(self, register, alias):
        """ 检查这个帧是否使用了一个寄存器或它的别名。
        """
        # assert register in alias
        return any(r in self.used_regs for r in alias[register.get_real()])

    def live_ranges(self, vreg):
        """ 确定某个寄存器的有效范围 """
        return self.cfg._live_ranges[vreg]

    def new_reg(self, cls, twain=""):
        """ 检索一个新的虚拟寄存器 """
        tmp_name = self.temps.__next__() + twain
        assert issubclass(cls, Register)
        tmp = cls(tmp_name)
        return tmp

    def new_label(self):
        """ 生成唯一的新标签 """
        return Label(self.new_name("label"))

    def emit(self, ins):
        """ 在这个框架的末尾附加一个抽象指令 """
        #assert isinstance(ins, Instruction)
        self.instructions.append(ins)
        return ins

    def insert_code_before(self, instruction, code):
        """ 在指令之前插入代码序列 """
        pt = self.instructions.index(instruction)
        for idx, ins in enumerate(code):
            self.instructions.insert(idx + pt, ins)

    def insert_code_after(self, instruction, code):
        """ 在指令后插入代码序列 """
        pt = self.instructions.index(instruction) + 1
        for idx, ins in enumerate(code):
            self.instructions.insert(idx + pt, ins)
