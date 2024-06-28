"""
选择图是一个函数或基本块的控制和数据流的图形表示。
"""

from collections import namedtuple
from ..utils.collections import OrderedSet, OrderedDict


SGEdge = namedtuple("SGEdge", ["src", "dst", "name", "kind"])
SGGroup = namedtuple("SGGroup", ["name"])


class SelectionGraph:
    """ DAG的待选指令 """

    # TODO: can this derive from graph class?
    def __init__(self):
        self.roots = []
        self.nodes = OrderedSet()

        # An ordered dict of group names to ordered sets of nodes:
        self.groups = OrderedDict()

    def get_node(self, value):
        return value.src()

    def add_node(self, node):
        """ Add a node to the graph """
        self.nodes.add(node)
        if hasattr(node, "group"):
            group = getattr(node, "group")
            if group not in self.groups:
                self.groups[group] = OrderedSet()
            self.groups[group].add(node)

    def get_group(self, group):
        """ Get all nodes of a group """
        assert group in self.groups
        return self.groups[group]

    @property
    def edges(self):
        """ 通过查看所有节点的所有输入，然后找到产生这些输入的节点来生成所有边! """
        for node in self.nodes:
            for inp in node.inputs:
                yield SGEdge(inp.node, node, inp.name, inp.kind)

    def check(self):
        """ Check if the graph is consistent """
        for edge in self.edges:
            assert edge.src in self.nodes
            assert edge.dst in self.nodes

    def __iter__(self):
        return iter(self.nodes)


class SGValue:
    """ A value is actually an edge in the graph

    it has one single source, and can have multiple usages.
    """

    DATA = 0
    CONTROL = 1
    MEMORY = 2

    def __init__(self, name, kind, node):
        assert kind in (self.DATA, self.CONTROL, self.MEMORY)
        self.name = name
        self.kind = kind  # Control or data value
        self.node = node  # The node producing the value
        self.users = []
        self.vreg = None

        # Indicator if a value needs a vreg or not:
        # For example, a const does not want a vreg, and an
        # framepointer + offset also does not want to be copied
        # into a vreg!
        self.wants_vreg = True  # Indicator if this value is expensive

    def src(self):
        """ Gets the originating node for this value """
        pass

    def targets(self):
        """ Gets the nodes that use this value """
        pass

    def add_use(self, use):
        self.users.append(use)

    @property
    def ty(self):
        """ Get the ir-type of this value """
        return self.node.name.ty

    def __repr__(self):
        return "SGValue(name={},vreg={})".format(self.name, self.vreg)


class SGNode:
    """
    选择图中的单个节点。
    节点有一个操作名称，在未选择图的情况下可以是一个抽象操作，
    但在选择了机器指令的情况下，它也可以是一个选择指令。
    它也有输入值和输出值。一个节点可以产生多个值。
    例如，x86指令'div'同时产生商和余数。
    """

    def __init__(self, op):
        self.name = op
        self.value = None
        self.inputs = []
        self.outputs = []

    def __repr__(self):
        return "{} [{}]".format(self.name, self.value)

    def is_machine_instruction(self):
        return False

    def inputs_of_type(self, kind):
        """ Return all inputs of a given type """
        return [inp for inp in self.inputs if inp.kind == kind]

    @property
    def data_inputs(self):
        return self.inputs_of_type(SGValue.DATA)

    @property
    def control_inputs(self):
        return self.inputs_of_type(SGValue.CONTROL)

    @property
    def memory_inputs(self):
        return self.inputs_of_type(SGValue.MEMORY)

    def outputs_of_type(self, kind):
        return [out for out in self.outputs if out.kind == kind]

    @property
    def values(self):
        return self.inputs + self.outputs

    @property
    def data_outputs(self):
        return self.outputs_of_type(SGValue.DATA)

    def add_input(self, inp):
        """ Add a single input to this node """
        assert isinstance(inp, SGValue)
        self.inputs.append(inp)
        inp.add_use(self)

    def add_inputs(self, *args):
        """ Add a series of inputs """
        for inp in args:
            self.add_input(inp)

    def new_output(self, name, kind=SGValue.DATA):
        """ 创建一个具有名称和给定类型的新输出值 """
        if self.name.ty is None and kind == SGValue.DATA:
            # self.name.op not in ['ENTRY', 'EXIT'] and \
            raise ValueError("{} cannot produce output".format(self))
        val = SGValue(name, kind, self)
        self.add_output(val)
        return val

    def usages(self):
        return len(self.outputs)

    @property
    def children(self):
        return [u for o in self.outputs for u in o.users]

    def add_output(self, x):
        assert isinstance(x, SGValue)
        assert x.node is self
        self.outputs.append(x)

    @property
    def volatile(self):
        return any(v.kind != SGValue.DATA for v in self.values)
