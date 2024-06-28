import re

# from ...common import make_num
from ..tools.baselex import BaseLexer
from . import nodes


class LlvmIrLexer(BaseLexer):
    types = [
        "void",
        "double",
        "float",
        "label",
        "i64",
        "i32",
        "i16",
        "i8",
        "i1",
        "f32",
        "f16",
        #添加ptr
        "ptr",
        "nsw",
        "metadata",
    ]

    keywords = [
        "define",
        "declare",
        "type",
        "target",
        "triple",
        "datalayout",
        "attributes",
        "noinline",
        "optnone",
        "nounwind",
        "sspstrong",
        "uwtable",
        "readonly",
        "private",
        "constant",
        "nonnull",
        "align",
        "inbounds",
        "nocapture",
        "nsw",# 自己添加
        # "ptr",# 自己添加
        "dso_local", # 自己添加
        "distinct", # 添加distinct
        "null",# 添加null
        "noundef",
        "ret",
        "br",
        "call",
        "icmp",
        "fcmp",
        "eq",
        "ne",
        "slt",
        "sgt",
        "sle",
        "sge",
        "ule",
        "ult",
        "uge",
        "ugt",
        "ueq",
        "select",
        "x",
        "zeroinitializer",
        "undef",
        "alloca",
        "load",
        "store",
        "switch",  # 自己添加
        "getelementptr",
        "extractelement",
        "insertelement",
        "shufflevector",
        "add",
        "sub",
        "mul",
        "shl",
        "lshr",
        "ashr",  
        "srem",
        "urem",
        "fadd",
        "fsub",
        "fmul",
        "fdiv",
        "sdiv",
        "frem",
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
        "to",
        "or",
        "xor",
        "and",
        "true",
        "false",
        "rol",
        "ror",
        # 自己添加
        "DIFlagPrototyped",
        "DISPFlagDefinition",
        "FullDebug",
        "CSK_MD5",
        "DW_LANG_C11",
        "None",
        "DW_ATE_signed",
        "DW_TAG_pointer_type",     
        "nocallback",#
        "nofree",
        "nosync",
        "speculatable",
        "willreturn",
        "memory",
        "none",
        "readnone",
        "readonly",
        "writeonly",
        "readwrite",
        "clobber",
        "range",
        "phi",#添加
        "",
        "",
        "",
        "",
        "",

    ]
    glyphs = (",", "=", "{", "}", "(", ")", "*", "<", ">", "[", "]", "!")

    def __init__(self, context):
        # Construct the string of possible glyphs:
        op_txt = "|".join(re.escape(g) for g in self.glyphs)
        tok_spec = [
            (
                "HEXDOUBLE",
                r"0x[KLMHJ]?[\da-fA-F]+",
                lambda typ, val: (typ, val),
            ),
            # ('HEXNUMBER', r'0x[\da-fA-F]+',
            #  lambda typ, val: ('NUMBER', make_num(val))),
            ("NUMBER", r"[\-\+]?\d+", lambda typ, val: (typ, int(val))),
            ("GID", r"@[A-Za-z\d_\.]+", lambda t, v: (t, v)),
            (
                "LID",
                r'%[A-Za-z\d_]+|%"[A-Za-z\d_\.\:\<\>\&\[\]]+"',
                lambda t, v: (t, v),
            ),
            ("ATTRID", r"#\d+", lambda t, v: (t, v)),
            ("MDVAR", r"![a-zA-Z_][a-zA-Z\d\.]*", lambda t, v: (t, v)),
            ("LBL", r"[A-Za-z_][A-Za-z\d_]*:", lambda t, v: (t, v)),
            ("ID", r"[A-Za-z_][A-Za-z\d_]*", self.handle_id),
            ("LINECOMMENT", r";[^\n\r]*", None),
            ("STR", r'"[^"]*"', lambda typ, val: (typ, val[1:-1])),
            ("NEWLINE", r"\n", lambda typ, val: self.newline()),
            ("SKIP", r"[ \t]", None),
            ("GLYPH", op_txt, lambda typ, val: (val, val)),
        ]
        super().__init__(tok_spec)
        self.context = context

    def handle_id(self, typ, val):
        if val in self.keywords:
            typ = val
        elif val in self.types:
            typ = "type"
            # 这里没有处理f32和f16的类型
            if val == "void":
                val = self.context.void_ty
            elif val == "float":
                val = self.context.float_ty
            elif val == "double":
                val = self.context.double_ty
            elif val == "label":
                val = self.context.label_ty
            elif val.startswith("i"):
                bits = int(val[1:]) #获取32类型
                val = nodes.IntegerType.get(self.context, bits)
            # 增加一个ptr的类型处理
            elif val == "ptr":
                #这里val有问题
                # val = self.context.pointer_ty
                val = self.context.pointer_ty
            elif val == "nsw":
                #增加对nsw的处理
                val = self.context.pointer_ty
            elif val == "metadata":
                #增加对metadata的处理
                val = self.context.metadata_ty
            else:  # pragma: no cover
                raise NotImplementedError(val)
        else:  # pragma: no cover
            raise NotImplementedError(val)
        return typ, val
