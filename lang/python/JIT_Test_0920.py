""" 测试其他架构的python的JIT """

from ppci.lang.c.api import c_to_ir
from ppci.lang.python import jit
from ppci import api
from ppci.lang.python.python2ir import python_to_ir
import io


f = "int add(int a,int b) {return a+b;}"
add = jit(f)
R2 = add.compiled(2,1)
print("R2===", R2)
# imports=None
# reporter=None

# ir_module = python_to_ir(f, imports=imports)
# obj = api.ir_to_object([ir_module], "arm", debug=True, reporter=reporter)
# #obj = api.ir_to_object([ir_module], "x86_64", debug=True, reporter=reporter)
# print("obj=====", obj)
# print("success!!!!!")

# @jit  
# def heavymath(a: int, b: int) -> int:
#     return a + b

# # heavymath函数可被调用
# R1 = heavymath.original
# R2 = heavymath.compiled(2,7)
# print("R2====", R2)
# R3 = heavymath.mod
# print("R1===", R1)
# print("R2===", R2)
# print("R3===", R3)


