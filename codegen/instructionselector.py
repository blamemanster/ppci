""" Instruction selector.

This part of the compiler takes in a DAG (directed
acyclic graph) of instructions and selects the proper target instructions.

Selecting instructions from a DAG is a NP-complete problem. The simplest
strategy is to split the DAG into a forest of trees and match these
trees.

Another solution may be: PBQP (Partitioned Boolean Quadratic Programming)

The selection process creates operations in a selection DAG. The possible
operations are listed in the below table:

选择过程在选择DAG中创建操作。可能的操作如下表所示:
+---------------+---------+-----------------------------------------+
| operation     | types   | description                             |
+===============+=========+=========================================+
| ADD(c0,c1)    | I,U     | Add its operands                        |
+---------------+---------+-----------------------------------------+
| SUB(c0,c1)    | I,U     | Substracts c1 from c0                   |
+---------------+---------+-----------------------------------------+
| MUL(c0,c1)    | I,U     | Multiplies c0 by c1                     |
+---------------+---------+-----------------------------------------+
| DIV(c0,c1)    | I,U     | Divides c0 by c1                        |
+---------------+---------+-----------------------------------------+
| OR(c0,c1)     | I,U     | Bitwise or                              |
+---------------+---------+-----------------------------------------+
| AND(c0,c1)    | I,U     | Bitwise and                             |
+---------------+---------+-----------------------------------------+
| XOR(c0,c1)    | I,U     | Bitwise exclusive or                    |
+---------------+---------+-----------------------------------------+
| LDR(c0)       | I,U     | Load from memory                        |
+---------------+---------+-----------------------------------------+
| STR(c0,c1)    | I,U     | Store value c1 at memory address c0     |
+---------------+---------+-----------------------------------------+
| FPREL         | U       | Frame pointer relative location         |
+---------------+---------+-----------------------------------------+
| CONST         | I,U     | Constant value                          |
+---------------+---------+-----------------------------------------+
| REG           | I,U     | Value in a specific register            |
+---------------+---------+-----------------------------------------+
| JMP           | I,U     | Jump to a label                         |
+---------------+---------+-----------------------------------------+
| CJMP          | I,U     | Conditional jump to a label             |
+---------------+---------+-----------------------------------------+

...

Memory move operations:

- STRI64(REGI32[rax], CONSTI32[1])
- MOVB()


"""

import abc
import logging
from ..utils.tree import Tree
from .treematcher import State
from .. import ir
from ..arch.encoding import Instruction
from .burg import BurgSystem
from .irdag import FunctionInfo, prepare_function_info
from .dagsplit import DagSplitter
from ..arch.generic_instructions import RegisterUseDef, InlineAssembly

#str(t)将变量t转为字符串，upper()将字符串变为大写
#
data_types = [str(t).upper() for t in ir.all_types]

ops = [
    "ADD", "SUB","MUL","DIV","REM", "OR","SHL",
    "SHR","AND","XOR", "NEG","INV",  "MOV","REG",
    "UND", "LDR","STR","CONST", "CJMP",  "I8TO","I16TO",
    "I32TO","I64TO",  "U8TO","U16TO","U32TO","U64TO",
    "F32TO","F64TO","FPREL","SPREL",  
]

# Add all possible terminals:

terminals = tuple(x + y for x in ops for y in data_types) + (
    "CALL", "LABEL", "MOVB", "JMP",
    "EXIT", "ENTRY", "ALLOCA", "FREEA", "ASM", 
)


class ContextInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def emit(self, instruction):  # pragma: no cover
        raise NotImplementedError()


class InstructionContext(ContextInterface):
    """ 在发出代码时可用于模式 """

    def __init__(self, frame, arch):
        self.frame = frame
        self.arch = arch
        self.debug_db = frame.debug_db
        self.tree = None

    def new_reg(self, cls):
        """ 生成给定类的新临时对象 """
        return self.frame.new_reg(cls)

    def new_label(self):
        """ Generate a new unique label """
        return self.frame.new_label()

    def move(self, dst, src):
        """ Generate move """
        self.emit(self.arch.move(dst, src))

    def emit(self, instruction):
        """ 抽象指令发射器代理 """
        self.frame.emit(instruction)
        if self.tree:
            self.debug_db.map(self.tree, instruction)
        return instruction


class TreeSelector:
    """ Tree matcher that can match a tree and generate instructions """

    def __init__(self, sys):
        self.sys = sys

    def gen(self, context, tree):
        """ 
        对给定AST树,平铺上pattern,并发出相应的代码
        """
        self.sys.check_tree_defined(tree)
        self.burm_label(tree)

        if not tree.state.has_goal("stm"):  # pragma: no cover
            raise RuntimeError("Tree {} not covered".format(tree))
        return self.apply_rules(context, tree, "stm")

    def burm_label(self, tree):
        """ 从下往上标记树中的所有节点 """
        for child_tree in tree.children:
            self.burm_label(child_tree)

        # Now the child nodes have been labeled, assign a state to the tree:
        tree.state = State()

        # 检查与此子树匹配的所有规则pattern，并检查是否可以确定状态
        for rule in self.sys.get_rules_for_root(tree.name):
            if self.sys.tree_terminal_equal(tree, rule.tree):
                nts = self.nts(rule.nr)
                kids = self.kids(tree, rule.nr)

                # Check for acceptance:
                if rule.acceptance:
                    accept = rule.acceptance(tree)
                else:
                    accept = True

                if (
                    all(x.state.has_goal(y) for x, y in zip(kids, nts))
                    and accept
                ):
                    cost = sum(x.state.get_cost(y) for x, y in zip(kids, nts))
                    marked_rules = set()
                    self.mark_tree(tree, rule, cost, marked_rules)

    def mark_tree(self, tree, rule, cost, marked_rules):
        cost = cost + rule.cost
        tree.state.set_cost(rule.non_term, cost, rule.nr)
        marked_rules.add(rule)

        # Also set cost for chain rules here:
        for cr in self.sys.chain_rules_for_nt(rule.non_term):
            if cr not in marked_rules:
                self.mark_tree(tree, cr, cost, marked_rules)

    def apply_rules(self, context, tree, goal):
        """ 将所有选定的指令应用到树中 """
        rule = tree.state.get_rule(goal)
        results = [
            self.apply_rules(context, kid_tree, kid_goal)
            for kid_tree, kid_goal in zip(
                self.kids(tree, rule), self.nts(rule)
            )
        ]
        # 获取要调用的函数:
        rule_f = self.sys.get_rule(rule).template
        context.tree = tree
        res = rule_f(context, tree, *results)
        context.tree = None
        return res

    def kids(self, tree, rule):
        """确定子树的规则"""
        template_tree = self.sys.get_rule(rule).tree
        return self.sys.get_kids(tree, template_tree)

    def nts(self, rule):
        """ 得到这个规则模式的开放端点 """
        template_tree = self.sys.get_rule(rule).tree
        return self.sys.get_nts(template_tree)


class InstructionSelector1:
    """ 
    指令选择器,它接受DAG并放置指令变成一个框架。
    这个是选择和调度的结合。
    """

    verbose = False

    def __init__(self, arch, sgraph_builder, weights=(1, 1, 1)):
        """ 创建一个新的指令选择器

            权重可以用来选择更多的指令:
            -大小
            -执行周期
            -或能量
            分别
        """
        self.logger = logging.getLogger("instruction-selector")
        self.dag_builder = sgraph_builder
        self.arch = arch
        self.dag_splitter = DagSplitter(arch)

        # 生成burm table表的规则:
        self.sys = BurgSystem()

        for terminal in terminals:
            self.sys.add_terminal(terminal)

        # 添加特殊节点:
        self.sys.add_rule("stm", Tree("CALL"), 0, None, self.call_function)
        self.sys.add_rule("stm", Tree("ASM"), 0, None, self.inline_asm)

        # 为寄存器类添加未定义的值:
        self._create_undefined_rules()

        # 添加所有isa的pattern:
        for pattern in arch.isa.patterns:
            #计算pattern的代价，weight[0] [1] [2]都是1
            #所以一个pattern的代价就是size、cycles和energy之和
            cost = (
                pattern.size * weights[0]
                + pattern.cycles * weights[1]
                + pattern.energy * weights[2]
            )
            self.sys.add_rule(
                pattern.non_term,
                pattern.tree,
                cost,
                pattern.condition,
                pattern.method,
            )

        self.sys.check()
        self.tree_selector = TreeSelector(self.sys)

    def _create_undefined_rules(self):
        """ 
        为基于寄存器类的未定义值创建规则。
        """
        und_map = {}
        for register_class in self.arch.info.register_classes:
            for ir_typ in register_class.ir_types:
                if ir_typ in ir.value_types:
                    und_map[ir_typ] = (register_class.name, register_class.typ)

        for ir_typ, info in und_map.items():
            reg_class_name, reg_class = info
            self._mk_undefined_rule(reg_class_name, reg_class, ir_typ)

    def _mk_undefined_rule(self, reg_class_name, reg_class, ir_ty):
        """ 
        为未定义值创建规则。
        例如,创建UNDU16,它定义一个16位寄存器并返回它。
        """
        suffix = ir_ty.name.upper()

        def und_pattern(context, tree):
            r = context.new_reg(reg_class)
            context.emit(RegisterUseDef(defs=(r,)))
            return r

        self.sys.add_rule(
            reg_class_name, Tree("UND{}".format(suffix)), 0, None, und_pattern
        )

    def call_function(self, context, tree):
        #生成函数调用的相关指令
        label, args, rv = tree.value
        for instruction in self.arch.gen_call(context.frame, label, args, rv):
            context.emit(instruction)

    def inline_asm(self, context, tree):
        """ 对内联汇编代码运行汇编程序. """
        template, output_registers, input_registers, clobbers = tree.value
        context.emit(
            InlineAssembly(
                template, output_registers, input_registers, clobbers
            )
        )

    def memcp(self):
        """ 调用memcpy arch函数 """
        for instruction in self.arch.gen_memcpy(dst, src, size):
            context.emit(instruction)

    def select(self, ir_function: ir.SubRoutine, frame, reporter):
        """ 选择指令的功能到一个框架 """
        assert isinstance(ir_function, ir.SubRoutine)
        self.logger.debug("Creating selection dag for %s", ir_function.name)

        # 创建一个携带全局函数info的对象:
        function_info = FunctionInfo(frame)
        prepare_function_info(self.arch, function_info, ir_function)

        # 创建选择图(有向无环图):
        sgraph = self.dag_builder.build(ir_function, function_info, frame.debug_db)

        if self.verbose:
            # 绘制图形需要相当长的时间，只有在冗长模式下才这样做。
            reporter.dump_sgraph(sgraph)

        # 将选择图分割为树的森林:
        forest = self.dag_splitter.split_into_trees(
            sgraph, ir_function, function_info, frame.debug_db
        )
        reporter.dump_trees(forest)

        # 创建一个可以发出指令的上下文:
        context = InstructionContext(frame, self.arch)

        args = list(zip(function_info.arg_types, function_info.arg_vregs))
        for instruction in self.arch.gen_function_enter(args):
            context.emit(instruction)

        # 生成适当的指令:
        self.munch_trees(context, forest)

        # 生成函数尾部:
        if isinstance(ir_function, ir.Function):
            rv = (ir_function.return_ty, function_info.rv_vreg)
        else:
            rv = None

        for instruction in self.arch.gen_function_exit(rv):
            context.emit(instruction)

        # TODO!!!
        # Emit code between blocks:
        # for instruction in self.arch.between_blocks(frame):
        #    frame.emit(instruction)

    def munch_trees(self, context, trees):
        """ 
        消耗一个dag,并使用匹配器将其与目标框架匹配。
        DAG匹配是np完全匹配。
        最简单的策略是把树林分成一片森林。然后,DAG被降低,只对树进行匹配。
        另一种方法是使用0-1编程,如NOLTIS算法。
        TODO: implement different strategies.
        """

        # 匹配所有子树:
        for tree in trees:
            # 调用动态编程匹配器机制:
            if isinstance(tree, Instruction):
                context.emit(tree)
            else:
                assert isinstance(tree, Tree)
                self.gen_tree(context, tree)

    def gen_tree(self, context, tree):
        """
        从树生成代码!!!!!!!!!!
        匹配成功后
        """
        self.tree_selector.gen(context, tree)
        # print( "测试1=========================", context )
        # print( "测试2=========================", tree )
