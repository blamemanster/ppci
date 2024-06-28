"""
Isa related classes.
These can be used to define an instruction set.
"""

from collections import namedtuple
from ..utils.tree import Tree, from_string
from .encoding import Relocation

# 创建一个命名元组类型
Pattern = namedtuple("Pattern", ["non_term", "tree", "size", "cycles", "energy", "condition", "method"],)


class Isa:
    """ Container type for an instruction set.

    Contains a list of instructions, mappings from intermediate code
    to instructions.

    Isa's can be merged into new isa's which can be used to define target.
    For example the arm without FPU can be combined with the FPU isa
    to expand the supported functions.
    """
#初始化一个 指令集、重定位映射集合、模式集、窥孔优化集
    def __init__(self):
        self.instructions = []
        self.relocation_map = {}
        self.patterns = []
        self.peepholes = []
#定义isa合并的操作
    def __add__(self, other):
        assert isinstance(other, Isa)
        isa3 = Isa()
        isa3.instructions = self.instructions + other.instructions
        isa3.patterns = self.patterns + other.patterns
        isa3.relocation_map = self.relocation_map.copy()
        isa3.relocation_map.update(other.relocation_map)
        return isa3
#在isa中添加指令
    def add_instruction(self, instruction):
        """ Register an instruction into this ISA """
        self.instructions.append(instruction)
        return instruction
#在isa中定义重定位方法
    def register_relocation(self, relocation):
        """ Register a relocation into this isa """
        assert issubclass(relocation, Relocation)
        assert relocation.name is not None
        self.relocation_map[relocation.name] = relocation
        return relocation
#添加pattern到isa中
    def register_pattern(self, pattern):
        """ Add a pattern to this isa """
        self.patterns.append(pattern)

    #添加窥孔优化
    def peephole(self, function):
        """ Add a peephole optimization function """
        self.peepholes.append(function)
        return function

    def pattern(
        self, non_term, tree, condition=None, size=1, cycles=1, energy=1
    ):
        """
            Decorator function that adds a pattern.
        """
        if isinstance(tree, str):
            tree = from_string(tree)    #创建这棵树

        assert isinstance(tree, Tree)
        assert isinstance(size, int)

        def wrapper(function):
            """ Wrapper that add the function with the paramaters """
            pat = Pattern(non_term, tree, size, cycles, energy, condition, function)
            self.register_pattern(pat)  #把这个pattern加入注册集合
            return function

        return wrapper
