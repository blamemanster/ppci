""" Contains disassembler stuff. """

from ppci.arch.adv32.instructions import adv32Instruction
from ..arch.data_instructions import DByte, DataInstruction
# from ppci.arch.isa import instructions

class Disassembler:
    """ Base disassembler for some architecture """

    def __init__(self, arch):
        self.arch = arch
        # for instruction in arch.isa.instructions:
        #     print(instruction, instruction.patterns)
        #     for nl in instruction.non_leaves:
        #        print('  ', nl.patterns)
        pass

    def disasm(self, data, outs, address=0):
        """ 将数据反汇编到指令流中 """
        # TODO: implement this!

        # 试错的方法，会慢如蜗牛
        # for instruction in self.arch.isa.instructions:
        #    for size in instruction.sizes():
        #        part = data[:size]
        #        try:
        #            print(instruction, part, size)
        #            i = instruction.decode(part)
        #            print(i)
        #        except ValueError:
        #            pass
        # for instruction in self.arch.isa.instructions:
        #    for size in instruction.sizes():
        #        part = data[:size]
        #        try:
        #            print(instruction, part, size)
        #print("\"code\"段的反汇编如下:" )
        while len(data) != 0 :
            for instruction in self.arch.isa.instructions:
                if instruction != adv32Instruction and instruction != DataInstruction:
                    # for size in instruction.sizes():
                    size = instruction.sizes()[0]
                    part = data[:size]
                    try:
                        # print("data==", part)
                        i = instruction.decode(part)
                        # outs.emit(i)
                        # print(  hex(address),  i)
                        a = str(i)
                        b = " "
                        print(i)
                        # print( f"{hex(address):>5}", f"{b:<10}{a:<100}")
                        address += size * 8
                        #TODO：data移位操作，data = data[size:]
                        data = data[size:]
                        break
                        # TODO：判断data为空后，跳出循环
                    except ValueError:
                        continue
                else:
                    continue


        # for instruction in self.arch.isa.instructions:
        # size = 32
        # part = data[:size]
        # try:
        #     print(instruction, part, size)
        #     i = instruction.decode(part)
        #     print(i)
        # except ValueError:
        #     pass

        # For now, all is bytes!

        for byte in data:
            ins = DByte(byte)
            ins.address = address
            outs.emit(ins)
            address += len(ins.encode())


    def take_one(self):
        pass
