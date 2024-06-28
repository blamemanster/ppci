""" 这个模块处理指令的编码和解码 """


import abc
from .registers import Register
from .token import TokenSequence


class Operand(property):
    """ 指令操作数。
当指令有操作数时，使用此函数创建该属性。
参数:name:将在用法中显示的名称。cls:此函数必须采用的类型。
实现描述符协议的自定义派生属性
通过继承财产
    """

    def __init__(self, name, cls, read=False, write=False):
        self._name = name
        if isinstance(cls, dict):
            self._value_map = cls
            cls = tuple(cls.keys())
        else:
            self._value_map = None
        self._cls = cls
        self._read = read
        self._write = write
        #self.int_value = None
        # if isinstance(cls, type) or isinstance(cls, tuple)
        # if isinstance(cls, type) and isinstance(cls,int):
        #     self.int_value = value

        # Construct a private backing field for the property:
        private_field = "_{}".format(name)

        if isinstance(cls, type) and issubclass(cls, Register):
            assert read or write

        def getter(self):
            return getattr(self, private_field)

        def setter(self, value):
            assert isinstance(value, cls)
            # if  isinstance(value,int):
            #     int_value = value
            #     print("value is : %d\n", int_value)
            setattr(self, private_field, value)

        super().__init__(getter, setter)

    def __repr__(self):
        return "operand name={}, cls={}".format(self._name, self._cls)

    @property
    def is_constructor(self):
        """ 检查这是一个简单的类型，还是许多类型的选择 """
        if isinstance(self._cls, tuple):
            return True
        else:
            return issubclass(self._cls, Constructor)

    @property
    def source(self):
        """ Get the original """
        return self

    def get_value(self, objref):
        """ 获取此属性的数值，这里只处理寄存器和立即数类型
         编码的时候用的
           """
        val = self.__get__(objref)
        if isinstance(val, Register):
            val = val.num
        if self._value_map and not isinstance(val, int):
            val = self._value_map[type(val)]
        assert isinstance(val, int)
        return val

    def set_value(self, objref, value):
        """ Set the numeric value of this property """
        raise NotImplementedError()

    def from_value(self, value):
        """ 从给定的值创建正确类型的对象 
        """
        if issubclass(self._cls, Register):
            regs = self._cls.all_registers()
            reg_map = {r.num: r for r in regs}
            return reg_map[value]
        else:
            # assume int here!
            return value


class Transform(metaclass=abc.ABCMeta):
    """ 包装器转换属性的数值 """

    def __init__(self, wrapped):
        self._wrapped = wrapped

    @abc.abstractmethod
    def forwards(self, value):  # pragma: no cover
        """ 在这里实现前向转换 """
        raise NotImplementedError()

    def backwards(self, value):  # pragma: no cover
        """ 在这里实现后向转换 """
        raise NotImplementedError()

    def get_value(self, obj):
        """ 获取此属性的数值 
        如果是可变的操作数，则调用forwards
        """
        val = self._wrapped.get_value(obj)
        return self.forwards(val)

    def from_value(self, value):
        value = self.backwards(value)
        return self._wrapped.from_value(value)

    @property
    def source(self):
        """ Get the original data source """
        return self._wrapped.source


class Constructor:
    """指令，指令的一部分

指令是构造函数的特殊子类。这是最终结果
换句话说，它不能在构造函数中使用。一条指令也可以物化，其中作为构造函数的一部分
指令。构造函数可以包含语法，并且可以使用这个语法
    """

    syntax = None
    patterns = ()

    def __init__(self, *args, **kwargs):
        # Generate constructor from args:
        if self.syntax:
            formal_args = self.syntax.formal_arguments

            # Set parameters:
            if len(args) != len(formal_args):
                raise TypeError(
                    "{} arguments given, but {} expects {}".format(
                        len(args), self.__class__, len(formal_args)
                    )
                )
            for farg, arg in zip(formal_args, args):
                if not isinstance(arg, farg._cls):  # pragma: no cover
                    # Create some nice looking error:
                    raise TypeError(
                        '{} expected {}, but got "{}" of type {}'.format(
                            type(self), farg._cls, arg, type(arg)
                        )
                    )
                setattr(self, farg._name, arg)
        if args:
            #print("元组不为空")
            if len(args) == 1:
                if isinstance(args[0],int):
                    self.intvalue = args[0]
                if isinstance(args[0],Register):
                    self.regvalue = args[0]
            elif len(args) == 2:
                if isinstance(args[0],int):
                    self.intvalue = args[0]
                if isinstance(args[0],Register):
                    self.regvalue = args[0]
                if isinstance(args[1],int):
                    self.intvalue = args[1]
                if isinstance(args[1],Register):
                    self.regvalue = args[1]
        
        # else:
        #     print("元组为空")
        
        for pname, pval in kwargs.items():
            # print('\n\n\n===', pname, pval)
            setattr(self, pname, pval)

    def __str__(self):
        """ 创建一个好看的组装字符串 """
        if self.syntax:
            return self.syntax.render(self)
        else:
            return super().__str__()

    @staticmethod
    def dict_to_patterns(d):
        """ 从字典创建模式 """
        if isinstance(d, dict):
            patterns = []
            for field, value in d.items():
                if isinstance(value, int):
                    patterns.append(FixedPattern(field, value))
                
                elif isinstance(value, (Operand, Transform)):
                    patterns.append(VariablePattern(field, value))
                else:  # pragma: no cover
                    raise NotImplementedError(str(value))
        else:
            patterns = d
        return patterns

    def set_patterns(self, tokens):
        """ 用指定的位模式填充令牌 """
        for pattern in self.dict_to_patterns(self.patterns):
            value = pattern.get_value(self) 
            assert isinstance(value, int), str(self) + str(value)
            tokens.set_field(pattern.field, value) 
        self.set_user_patterns(tokens)

    def set_user_patterns(self, tokens):
        """ This is the place for custom patterns """
        pass

    @classmethod
    def from_tokens(cls, tokens):
        """ 从令牌创建这个构造函数 """
        prop_map = {}

        patterns = cls.dict_to_patterns(cls.patterns)

        # Fill patterns:
        for pattern in patterns:
            v = tokens.get_field(pattern.field)
            if isinstance(pattern, FixedPattern):
                #v是输入的值，pattern.value是当前匹配指令的pattern中的值（这里先匹配固定值）
                if v != pattern.value:
                    raise ValueError("")
            elif isinstance(pattern, VariablePattern):
                prop_map[pattern.prop.source] = pattern.prop.from_value(v)
            else:  # pragma: no cover
                raise NotImplementedError(pattern)

        # Create constructors:
        #fargs是所有间接寻址模式
        fargs = cls.syntax.formal_arguments
        for farg in fargs:
            if isinstance(farg._cls, tuple):
                options = farg._cls
                #遍历间接寻址的元组
                for sub_con in options:
                    try:
                        c = sub_con.from_tokens(tokens)
                        prop_map[farg] = c
                    except ValueError:
                        continue

        # 实例化:
        init_args = [prop_map[a] for a in fargs]
        return cls(*init_args)

    @property
    def properties(self):
        """ 返回此语法中可用的所有属性 """
        if not self.syntax:
            return []
        return self.syntax.formal_arguments

    @property
    def leaves(self):
        """ 
        递归地生成所有使用的属性，展开复合道具。
        返回所有属性以及可以获取这些属性的对象。
        """
        for prop in self.properties:
            if prop.is_constructor:
                for propcls in prop.__get__(self).leaves:
                    yield propcls
            else:
                yield prop, self

    @property
    def non_leaves(self):
        """ 获得所有复合部件。这是深度优先循环。
        """
        yield self
        for prop in self.properties:
            if prop.is_constructor:
                s2 = prop.__get__(self)
                # yield s2
                for nl in s2.non_leaves:
                    yield nl

    def gen_relocations(self):
        """ Override this method to generate relocation information """
        return []


class InsMeta(type):
    """ 在isa类中注册指令的元类。 """

    def __init__(cls, name, bases, attrs):
        super(InsMeta, cls).__init__(name, bases, attrs)

        # Register instruction with isa:
        if hasattr(cls, "isa"):
            cls.isa.add_instruction(cls)

    def __add__(cls, other):
        assert isinstance(other, InsMeta)
        tokens = cls.tokens + other.tokens
        p1 = cls.dict_to_patterns(cls.patterns)
        p2 = cls.dict_to_patterns(other.patterns)
        patterns = p1 + p2
        syntax = cls.syntax + other.syntax
        members = {"tokens": tokens, "patterns": patterns, "syntax": syntax}
        member_list = list(cls.__dict__.items())
        member_list += list(other.__dict__.items())
        for name, val in member_list:
            if isinstance(val, Operand):
                if name in members:  # pragma: no cover
                    raise ValueError("{} already defined!".format(name))
                members[name] = val
        name = cls.__name__ + other.__name__
        return InsMeta(name, (Instruction,), members)


class Instruction(Constructor, metaclass=InsMeta):
    """ Base instruction class.

    Instructions are created in the following ways:

    - From python code, by using the instruction directly:
      self.stream.emit(Mov(r1, r2))
    - By the assembler. This is done via a generated parser.
    - By the instruction selector. This is done via pattern matching rules

    Instructions can then be emitted to output streams.

    Instruction classes are automatically added to an
    isa if they have an isa attribute.
    """

    def __init__(self, *args, **kwargs):
        """ Base instruction constructor.

        Takes an arbitrary amount of arguments and tries to fit them
        on the args or syntax fields.
        """
        super().__init__(*args)

        # Initialize the jumps this instruction makes:
        self.jumps = []
        self.ismove = False

        # A list of clobbered registers:
        self.clobbers = []

        # TODO: some instructions, like call, use several registers.
        # Probably this can be handled better:
        self.extra_uses = []
        self.extra_defs = []

        # Set several properties:
        for k, v in kwargs.items():
            assert hasattr(self, k)
            setattr(self, k, v)

    @property
    def used_registers(self):
        """ Return a set of all registers used by this instruction """
        s = []
        for p, o in self.leaves:
            if p._read:
                s.append(p.__get__(o))
        s.extend(self.extra_uses)
        return s

    def reads_register(self, register):
        """ Check if this instruction reads the given register """
        return register in self.used_registers

    @property
    def defined_registers(self):
        """ Return a set of all defined registers """
        s = []
        for p, o in self.leaves:
            if p._write:
                s.append(p.__get__(o))
        s.extend(self.extra_defs)
        return s

    def writes_register(self, register):
        """ Check if this instruction writes the given register """
        return register in self.defined_registers

    @property
    def registers(self):
        """ Determine all registers used by this instruction """
        for p, o in self.leaves:
            if issubclass(p._cls, Register):
                yield p.__get__(o)

    def set_all_patterns(self, tokens):
        """ 查找所有模式并将它们应用于标记 """
        assert hasattr(self, "patterns")
        # self.set_patterns(tokens)
        for nl in self.non_leaves:
            nl.set_patterns(tokens)

    def replace_register(self, old, new):
        """ 用另一个寄存器替换一个寄存器的用法"""
        for p, o in self.leaves:
            if issubclass(p._cls, Register):
                if p.__get__(o) is old:
                    p.__set__(o, new)

    def get_tokens(self):
        #从非叶子节点中提取令牌，根据令牌的属性进行分
        precodes = []
        tokens = []
        for nl in self.non_leaves:
            if hasattr(nl, "tokens"):
                for tc in nl.tokens:
                    t = tc()
                    if t.Info.precode:
                        precodes.append(t)
                    else:
                        tokens.append(t)
        return TokenSequence(precodes + tokens)

    def get_positions(self):
        """ 计算所有部件在字节流中的位置 """
        pos = 0
        positions = {}
        for nl in self.non_leaves:
            positions[nl] = pos
            if hasattr(nl, "tokens"):
                tokens = getattr(nl, "tokens")
                # TODO: this position might not what is expected!
                size = sum(t.Info.size for t in tokens) // 8
            else:
                size = 0
            pos += size
        return positions

    # Interface methods:
    def encode(self):
        """ 将指令编码成二进制形式
            返回该指令的字节数。
        """

        tokens = self.get_tokens()
        self.set_all_patterns(tokens)
        return tokens.encode()

    @classmethod
    def decode(cls, data):
        """ 将数据解码成这个类的指令 """
        # data是输入的二进制，tokens是用户定义的
        tokens = [tok_cls() for tok_cls in cls.tokens]
        tokens = TokenSequence(tokens)
        tokens.fill(data)
        return cls.from_tokens(tokens)

    @classmethod
    def sizes(cls):
        """ Get possible encoding sizes in bytes """
        if hasattr(cls, "tokens"):
            return [sum(t.Info.size for t in cls.tokens) // 8]
        else:
            return []

    def relocations(self):
        """ 确定此指令的总重定位集 """
        relocs = []
        positions = self.get_positions()
        for nl, offset in positions.items():
            for reloc in nl.gen_relocations():
                relocs.append(reloc.shifted(offset))
        return relocs

    def symbols(self):
        return []


class Syntax:
    """ Defines a syntax for an instruction or part of an instruction.

    Arguments:
        syntax: a list of syntax elements.

        new_func: When using this syntax to create
        the instruction, instead of the default constructor, this function
        is called.

        set_props: The set_props property can be used to set additional
        properties after creating the instruction.
    """

    GLYPHS = [
        "@","&","#","=",",",".",":","(",")",
        "[","]","{","}","+","-","*","%","<",
        "0","1","2","3","4","5","6","7","8","9",
        # "A","B","C","D","E","F","G","H","I","J","K","L","M","N",
        # "O","P","Q","R","S","T","U","V","W","X","Y","Z"
    ]

    def __init__(self, syntax, priority=0):
        assert isinstance(syntax, (list, tuple))
        for element in syntax:
            if isinstance(element, str):
                if element.isidentifier():
                    if not element.islower():
                        raise TypeError(
                            'element "{}" must be lower case'.format(element)
                        )
                        pass
                elif element.isspace():
                    pass
                elif element in self.GLYPHS:
                    pass
                else:  # pragma: no cover
                      #raise TypeError('Invalid element "{}"'.format(element))
                    pass
            elif isinstance(element, Operand):
                pass
            else:  # pragma: no cover
                raise TypeError("Element must be string or parameter")
        self.syntax = syntax
        self.priority = priority

        # Pre-calculate format arguments:
        formal_args = []
        for element in self.syntax:
            if isinstance(element, Operand):
                formal_args.append(element)
        self.formal_arguments = formal_args

    def __add__(self, other):
        assert isinstance(other, Syntax)
        assert self.priority == 0
        assert other.priority == 0
        syntax = self.syntax + other.syntax
        return Syntax(syntax)

    def __repr__(self):
        return "{}".format(self.syntax)

    def get_args(self):
        """ Return all non-whitespace elements """
        for element in self.syntax:
            if isinstance(element, str) and element.isspace():
                continue
            yield element

    def render(self, obj):
        """ Return this syntax formatted for the given object. """
        return "".join(self._get_repr(e, obj) for e in self.syntax)

    @staticmethod
    def _get_repr(syntax_element, obj):
        """ Get the repr of a syntax part. Can be str or prop class,
            in refering to an element in the args list """
        if isinstance(syntax_element, str):
            return syntax_element
        elif isinstance(syntax_element, Operand):
            return str(syntax_element.__get__(obj))
        else:  # pragma: no cover
            raise NotImplementedError(str(syntax_element))


class BitPattern:
    """ 基位模式类。位映射是一个字段到某种值的映射。
    """

    def __init__(self, field):
        self.field = field

    def get_value(self, objref):  # pragma: no cover
        raise NotImplementedError("Implement this for your pattern")

    def set_value(self, value):  # pragma: no cover
        raise NotImplementedError("Implement this for your pattern")


class FixedPattern(BitPattern):
    """ 将字段绑定到固定值 """

    def __init__(self, field, value):
        super().__init__(field)
        self.value = value

    def get_value(self, objref):
        return self.value


class VariablePattern(BitPattern):
    # 
    def __init__(self, field, prop):
        super().__init__(field)
        self.prop = prop

    def get_value(self, objref):
        return self.prop.get_value(objref)


class Relocation:
    """ Baseclass for all relocation types.

    Subclass this class to create custom relocations.
    Subclasses should add the following attributes:
    - name: the name used to refer to the relocation type.
    - number: the number that can be used to uniquely identify the relocation.
    - apply: a function that can be used to apply the relocation.
    - calc: a function that calculates the value for the relocation.
    """

    name = None
    number = None
    token = None
    field = None

    def __init__(self, symbol_name, offset=0, addend=0):
        self.symbol_name = symbol_name
        self.addend = addend
        self.offset = offset

    def __repr__(self):
        return "Reloc[{} offset={}]".format(self.name, self.offset)

    def __eq__(self, other):
        return (
            (self.symbol_name == other.symbol_name)
            and (self.offset == other.offset)
            and (type(self) == type(other))
            and (self.addend == other.addend)
        )

    def shifted(self, offset):
        """ Create a shifted copy of this relocation """
        return type(self)(
            self.symbol_name, offset=self.offset + offset, addend=self.addend
        )

    @classmethod
    def size(cls):
        """ Calculate the amount of bytes this relocation requires """
        assert cls.token.Info.size % 8 == 0
        return cls.token.Info.size // 8

    def apply(self, sym_value, data, reloc_value):
        """ Apply this relocation type given some parameters.

        This is the default implementation which stores the outcome of
        the calculate function into the proper token. """
        assert self.token is not None
        token = self.token.from_data(data)
        assert self.field is not None
        assert hasattr(token, self.field)
        setattr(token, self.field, self.calc(sym_value, reloc_value))
        data = token.encode()
        return data

    def can_shrink(self, sym_value, reloc_value):
        """ Test if this relocation can shrink during the relaxation phase.

        Override this method to enable linker relaxation the relocation
        subtype.
        """
        return False

    def calc(self, sym_value, reloc_value):  # pragma: no cover
        """ Calculate the relocation """
        raise NotImplementedError()
