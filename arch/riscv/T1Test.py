import ppci.cli.link as link
import ppci.cli.cc as cc
import ppci.cli.asm as asm
# arg = ["-S","hello.c", "--machine=c240x", "-o" ,"fc.o"]
# cc.cc(arg)

# arg = ["-c","hello2.c", "--machine=c240x", "-o" ,"fc2.o"]
# cc.cc(arg)

# args=["fc.o","fc2.o","-o" ,"fccTestqwe.out"]
# link.link(args)

arg=["f.out","-o" ,"riscv_PE.out"]
asm.asm(arg)

print("aaa")

# from ctypes import *

# pDLL = windll.LoadLibrary("F:/TianyiLi_WorkSpace/VSWorkSpace/COFFI-master/T1TestDLL/DllT1/x64/Debug/DllT1.dll")
# """*******************************************"""
# pDLL.test.restype = c_int
# pDLL.test2.restype = c_int

# """*******************************************"""
# pDLL.test.argtypes = [c_int]
# pDLL.test2.argtypes = [c_int]
# """*******************************************"""
# res = pDLL.test(3)
# res2 = pDLL.test2(1)
# print("aaa"+str(res))
# print("aaa"+str(res2))

