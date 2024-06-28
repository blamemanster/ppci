# import io
# from ppci.lang.python import jit
# from ppci.api import cc

# source_file = io.StringIO("int main() { int a=8; a = a+10; return a;}")

# obj = cc(source_file, 'x86_64')

# print(obj)
from ppci.lang.python import jit



@jit
def heavymath(a: int, b: int) -> int:
    return a + b



# heavymath函数可被调用
R1 = heavymath.original
R2 = heavymath.compiled(2,7)
R3 = heavymath.mod
print("R1===", R1)
print("R2===", R2)
print("R3===", R3)

