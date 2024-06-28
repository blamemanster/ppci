from collections import namedtuple
import logging
from ..tools.recursivedescent import RecursiveDescentParser
from..tools import baselex #自己添加
from . import nodes


class LlvmIrParser(RecursiveDescentParser):
    """ llvm-ir的递归下降解析器

    Closely modeled after LLParser.cpp at:
    https://github.com/llvm-mirror/llvm/blob/master/lib/AsmParser/LLParser.cpp 
    """

    logger = logging.getLogger("llvm-parse")

    def __init__(self, context):
        super().__init__()
        self.context = context
        self._pfs = None
        self.module = None
        self.numbered_vals = []

    def parse_module(self):
        """ 解析模块 """
        self.logger.debug("Parsing module")
        flag = 1 # 添加标志
        self.module = nodes.Module(self.context)
        self.forward_refs = {}
        while not self.at_end:
            if self.peek == "define":    # 定义函数或者全局变量
                self.parse_define()
            elif self.peek == "declare": # 声明函数或者全局变量
                self.parse_declare()
            elif self.peek == "target":
                self.parse_target_definition()
            elif self.peek == "LID":
                self.parse_unnamed_type()
            elif self.peek == "LID":
                self.parse_named_type()
            elif self.peek == "GID":
                self.parse_named_global()
            elif self.peek == "attributes":
                if flag:
                    self.module.lldbg = baselex.m.string[baselex.p:] #截取调试信息，使用module.lldbg存储
                    flag = flag - 1 #只截取一次
                self.parse_unnamed_attr_group()
            elif self.peek == "MDVAR":
                if flag:
                    self.module.lldbg = baselex.m.string[baselex.p:] #截取调试信息，使用module.lldbg存储
                    flag = flag - 1 #只截取一次
                self.parse_named_metadata()
            elif self.peek == "!":
                if flag:
                    self.module.lldbg = baselex.m.string[baselex.p:] #截取调试信息，使用module.lldbg存储
                    flag = flag - 1 #只截取一次
                self.parse_standalone_metadata()
            elif self.peek == "EOF":
                self.test1()
            else:  # pragma: no cover
                self.error("TODO!!!!!")
                raise NotImplementedError(str(self.peek))
        return self.module

    def parse_unnamed_type(self):
        """ Parse LocalVarID '=' 'type' type """
        name = self.consume("LID")
        print(name)
        self.consume("=")
        self.consume("type")
        self.parse_struct_definition()

    def parse_named_type(self):
        """ Parse LocalVar '=' 'type' type """
        self.consume("=")
        self.consume("type")
        self.parse_struct()

    def parse_define(self):
        """ 解析函数 """
        self.consume("define")  # 获取下一个token
        function = self.parse_function_header()
        self.parse_function_body(function)

    def parse_named_global(self):
        self.consume("GID")
        self.consume("=")
        self.parse_optional_linkage()
        self.parse_global()

    def parse_global(self):
        is_constant = self.parse_global_type()
        ty = self.parse_type()
        self.parse_global_value(ty)
        print(is_constant)

    def parse_global_type(self):
        if self.has_consumed("constant"):
            return True
        elif self.has_consumed("global"):
            return False
        else:
            self.error("Expected 'global' or 'constant'")

    def parse_function_body(self, function):
        self._pfs = PerFunctionState(self, function) #用于跟踪函数解析过程中的状态信息
        self.consume("{")
        while self.peek != "}":
            self.parse_basic_block()
        self.consume("}")
        self._pfs = None #清理相应的状态信息

    def parse_declare(self):
        """ Parse a function declaration """
        self.consume("declare")
        function = self.parse_function_header()
        print(function)

    def parse_function_header(self):
        return_type = self.parse_type() #解析函数的返回类型
        name = self.parse_name(global_name=True) #解析函数的名称。
        arg_list = self.parse_argument_list() #解析函数的参数列表
        attributes = self.parse_fn_attribute_value_pairs() #解析函数的属性和值对
        print(attributes)
        param_types = [a.type for a in arg_list] #获取参数列表中每个参数的类型，并将其保存在 param_types 列表中
        if self.peek == "ATTRID":
            self.consume("ATTRID")
        lldbg = self.parse_lldbg() # 添加解析llvm调试信息,并且在create函数中添加该参数
        function_type = nodes.FunctionType.get(return_type, param_types) #使用返回类型和参数类型创建函数类型对象
        function = nodes.Function.create(function_type, name, self.module, lldbg) #使用函数类型、名称和模块信息创建函数对象  //#自己添加lldbg参数
        for argument, arg_info in zip(function.arguments, arg_list): #对函数的每个参数进行处理，设置参数的名称
            if arg_info.name:
                argument.set_name(arg_info.name)
            else:
                # The parameter had no name, so number it?
                name = "%{}".format(len(self.numbered_vals))
                argument.set_name(name)
                self.numbered_vals.append((name, argument))
        return function

    def parse_target_definition(self):
        """ Parse a target top level entity """
        self.consume("target")
        if self.peek == "triple":
            self.consume("triple")
            self.consume("=")
            val = self.parse_string_constant()
        else:
            self.consume("datalayout")
            self.consume("=")
            val = self.parse_string_constant()
            self.module.data_layout = nodes.DataLayout.from_string(val)
        return val

    def parse_unnamed_attr_group(self):
        self.consume("attributes")
        attr_id = self.consume("ATTRID")
        self.consume("=")
        self.consume("{")
        attributes = self.parse_fn_attribute_value_pairs()
        print(attributes)
        self.consume("}")
        return attr_id

    def parse_fn_attribute_value_pairs(self):
        attributes = []
        while True:
            if self.peek in ["nounwind", "sspstrong", "uwtable", "readonly", "noinline", "optnone",
                             "nocallback","nofree","nosync","speculatable","willreturn",]:#自己添加
                a = self.consume().val
                attributes.append(a)
            elif self.peek in ["memory", "range"]: #添加新数据格式处理 memory(none) range(2, 6) 等
                b = self.consume().val #
                tem = [] #
                self.consume("(") #
                while self.peek != ")": #
                    tem.append(self.consume().val) #数据暂存于tem列表
                    if self.peek != ")": #
                        self.consume(",") #
                self.consume(")") #
                attributes.append({b : tem}) #使用字典存储
            elif self.peek == "STR":
                key = self.parse_string_constant()
                if self.has_consumed("="):
                    val = self.parse_string_constant()
                else:
                    val = None
                attributes.append((key, val))
            else:
                break
        return attributes

    def create_global_fwd_ref(self, module, pty, name):
        if isinstance(pty.el_type, nodes.FunctionType):
            self.not_impl()
        else:
            return nodes.GlobalVariable(pty.el_type, name, module=module)

    def get_global_val(self, name, ty):
        """ Get a global with the given id """
        if not isinstance(ty, nodes.PointerType):
            self.error("global variable reference must have pointer type")

        if name in self.module.vmap:
            val = self.module.vmap[name]
        elif name in self.forward_refs:
            val = self.forward_refs[name]
        else:
            print(self.module, ty, name)
            val = self.create_global_fwd_ref(self.module, ty, name)
            self.forward_refs[name] = val
        return val

    def parse_named_metadata(self):
        """ Parse meta data starting with '!my.var'  """
        self.consume("MDVAR")
        self.consume("=")
        self.consume("!")
        self.consume("{")
        while self.peek != "}":
            self.consume()
        self.consume("}")

    def parse_standalone_metadata(self):
        """ Parse meta data starting with '!' 'num' """
        self.consume("!")
        self.parse_number()
        self.consume("=")
        if self.peek == "distinct":
            self.consume("distinct")
        if self.peek == "!":
            self.consume("!")
        self.parse_md_node_vector()

    def parse_md_node_vector(self):
        if self.peek == "{":
            self.consume("{")
            elements = []
            while self.peek != "}":
                # self.consume()
                # TODO: parse meta data!
                metadata = self.parse_metadata()
                elements.append(metadata)
                if self.peek != "}":
                    self.consume(',')
            self.consume("}")
        else : #自己添加解析调试信息
            if self.peek == "distinct":
                self.consume("distinct")
            self.consume("MDVAR")
            self.consume("(")
            elements={}
            while self.peek != ")":
                # self.consume()
                # TODO: parse meta data!
                metadata = self.parse_metadata1() # 仿
                elements.update(metadata)
                if self.peek != ")":
                    self.consume(',')
            self.consume(")")
        print(elements)
        return elements

    def parse_metadata(self):
        """ Parse meta data

        i32 1
        !42
        !{...}
        !"string"
        
        """
        if self.peek == "!":
            self.consume("!")
            if self.peek == "{":
                # 添加 Parse metadata node
                metadata = self.parse_md_node_vector()
            elif self.peek == "STR":
                # 添加 Parse string metadata
                metadata = self.parse_string_constant()
            elif self.peek == "NUMBER":
                # 添加 Parse number metadata
                metadata = self.parse_number()
        elif self.peek == "type":
            self.consume("type")
                # 添加 Parse number metadata
            metadata = self.parse_number()
        else :
            metadata = self.peek
            self.consume()

        return metadata

    def parse_metadata1(self): #自己仿造
            """ Parse meta data

            name : "lock"
            scope : !2
            line : 45
            !DIExpression()

            """
            tem1 = self.consume("LBL").val
            tem1=tem1[:-1] # 除去 :

            if self.peek == "!":
                self.consume("!")
            if self.peek == "NUMBER":
                tem2 = self.parse_number()
            elif self.peek == "STR":
                tem2 = self.parse_string_constant()
            elif self.peek == "MDVAR":
                tem2 = self.parse_md_node_vector()
            else : #匹配ID类型
                tem2 = self.peek
                self.consume()
            metadata = {tem1 : tem2}

            return metadata

    def test1(self):
            """ 自己添加：用来匹配EOF """
            self.consume("EOF")

    """ 原始代码 """
    # def parse_md_node_vector(self):
    #     self.consume("{")
    #     elements = []
    #     while self.peek != "}":
    #         self.consume()
    #         # TODO: parse meta data!
    #         # if elements:
    #         #    self.consume(',')
    #         # metadata = self.parse_metadata()
    #         # elements.append(metadata)
    #     self.consume("}")
    #     return elements

    # def parse_metadata(self):
    #     """ Parse meta data

    #     !42
    #     !{...}
    #     !"string"

    #     """
    #     if self.peek == "!":
    #         self.consume("!")
    #     else:
    #         md = 1
    #     return md


    def parse_string_constant(self):
        return self.consume("STR").val

    def parse_basic_block(self):
        if self.peek == "LBL": # 检查当前的词元（token）是否为标签（label） 
            label = self.consume("LBL").val
        else:
            label = None
        # 在这里定义基本块？？？
        bb = self._pfs.define_bb(label)

        # Parse instructions until terminator
        while True:
            if self.peek == "LID": #检查当前的词元是否为指令的名称标识符
                name = self.parse_name()
                self.consume("=")
            else:
                name = None
            # 解析指令
            instruction = self.parse_instruction()
            # 将解析完的指令添加到当前基本块的指令列表中
            bb.instructions.append(instruction)
            if name:
                self._pfs.set_instruction_name(name, instruction)
            # 什么指令才是终止指令？？
            if instruction.is_terminator:
                break
        return bb

    def parse_argument_list(self):
        """ Parse '(' ... ')' """
        self.consume("(")
        args = []
        if self.peek == ")":
            pass
        else:
            args.append(self.parse_arg())
            while self.has_consumed(","):
                args.append(self.parse_arg())
        self.consume(")")
        return args

    def parse_arg(self):
        ty = self.parse_type()
        attrs = self.parse_optional_param_attrs()
        # print(attrs)
        if self.peek == "LID":
            name = self.consume("LID").val
        else:
            name = None
        return ArgInfo(ty, name)

    def parse_optional_param_attrs(self):
        attrs = []
        while True:
            if self.peek in ["nocapture", "nonnull"]:
                attr = self.consume().val
                attrs.append(attr)
            else:
                break
        return attrs

    def parse_optional_linkage(self):
        if self.has_consumed("private"):
            pass
        else:
            pass

    def parse_type(self):
        if self.peek == "type":
            typ = self.consume("type").val
            if self.peek == "type": #添加处理两个类型的情况 ：metadata ptr %2
                self.consume("type")
            if self.peek == "noundef":  # 处理 i32 noundef %0 的情况
                self.consume("noundef")
        elif self.peek == "dso_local":  # 添加了一个处理 dso_local
            self.consume("dso_local")
            typ = self.parse_type()  #继续往下解析类型
        elif self.peek == "noundef":  # 添加了一个处理 noundef
            self.consume("noundef")
            typ = self.parse_type()  #继续往下解析类型
        elif self.peek == "nsw":  # 添加了一个处理 nsw
            self.consume("nsw")
            typ = self.parse_type()  #继续往下解析类型
        # elif self.peek == "metadata":  # 添加了一个处理 metadata
        #     self.consume("metadata")
        #     if self.peek == "type":
        #         typ = self.parse_type()  #后面存在类型，则继续往下解析类型
        #     typ = nodes.MetadatdType(self.context) # typ仍然是metadata
        elif self.peek == "ptr":  # 添加了一个处理 nsw
            # self.consume("ptr")
            typ = nodes.PointerType.get_unequal(typ) 
        elif self.peek == "{":
            typ = self.parse_anon_struct_type(packed=False)
        elif self.peek == "[":
            typ = self.parse_array_vector_type(False)
        elif self.peek == "<":
            typ = self.parse_array_vector_type(True)
        elif self.peek == "LID":
            lid = self.consume("LID")
            # named_types[lid]
            # print(lid)
            typ = nodes.StructType.get(self.context, [], False)
        else:  # pragma: no cover
            self.not_impl()

        assert isinstance(typ, nodes.Type), str(typ)

        # 解析后缀:
        while True:
            if self.peek == "*":
                self.consume("*")
                typ = nodes.PointerType.get_unequal(typ)
            elif self.peek == "(":
                typ = self.parse_function_type(typ)
            else:
                break
        return typ

    def parse_function_type(self, result):
        arg_list = self.parse_argument_list()
        return nodes.FunctionType.get(result, arg_list)

    def parse_anon_struct_type(self, packed=False):
        elts = self.parse_struct_body()
        return nodes.StructType.get(self.context, elts, packed)

    def parse_struct_definition(self):
        body = self.parse_struct_body()
        # print(body)

    def parse_struct_body(self):
        """ Parse struct body.

        Can be either of:
        '{' '}'
        '{' type (',' type)* '}'
        """
        body = []
        self.consume("{")
        if self.has_consumed("}"):
            return body
        ty = self.parse_type()
        body.append(ty)
        while self.has_consumed(","):
            ty = self.parse_type()
            body.append(ty)
        self.consume("}")
        return body

    def parse_array_vector_type(self, is_vector):
        if is_vector:
            self.consume("<")
        else:
            self.consume("[")
        size = self.parse_number()
        self.consume("x")
        ty = self.parse_type()
        if is_vector:
            self.consume(">")
            return nodes.VectorType.get(ty, size)
        else:
            self.consume("]")
            return nodes.ArrayType.get(ty, size)

    def parse_number(self):
        return self.consume("NUMBER").val

    def parse_name(self, global_name=False):
        if global_name:
            return self.consume("GID").val
        else:
            return self.consume("LID").val

    def parse_lldbg(self): #自己定义解析llvm调试信息函数
        lldbg = {} # 字典
        while True:
            # 添加解析 !dbg，!tbaa等
            if self.peek == "MDVAR":
                a = self.consume("MDVAR").val
                # 添加解析 !num
                self.consume("!")
                b = "!"+str(self.parse_number())
                if a not in lldbg:
                    lldbg[a] = set()
                lldbg[a].add(b) # 存储格式 lldbg = {"!dbg": {'!0','!1'}, "!tbaa": {'!2'}}
            if self.peek == ",":
                self.consume(",")
            else:
                break
        return lldbg

    def parse_global_value(self, ty):
        v = self.parse_val_id()
        v2 = self.convert_val_id_to_value(ty, v)
        return v2

    def parse_value(self, ty):
        """ 解析具有特定类型的值 """
        v = self.parse_val_id() #kind=local，val=%2
        v2 = self.convert_val_id_to_value(ty, v)
        return v2

    def parse_val_id(self):
        """ 一些更抽象的值解析 """
        if self.peek == "zeroinitializer":
            self.consume("zeroinitializer")
            v = ValId("zero", None)
        elif self.peek == "!": #添加处理 !num 类型
            self.consume("!") #
            v = ValId("!", "!" + str(self.consume("NUMBER").val)) # v=!14
        elif self.peek == "MDVAR": #添加处理 MDVAR 类型
            tem = self.consume("MDVAR").val  #
            if self.peek == "(": #
                tem += self.consume().val #
                while self.peek != ")": #
                    tem += self.consume().val #
                tem += self.consume().val #
            v = ValId("!", tem) # v=!DIExpression()
        elif self.peek == "LID":
            v = ValId("local", self.parse_name())
        elif self.peek == "GID":
            v = ValId("global", self.parse_name(global_name=True))
        elif self.peek == "NUMBER":
            v = ValId("int", self.consume("NUMBER").val)
        elif self.peek == "HEXDOUBLE":
            v = ValId("float", self.consume("HEXDOUBLE").val)
        elif self.peek == "undef":
            self.consume("undef")
            v = ValId("undef", None)
        elif self.peek == "true":
            self.consume("true")
            v = ValId("constant", nodes.ConstantInt.get_true(self.context))
        elif self.peek == "false":
            self.consume("false")
            v = ValId("constant", nodes.ConstantInt.get_false(self.context))
        elif self.peek == "{":
            self.consume("{")
            elts = self.parse_global_value_vector()
            self.consume("}")
            v = ValId("constant_struct", elts)
        elif self.peek == "<":
            # '<' constvect '>'
            self.consume("<")
            elts = self.parse_global_value_vector()
            self.consume(">")
            v = ValId("constant", nodes.ConstantVector.get(elts))
        elif self.peek == "getelementptr":
            self.consume("getelementptr")
            in_bounds = self.has_consumed("inbounds")
            # print(in_bounds)
            self.consume("(")
            ty = self.parse_type()
            # print(ty)
            self.consume(",")
            elts = self.parse_global_value_vector()
            self.consume(")")
            v = ValId("constant_gep", elts)
        else:  # pragma: no cover
            self.not_impl()
        assert isinstance(v, ValId), str(v)
        return v

    def convert_val_id_to_value(self, ty, val_id):
        if val_id.kind == "local":
            v = self._pfs.get_val(val_id.val, ty)
        elif val_id.kind == "global":
            v = self.get_global_val(val_id.val, ty)
        elif val_id.kind == "int":
            if not ty.is_integer:
                self.error("integer constant must have integer type")
            v = nodes.ConstantInt.get(ty, val_id.val)
        elif val_id.kind == "float":
            if not ty.is_floating_point:
                self.error("Floating point constant invalid for type")
            v = nodes.ConstantFP.get(ty, val_id.val)
        elif val_id.kind == "zero":
            v = nodes.Constant.get_null_value(ty)
        elif val_id.kind == "undef":
            v = nodes.UndefValue.get(ty)
        elif val_id.kind == "constant":
            v = val_id.val
            if v.ty is not ty:
                self.error("constant expression type mismatch")
        elif val_id.kind == "!":
            v = nodes.MetadataInt.get(ty, val_id.val) #添加metadata节点测试
        else:
            raise NotImplementedError(str(val_id))
        return v

    def parse_type_and_value(self):
        ty = self.parse_type() #看下这里
        val = self.parse_value(ty)
        return val

    def parse_type_and_basic_block(self):
        value = self.parse_type_and_value()
        if not isinstance(value, nodes.BasicBlock):
            self.error("Expected a basic block")
        return value

    def parse_global_value_vector(self):
        """ """
        v = []
        v.append(self.parse_global_type_and_value())
        while self.has_consumed(","):
            v.append(self.parse_global_type_and_value())
        return v

    def parse_global_type_and_value(self):
        ty = self.parse_type()
        val = self.parse_global_value(ty)
        return val

    # Instructions
    def parse_instruction(self):
        """ Parse a single instruction """
        #这里加上ptr的处理来生成指令，这里是生成PPCI的IR
        if self.peek == "store":
            instruction = self.parse_store()
        elif self.peek == "call":
            instruction = self.parse_call()
        elif self.peek == "ret":
            instruction = self.parse_ret()
        elif self.peek == "br":
            instruction = self.parse_br()
        # 增加一个switch匹配
        elif self.peek == "switch":
            instruction = self.parse_switch()

        elif self.peek == "alloca":
            instruction = self.parse_alloca()
        elif self.peek == "load":
            instruction = self.parse_load()
        elif self.peek == "extractelement":
            instruction = self.parse_extract_element()
        elif self.peek == "insertelement":
            instruction = self.parse_insert_element()
        elif self.peek == "shufflevector":
            instruction = self.parse_shuffle_vector()
        elif self.peek in [
            "add",
            "fadd",
            "sub",
            "fsub",
            "mul",
            "fmul",
            "udiv",
            "sdiv",
            "fdiv",
            "urem",
            "srem",
            "shl",
            "lshr",
            "ashr",  
        ]:
            instruction = self.parse_arithmatic()
        elif self.peek in ["and", "or", "xor"]:
            instruction = self.parse_arithmatic()
        elif self.peek in [
            "sext",
            "zext",
            "trunc",
            "fptrunc",
            "uitofp",
            "fptoui",
            "sitofp",
            "fptosi",
            "ptrtoint",
            "inttoptr",
        ]:
            instruction = self.parse_cast()
        elif self.peek == "select":
            instruction = self.parse_select()
        elif self.peek in ["icmp", "fcmp"]:
            instruction = self.parse_compare()
        elif self.peek == "getelementptr":
            instruction = self.parse_getelementptr()
        elif self.peek == "phi":  #自己添加
            instruction = self.parse_phi() 
        else:  # pragma: no cover
            self.not_impl()
        return instruction

    def parse_arithmatic(self):
        op = self.consume().val
        lhs = self.parse_type_and_value()
        self.consume(",")
        rhs = self.parse_value(lhs.ty)

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.BinaryOperator.create(op, lhs, rhs, lldbg) #添加lldbg参数

    def parse_cast(self):
        op = self.consume()
        val = self.parse_type_and_value()
        self.consume("to")
        dest_ty = self.parse_type()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.CastInst.create(op, val, dest_ty, lldbg) #添加lldbg参数

    def parse_select(self):
        self.consume("select")
        op0 = self.parse_type_and_value()
        self.consume(",")
        op1 = self.parse_type_and_value()
        self.consume(",")
        op2 = self.parse_type_and_value()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.SelectInst.create(op0, op1, op2, lldbg) #添加lldbg参数

    def parse_compare(self):
        icmp = self.peek == "icmp"
        if icmp:
            self.consume("icmp")
        else:
            self.consume("fcmp")
        pred = self.parse_cmp_predicate(icmp)
        lhs = self.parse_type_and_value()
        self.consume(",")
        rhs = self.parse_value(lhs.ty)

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.ICmpInst(pred, lhs, rhs, lldbg) #添加lldbg参数

    def parse_cmp_predicate(self, icmp):
        if icmp:
            predicates = {
                "eq": nodes.CmpInst.ICMP_EQ,
                "ne": nodes.CmpInst.ICMP_NE,
                "slt": nodes.CmpInst.ICMP_SLT,
                "sgt": nodes.CmpInst.ICMP_SGT,
                "sle": nodes.CmpInst.ICMP_SLE,
                "sge": nodes.CmpInst.ICMP_SGE,
                "ult": nodes.CmpInst.ICMP_ULT,
                "ugt": nodes.CmpInst.ICMP_UGT,
                "ule": nodes.CmpInst.ICMP_ULE,
                "uge": nodes.CmpInst.ICMP_UGE,
            }
        else:
            predicates = {"ueq": nodes.CmpInst.FCMP_UEQ}
        if self.peek in predicates:
            v = self.consume().val
            return predicates[v]
        else:
            self.error("Expected one of {}".format(predicates.keys()))

    def parse_alloca(self):
        self.consume("alloca")
        ty = self.parse_type()
        size = 0
        alignment = 0
        if self.peek == ",":
            self.consume(",")
            self.consume("align")
            self.parse_number()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.AllocaInst(ty, size, alignment, lldbg) #添加lldbg参数

    def parse_extract_element(self):
        self.consume("extractelement")
        op1 = self.parse_type_and_value()
        self.consume(",")
        op2 = self.parse_type_and_value()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.ExtractElementInst(op1, op2, lldbg) #添加lldbg参数

    def parse_insert_element(self):
        self.consume("insertelement")
        op1 = self.parse_type_and_value()
        self.consume(",")
        op2 = self.parse_type_and_value()
        self.consume(",")
        op3 = self.parse_type_and_value()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.InsertElementInst(op1, op2, op3, lldbg) #添加lldbg参数

    def parse_shuffle_vector(self):
        """ Parse the shuffle vector """
        self.consume("shufflevector")
        op1 = self.parse_type_and_value()
        self.consume(",")
        op2 = self.parse_type_and_value()
        self.consume(",")
        op3 = self.parse_type_and_value()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.ShuffleVectorInst(op1, op2, op3, lldbg) #添加lldbg参数

    def parse_load(self):
        """ 解析加载指令

        'load' 'volatile'? typeandvalue (',' 'align' i32)?
        """
        self.consume("load")
        atomic = self.has_consumed("atomic")
        volatile = self.has_consumed("volatile")
        # print(atomic, volatile)
        ty = self.parse_type()
        self.consume(",")
        val = self.parse_type_and_value()
        if self.has_consumed(","):
            self.consume("align")
            self.parse_number()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.LoadInst(ty, val, lldbg) #添加lldbg参数

    def parse_store(self):
        """ 解析存储指令 """
        self.consume("store")
        val = self.parse_type_and_value()
        self.consume(",")
        ptr = self.parse_type_and_value()
        if self.has_consumed(","):
            self.consume("align")
            self.parse_number()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.StoreInst(val, ptr, lldbg) #添加lldbg参数

    def parse_getelementptr(self):
        """ 解析get元素ptr (GEP) """
        self.consume("getelementptr")
        inbounds = self.has_consumed("inbounds")
        ty = self.parse_type()
        self.consume(",")
        ptr = self.parse_type_and_value()
        indices = []
        while self.has_consumed(","):
            val = self.parse_type_and_value()
            indices.append(val)

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        gep = nodes.GetElementPtrInst(ty, ptr, indices, lldbg) #添加lldbg参数
        gep.inbounds = inbounds
        return gep

    def parse_call(self):
        self.consume("call")
        ret_type = self.parse_type()
        #----------临时添加-------
        if self.peek == "asm":
            self.consume("asm")
            if self.peek == "sideeffect":
                self.consume("sideeffect")
            name = "asm" + self.parse_string_constant()
            self.consume(",")
            self.parse_string_constant()
            args = self.parse_parameter_list()
            if self.peek == "ATTRID":
                self.consume("ATTRID")
        #-----------------------------
        else:
            name = self.parse_name(global_name=True)
            args = self.parse_parameter_list()

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.CallInst(ret_type, name, args, lldbg) #添加lldbg参数)

    def parse_parameter_list(self):
        self.consume("(")
        args = []
        while self.peek != ")":
            if args:
                self.consume(",")
            ty = self.parse_type()
            v = self.parse_value(ty)
            args.append(v)
        self.consume(")")
        return args

    def parse_ret(self):
        """ Parse return instruction """
        self.consume("ret")
        ty = self.parse_type()

        if ty.is_void:
            lldbg = "" #自己添加
            if self.peek == ",": # 添加解析llvm调试信息
                self.consume(",") #
                lldbg = self.parse_lldbg() #
            return nodes.ReturnInst(ty, None, lldbg) #添加lldbg参数
        else:
            val = self.parse_value(ty)
            lldbg = "" #自己添加
            if self.peek == ",": # 添加解析llvm调试信息
                self.consume(",") #
                lldbg = self.parse_lldbg() #
            return nodes.ReturnInst(ty, val, lldbg) #添加lldbg参数

    def parse_br(self):
        """ Parse a branch instruction """
        self.consume("br")
        op0 = self.parse_type_and_value()
            
        if isinstance(op0, nodes.BasicBlock):

            lldbg = "" #自己添加
            if self.peek == ",": # 添加解析llvm调试信息
                self.consume(",") #
                lldbg = self.parse_lldbg() #
            return nodes.BranchInst(op0, None,None,lldbg) #添加lldbg参数
        else:
            self.consume(",")
            op1 = self.parse_type_and_basic_block()
            self.consume(",")
            op2 = self.parse_type_and_basic_block()

            lldbg = "" #自己添加
            if self.peek == ",": # 添加解析llvm调试信息
                self.consume(",") #
                lldbg = self.parse_lldbg() #
            return nodes.BranchInst(op1, op2, op0, lldbg) #添加lldbg参数

    # 增加一个对switch指令的解析
    def parse_switch(self):
        self.consume("switch") 
        op0 = self.parse_type_and_value() #得到待比较的数
        self.consume(",")
        default_block = self.parse_type_and_basic_block() #得到跳出switch后的基本块
        self.consume("[")  # 跳过左方括号
        cases = []
        while True:
            value = self.parse_type_and_value()  # 解析case的值
            self.consume(",")
            block = self.parse_type_and_basic_block()   #得到要跳转到的基本块
            cases.append((value, block))   
            if self.peek == ']':  # 如果遇到右方括号，表示解析完成
                break

        self.consume(']')  # 跳过右方括号

        lldbg = "" #自己添加
        if self.peek == ",": # 添加解析llvm调试信息
            self.consume(",") #
            lldbg = self.parse_lldbg() #
        return nodes.SwitchInst( op0, default_block, cases, lldbg) #添加lldbg参数

    def parse_phi(self):
        """ Parse a phi instruction.

        For example 'phi' Type '[' Value ',' Value ']' (',' ...) *
        """
        self.consume("phi")
        self.parse_type()
        self.consume("[")
        self.parse_value()
        self.consume(",")
        self.parse_value()
        self.consume("]")
        while self.has_consumed(","):
            self.consume("[")
            self.parse_value()
            self.consume(",")
            self.parse_value()
            self.consume("]")


class PerFunctionState:
    """ 跟踪函数中的解析内容 """

    def __init__(self, parser, function):
        self.parser = parser
        self.function = function
        self.forward = {}

    def get_val(self, name, ty):
        """ 获取具有名称和给定类型的值 """
        # Lookup the name:
        if name in self.function.vmap:
            val = self.function.vmap[name]
        elif name in self.forward:
            val = self.forward[name]
        else:
            if ty.is_label:
                val = nodes.BasicBlock.create(
                    self.function.context, name, self.function
                )
            else:
                raise NotImplementedError(str(ty))
            self.forward[name] = val

        # if ty is not val.ty:
        #     self.parser.error("{} != {}".format(ty, val.ty))
        return val

    def get_bb(self, name):
        return self.get_val(name, self.function.context.label_ty)

    def define_bb(self, name):
        bb = self.get_bb(name)

        #在函数内部定义基本块:
        self.function.basic_blocks.append(bb)
        self.forward.pop(name)
        return bb

    def set_instruction_name(self, name, instruction):
        # This will update the symbol table:
        instruction.set_name(name)

        # Remove placeholder:
        if name in self.forward:
            sentinel = self.forward.pop(name)
            if sentinel.ty is not instruction.ty:
                self.parser.error(
                    "Instruction forward referenced with type {}".format(
                        sentinel.ty
                    )
                )
            sentinel.replace_all_uses_with(instruction)


ValId = namedtuple("ValId", ["kind", "val"])
ArgInfo = namedtuple("ArgInfo", ["type", "name"])
