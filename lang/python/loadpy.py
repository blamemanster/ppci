import inspect
import io

from ... import ir
from ...binutils import debuginfo
from .python2ir import python_to_ir
from ppci.binutils.objectfile import print_object
from ppci.lang.c.api import c_to_ir

def load_py(f, imports=None, reporter=None):
    """ 
    加载带有类型注释的python文件。
    参数:F:包含python源代码的类文件对象。
    """
    from ... import api
    from ...utils.codepage import load_obj

    ir_module = python_to_ir(f, imports=imports)
    # ir_module = c_to_ir(f, 'x86_64')
    if reporter:
        reporter.dump_ir(ir_module)

    arch = api.get_current_arch()
    print("arch=====", arch)
    #这里得到的obj就是obj文件
    obj = api.ir_to_object([ir_module], arch, debug=True, reporter=reporter)
    print("obj=====", obj)
    print("print_object====",print_object(obj))
    """ load_obj ->
    obj放入mod中得到m2
    将obj加载内存中,并创建一个mod对象来表示obj的所有信息,包括内存页面、符号表、函数指针和变量指针等
    使得可以在运行时通过mod调用目标对象中的函数,访问其中的数据
    """
    m2 = load_obj(obj, imports=imports)
    print("m2=====", m2)
    return m2


class JittedFunction:
    """ 将源代码、目标代码函数名字、目标代码放入该处，方便在运行时能够调用jit编译后的机器码函数 """

    def __init__(self, original, compiled, mod):
        self.original = original
        self.compiled = compiled
        self.mod = mod

    def __call__(self, *args):
        return self.compiled.__call__(*args)


# def jit(function):
#     """ Jitting function decorator.

#     Can be used to just-in-time (jit) compile and load a function. When
#     a function is decorated with this decorator, the python code is translated
#     into machine code and this code is loaded in the current process.

#     For example:

#     .. testcode:: jit

#         from ppci.lang.python import jit

#         @jit
#         def heavymath(a: int, b: int) -> int:
#             return a + b

#     Now the function can be used as before:

#     .. doctest:: jit

#         >>> heavymath(2, 7)
#         9

#     """
#     #获取传入的函数的源代码
#     source = inspect.getsource(function)

#     #使用ppci库中的load_py函数，将源代码字符串加载为一个Python模块。
#     #mod为目标代码的载体
#     mod = load_py(io.StringIO(source))
#     print("mod===",mod)

#     #获取传入函数的名称，并将其赋值给变量name
#     name = function.__name__
#     print("name===", name)

#     #将原始函数、加载的模块中的函数对象以及模块对象作为参数传递给它。然后将该对象返回。
#     print("JittedFunction=== ",JittedFunction(function, getattr(mod, name), mod))
#     print(" getattr=== ", getattr(mod, name))
#     return JittedFunction(function, getattr(mod, name), mod)

#########################自己添加一个JIT　######################
# """ 自定义一个C语言的JIT """
# def load_py(f, imports=None, reporter=None):
#     from ...utils.codepage import load_obj
#     from ppci.api import cc
#     source_file = f
#     #这里的obj就是CC返回的ir_to_object
#     obj = cc(source_file, 'x86_64')
#     m2 = load_obj(obj, imports=imports)
#     return m2

# def jit(function):
#     # source = inspect.getsource(function)
#     mod = load_py(io.StringIO(function))
#     #mod = load_py( function )
#     print("mod===",mod)
#     #获取传入函数的名称，并将其赋值给变量name
#     name = function.__name__
#     print(name)
#     print(JittedFunction(function, getattr(mod, name), mod))
#     return JittedFunction(function, getattr(mod, name), mod)
#自写
def jit(function):
    # source = inspect.getsource(function)
    # mod = load_py(io.StringIO(source))
    #mod = load_py(function)
    from ppci.arch.target_list import  create_arch
    from ppci import api
    from ...utils.codepage import load_obj
    machine = "riscv"
    march = create_arch(machine)
    ir_module = api.c_to_ir(
        io.StringIO(function), march, coptions=None, reporter=None
    )
    obj = api.ir_to_object(
            [ir_module], march, reporter=None,debug=True
        )
    mod = load_obj(obj, imports=None)
    print("mod===",mod)
    #获取传入函数的名称，并将其赋值给变量name
    name = ir_module.functions[0].name
    print("name===", name)
    print("JittedFunction=== ",JittedFunction(function, getattr(mod, name), mod))

    return JittedFunction(function, getattr(mod, name), mod)




########################################################


def ir_to_dbg(typ):
    if typ is None:
        return
    mp = {
        ir.i64: debuginfo.DebugBaseType("int", 8, 1),
        ir.f64: debuginfo.DebugBaseType("double", 8, 1),
    }
    return mp[typ]


