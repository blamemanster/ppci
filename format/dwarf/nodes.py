class Module:

    def __init__(self, context):
        self.context = context
        #self.data_layout = DataLayout()
        #self.functions = OwnedList(self)
        self.items = {}
        #self.global_list = OwnedList(self)
        #self.lldbg = "" #自己添加llvm的dbg信息

    def add_global_variable(self, v):
        self.global_list.append(v)
        self.vmap[v.name] = v

class Attribute :
    def __init__(self, num, at_name, kv):    
        self.num = num #!0
        self.at_name = at_name
        self.kv = kv #属性键值对
    
    def get_value(self, key):
        if key in self.kv.keys():
            return self.kv[key]
        else:
            return None


void_ty_id = 0
half_ty_id = 1
float_ty_id = 2
double_ty_id = 3
fp128_ty_id = 5
label_ty_id = 7
integer_ty_id = 11
function_ty_id = 12
struct_ty_id = 13
array_ty_id = 14
pointer_ty_id = 15
vector_ty_id = 16
metadata_ty_id = 17 #自己添加


class Type:
    """ The type class """

    def __init__(self, context, type_id):
        self.context = context
        self.type_id = type_id


    @property
    def is_void(self):
        return self.type_id == void_ty_id
    # 添加一个ptr
    @property
    def is_pointer(self):
        return self.type_id == pointer_ty_id
    # 添加一个metadata
    @property
    def is_metadata(self):
        return self.type_id == metadata_ty_id

    @property
    def is_label(self):
        return self.type_id == label_ty_id

    @property
    def is_integer(self):
        return self.type_id == integer_ty_id

    @property
    def is_floating_point(self):
        return self.type_id in [half_ty_id, float_ty_id, double_ty_id]

    @staticmethod
    def get_void_ty(context):
        return context.void_ty

    @staticmethod
    def get_label_ty(context):
        return context.label_ty


class Context:
    """ LLVM context """

    def __init__(self):
        self.void_ty = Type(self, void_ty_id)
        self.half_ty = Type(self, half_ty_id)
        self.float_ty = Type(self, float_ty_id)
        self.double_ty = Type(self, double_ty_id)
        self.label_ty = Type(self, label_ty_id)
        self.pointer_ty = Type(self, pointer_ty_id)  #自己添加
        self.metadata_ty = Type(self, metadata_ty_id)  #自己添加
        self.integer_types = {}
        self.int1_ty = IntegerType.get(self, 1)
        self.int8_ty = IntegerType.get(self, 8)
        self.int16_ty = IntegerType.get(self, 16)
        self.int32_ty = IntegerType.get(self, 32)
        self.int64_ty = IntegerType.get(self, 64)
        self.int128_ty = IntegerType.get(self, 128)
        self.vector_types = []
        self.struct_types = {}
        self.type_map = {}


class IntegerType(Type):
    def __init__(self, context, bits):
        super().__init__(context, integer_ty_id)
        self.bits = bits

    @staticmethod
    def get(context, num_bits):
        """ 获取给定位数的整数类型 """
        if num_bits not in context.integer_types:
            context.integer_types[num_bits] = IntegerType(context, num_bits)
        return context.integer_types[num_bits]




"""定义dwarf节点"""
class DW_TAG_compile_unit:
    def __init__(self, num, DW_AT_name, DW_AT_producer, DW_AT_comp_dir, DW_AT_language):    
        self.num = num
        self.DW_AT_name = DW_AT_name 
        self.DW_AT_producer = DW_AT_producer
        self.DW_AT_comp_dir = DW_AT_comp_dir 
        self.DW_AT_language = DW_AT_language
        self.DW_TAG_compile_unit = "DW_TAG_compile_unit"

        

class DW_TAG_subprogram:
    def __init__(self, num, DW_AT_name, DW_AT_type, DW_AT_low_pc = None, DW_AT_high_pc = None, DW_AT_external = False):    
        self.num = num
        self.DW_AT_name = DW_AT_name 
        self.DW_AT_type = DW_AT_type
        self.DW_AT_low_pc = DW_AT_low_pc
        self.DW_AT_high_pc = DW_AT_high_pc 
        self.DW_AT_external = DW_AT_external
        self.DW_TAG_subprogram = "DW_TAG_subprogram"

class DW_TAG_formal_parameter:
    def __init__(self, num, DW_AT_name, DW_AT_type, DW_AT_location = None):    
        self.num = num
        self.DW_AT_name = DW_AT_name 
        self.DW_AT_type = DW_AT_type
        self.DW_AT_location = DW_AT_location
        self.DW_TAG_formal_parameter = "DW_TAG_formal_parameter"

class DW_TAG_variable:
    def __init__(self, num, DW_AT_name, DW_AT_type, DW_AT_location = None):    
        self.num = num
        self.DW_AT_name = DW_AT_name 
        self.DW_AT_type = DW_AT_type
        self.DW_AT_location = DW_AT_location
        self.DW_TAG_variable = "DW_TAG_variable"

class DW_TAG_base_type:
    def __init__(self, num, DW_AT_encoding, DW_AT_name, DW_AT_byte_size):    
        self.num = num
        self.DW_AT_name = DW_AT_name 
        self.DW_AT_encoding = DW_AT_encoding
        self.DW_AT_byte_size = DW_AT_byte_size
        self.DW_TAG_base_type = "DW_TAG_base_type"
