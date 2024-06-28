import logging
from . import nodes
from ... import ir, irutils


class CodeGenerator:
    """ 
    将llvm-ir转换为ppci-ir
    这个类的简单工作是将llvm-IR转换为ppci-IR。
    LLVM变量的前缀是ll_
    """

    logger = logging.getLogger("llvm-gen")

    def __init__(self):
        self.builder = irutils.Builder()
        self.val_map = {}
        self.forward = {}
        # 创建默认块
        self.default_num = None
        # 创建label与块序号的字典
        self.label_to_block_number = {}
        self.block_list = []
        self.lldbg = {}  # 创建lldbg字典


    def generate(self, ll_module):
        """ 将LLVM ir模块转换为ppci ir模块 """
        assert isinstance(ll_module, nodes.Module)
        self.logger.debug("从LLVM ir-code生成ir-code")
        self.builder.module = ir.Module("ADVDSP")
        self.builder.module.lldbg = ll_module.lldbg # 添加传递位于底部的全部调试信息
        self.ll_module = ll_module
        for function in ll_module.functions:
            self.gen_function(function)
        self.ll_module = None
        return self.builder.module

    def gen_function(self, function):
        """ 生成llvm 【函数】 的代码 """
        self.logger.debug("generating ir-code for %s", function)
        name = function.name #
        binding = function         #自己添加
        # 下面是获取last instruction returns的类型
        return_ty = self.get_ir_type(function.ty.result_type)
        # ir_function = self.builder.new_procedure(name, binding) #原始代码
        ir_function = self.builder.new_function(name, binding, return_ty, function.lldbg)    #将new_procedure修改为new_function  //添加function.lldbg参数
        self.builder.set_function(ir_function)
        self.val_map[function] = ir_function #自己添加函数node到ir的映射,call指令需要这个

        for ll_arg in function.arguments:
            arg_name = ll_arg.name
            arg_ty = self.get_ir_type(ll_arg.ty)
            pp_arg = ir.Parameter(arg_name, arg_ty)
            self.val_map[ll_arg] = pp_arg
            ir_function.add_parameter(pp_arg)


        for basic_block in function.basic_blocks: 
            # 判断block是否需要创建
            if self.block_list:
                block = self.block_list.pop(0)
            else:
                block = self.builder.new_block()
            self.builder.set_block(block) 
            for instruction in basic_block.instructions:   # 遍历块来转换指令
                self.gen_instruction(instruction)
        if len(ir_function.blocks) != 0: #添加判断，避免空值报错
            ir_function.entry = ir_function.blocks[0]
    def gen_instruction(self, instruction):
        """ 将llvm指令转换为正确的ppci部分 """
        if isinstance(instruction, nodes.BinaryOperator): 
            #print("lhs==", instruction.lhs)
            #print("rhs==", instruction.rhs)
            lhs = self.get_val(instruction.lhs) # a 
            #print("lhs==", lhs)
            ty = self.get_ir_type(instruction.ty) # ir-typ i32
            op_map = {"mul": "*", "add": "+", "sub":"-", "fdiv":"/", "sdiv":"/","srem":"%", "frem":"%", "or":"|", 
                    "and":"&", "xor":"^", "shl":"<<", "lshr":">>", "ashr":">>", "rol":"rol", "ror":"ror"
                    }   #需添加其他的操作类型
            op = op_map[instruction.op] 
            ## 如果右操作数是立即数类型,则将其转换成Const类型,不能直接调用get_value方法
            if isinstance( instruction.rhs , nodes.ConstantInt):
                rhs_value = instruction.rhs.value
                rhs_name = "{}".format(rhs_value)
                rhs_ty = self.get_ir_type(instruction.rhs.ty)
                rhs = ir.Const(rhs_value, rhs_name, rhs_ty)
                ir_val1 = self.emit(rhs) 
            else:
                rhs = self.get_val(instruction.rhs)
            #print("rhs", ir.IntegerTyp("int", 32))
            #rhs = self.get_val(instruction.rhs)  # 原始代码
            # name = "binop" 

            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            ir_val = self.emit(ir.Binop(lhs, op, rhs, "binop", ty, temp_lldbg)) #添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg
            self.val_map[instruction] = ir_val 
        elif isinstance(instruction, nodes.AllocaInst):
            amount = self.ll_module.data_layout.get_type_alloc_size(instruction.allocated_ty )
            name = instruction.name

            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合

            if amount == 1:
                alignment = 2
            else: alignment = amount

            ir_ins = self.emit(ir.Alloc(name, amount, alignment, temp_lldbg)) #加了一个 4  //添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg
            self.val_map[instruction] = ir_ins 
        elif isinstance(instruction, nodes.GetElementPtrInst): 
            # Implement arithmatic here!
            ir_ins = self.get_val(instruction.ptr)
            # print(instruction.indices)
            # raise NotImplementedError(str(instruction))
            # TODO
            self.val_map[instruction] = ir_ins
        elif isinstance(instruction, nodes.LoadInst):
            ty = self.get_ir_type(instruction.ptr.ty.el_type) 
            ptr = self.get_val(instruction.ptr)          #ptr=ppci.ir.Alloc类型

            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            ir_ins = self.emit(ir.Load(ptr, "load", ty, False, temp_lldbg)) # ptr有问题 //添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg
            self.val_map[instruction] = ir_ins
            return ir_ins #自己添加，CallInst要用到
        elif isinstance(instruction, nodes.StoreInst):
            # val = self.get_val(instruction.val) 
            # 更换了val的计算方式,ptr 未改动
            # print("instruction.val.ty==  ", instruction.val.ty)
            # print("instruction.val==  ", instruction.val)
            # print("nodes.ConstantInt==  ", nodes.ConstantInt)
            ty1 = self.get_ir_type(instruction.val.ty)
            # print("ty1=== ", ty1)
            # 如何区分val的类型
            if isinstance (instruction.val, nodes.ConstantInt ):
                val_value = instruction.val.value 
                val_name = "{}".format(val_value) 
                val_ty = self.get_ir_type(instruction.val.ty) 
                val = ir.Const(val_value, val_name, val_ty )
                ir_val1 = self.emit(val) 
            else:
                val = self.get_val(instruction.val)
            ptr = self.get_val(instruction.ptr) 

            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            self.emit(ir.Store(val, ptr, temp_lldbg)) # 添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg
        elif isinstance(instruction, nodes.InsertElementInst):
            pp_ptr = self.get_val(instruction.address)
            pp_val = self.get_val(instruction.value)
            # TODO: type check?
            # pp_ty = self.get_type(instruction.ty.el_type)
            # assert

            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            self.emit(ir.Store(pp_ptr, pp_val, temp_lldbg)) # 添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg
            self.val_map[instruction] = pp_val
        elif isinstance(instruction, nodes.ExtractElementInst):
            pp_ptr = self.get_val(instruction.val)
            pp_ty = self.get_type(instruction.ty)
            # TODO: offset?
            # TODO: what if loaded type is not a basetype?
            # pp_ptr = self.emit(ir.add())
            
            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            pp_val = self.emit(ir.Load(pp_ptr, "load", pp_ty, False, temp_lldbg)) # 添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg
            self.val_map[instruction] = pp_val
        elif isinstance(instruction, nodes.ShuffleVectorInst):
            raise NotImplementedError()
        elif isinstance(instruction, nodes.SelectInst):
            raise NotImplementedError()
        elif isinstance(instruction, nodes.PhiNode):
            # 还没弄完
            phi = ir.Phi()
            for incoming in instruction:
                value = self.get_val()
                block = 1
                phi.set_incoming(block, value)
            self.emit(phi) 
        elif isinstance(instruction, nodes.ICmpInst):
            # 比较操作只进行比较，块的跳转判断放在br指令中进行
            self.a = self.get_val(instruction.lhs) # a=%5
            # 判断b是否为立即数
            if isinstance (instruction.rhs, nodes.ConstantInt ):
                b_value = instruction.rhs.value
                b_name = "{}".format(b_value) 
                b_ty = self.get_ir_type(instruction.rhs.ty) 
                self.b = ir.Const(b_value, b_name, b_ty ) # b=10
            else: 
                self.b = self.get_val(instruction.rhs)
            # 首先需获取比较操作类型编号pred
            pred = instruction.pred
            self.icmp_type = self.get_icmp_type(pred) #然后根据数字pred判断是什么类型的操作
            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
        elif isinstance(instruction, nodes.BranchInst):
            # 这里只生成指令，将指令放入对应的块是在上面的for instruction in basic_block.instructions循环中进行
                # 条件跳转
            if isinstance(instruction.op2, nodes.BasicBlock):
                # 创建下一个块，并添加到block_list
                block0 = self.builder.new_block()
                self.block_list.append(block0)
                # 创建下下一个块，并添加到block_list
                block1 = self.builder.new_block()
                self.block_list.append(block1)
                # 获取比较的左操作数
                left_val =  self.a 
                # 获取比较的右操作数
                right_val = self.b
                # 如果是常量，则emit
                if isinstance (right_val, ir.Const ):
                    self.emit(right_val)
                # 获取比较类型
                type = self.icmp_type

                self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
                temp_lldbg = self.lldbg.copy() # 创建临时集合
                self.emit(ir.CJump(left_val, type, right_val, block0, block1, temp_lldbg)) #添加temp_lldbg
                self.lldbg.clear() #清空生成好的lldbg
            else:
                # 无条件跳转
                # 首先判断之前是否有cases语句
                if self.default_num :
                    # 针对cases进行额外判断
                    # 首先获取当前label的序号，判断是否与默认块的序号相等
                    current_num = instruction.op1.label
                    # 获取默认块的序号
                    default_num = self.default_num
                    if current_num == default_num:
                        # 相等则说明该cases语句中有break语句,直接跳出到默认块
                        block_number = self.block1
                    else :
                        # name = "{}_block{}".format(self.builder.function.name, self.builder.block_number)
                        # block_number = ir.Block(name)
                        block_number = self.builder.new_block()
                        self.block_list.append(block_number)
                else: 
                    # 使用一个字典来维护标签和基本块序号之间的映射关系，这里只考虑了直接跳转的情况。后续可改。
                    # 判断当前label是否是第一次出现（即未绑定块号），如果是则绑定下一个块号（else中）
                    # 如果不是，则说明是循环操作，需引用之前label绑定的块号，来跳到之前的前一个基本块
                    if instruction.op1.label in self.label_to_block_number:
                        block_number = self.label_to_block_number[instruction.op1.label]
                    else:
                        block_number = self.builder.new_block()
                        self.block_list.append(block_number)
                        self.label_to_block_number[instruction.op1.label] = block_number

                self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
                temp_lldbg = self.lldbg.copy() # 创建临时集合
                ir_ins = self.emit(ir.Jump(block_number, temp_lldbg)) #添加temp_lldbg
                self.lldbg.clear() #清空生成好的lldbg                
                self.val_map[instruction] = ir_ins 
        elif isinstance(instruction, nodes.SwitchInst):
            # 获取默认块label的序号，便于后续调用
            self.default_num = instruction.default_block.label
            # 获取这条指令的cases的个数，来决定默认快的序号
            # 创建序号个数的基本块
            len_cases = len(instruction.cases)
            for _ in range(len_cases+1):
                self.block1 = self.builder.new_block()
                self.block_list.append(self.block1)

            # 获取输入的变量
            compare_val = instruction.op0
            # i是用来做基本块的序号自增
            i = 0
            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            self.emit(self.generate_nested_cjmp( i ,compare_val, instruction.cases, self.block1, temp_lldbg)) #添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg 
        elif isinstance(instruction, nodes.ReturnInst):
            # 这个返回是无效的吗???

            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            if instruction.ty.is_void:
                self.emit(ir.Exit(temp_lldbg)) #添加temp_lldbg))
            else:
                pp_val = self.get_val(instruction.value)
                self.emit(ir.Return(pp_val, temp_lldbg)) #添加temp_lldbg
            self.lldbg.clear() #清空生成好的lldbg 
        elif isinstance(instruction, nodes.CallInst):
            # Is it a void call?
            #——————————————临时添——————————
            if instruction.fname[:3] == "asm":
                template = instruction.fname[3:]
                inline_asm = ir.InlineAsm(template, None)
                self.emit(inline_asm)
                return
            #————————————————————————————————
            ir_arguments = []
            instruction.fname = instruction.fname.replace("@", "")
            #---------------------- 添加参数列表 --------------------#
            for cl_arg in instruction.arguments:
                ## 如果参数是立即数类型,则将其转换成Const类型
                if isinstance( cl_arg , nodes.ConstantInt):
                    arg_value = cl_arg.value
                    arg_name = str(cl_arg.name if hasattr(cl_arg, 'name') else cl_arg.value )
                    arg_ty = self.get_ir_type(cl_arg.ty)
                    value = self.emit(ir.Const(arg_value, arg_name, arg_ty))
                    ir_arguments.append(value)
                    call_arg = ir.Parameter(arg_name, arg_ty)
                    self.val_map[cl_arg] = call_arg
                ##自己添加
                elif isinstance( cl_arg , nodes.MetadataInt) or isinstance(cl_arg, nodes.AllocaInst):
                    arg_name = str(cl_arg.name if hasattr(cl_arg, 'name') else cl_arg.value )
                    arg_ty = self.get_ir_type(cl_arg.ty)
                    value = ir.Metadata(arg_name, arg_ty)
                    ir_arguments.append(value)
                    call_arg = ir.Parameter(arg_name, arg_ty)
                    self.val_map[cl_arg] = call_arg
    
                else:
                    value = self.gen_instruction(cl_arg)
                    ir_arguments.append(value)
                    # arg_name = str(cl_arg.name if hasattr(cl_arg, 'name') else cl_arg.value )
                    # arg_ty = self.get_ir_type(cl_arg.ty)
                # call_arg = ir.Parameter(arg_name, arg_ty)
                # self.val_map[cl_arg] = call_arg
                # arguments.append(call_arg)
                # callee.add_parameter(call_arg)
            #-------------------------------------------------------#

            ret_name = instruction.name if hasattr(instruction, 'name') else ""#获取函数返回值名字
            cl_name = instruction.fname #获取call函数名字
            cl_ty = self.get_ir_type(instruction.ty)  #添加call函数类型
            for i in self.val_map.values(): #
                if i.name == instruction.fname: #简单判断条件
                    callee = i   #找到call的原函数的ir
                    break
            callee.binding = "global" #自己添加
            
            self.lldbg.update(instruction.lldbg) #添加lldbg到集合中
            temp_lldbg = self.lldbg.copy() # 创建临时集合
            if instruction.ty.is_void:
                                           # 参数fname改成callee
                ir_ins = self.emit(ir.ProcedureCall(callee, ir_arguments, temp_lldbg)) #添加temp_lldbg
            else:                          # 参数fname改成callee
                ir_ins = self.emit(ir.FunctionCall(callee, ir_arguments, ret_name, cl_ty, temp_lldbg)) #添加fname, cl_ty, temp_lldbg
                self.val_map[instruction] = ir_ins
            self.lldbg.clear() #清空生成好的lldbg
        else:  # pragma: no cover
            raise NotImplementedError(str(instruction))
    def get_val(self, llvm_val):
        # print("llvm_val===", llvm_val)
        val = self.val_map[llvm_val]
        # print("val===", val)
        return val 

    def get_ir_type(self, ll_ty):
        if ll_ty.type_id == nodes.integer_ty_id:
            mapping = {8: ir.i8, 16: ir.i16, 32: ir.i32, 64: ir.i64}
            return mapping[ll_ty.bits]
        elif ll_ty.type_id == nodes.pointer_ty_id:
            return ir.ptr
        elif ll_ty.type_id == nodes.vector_ty_id:
            return ir.ptr
        elif ll_ty.type_id == nodes.void_ty_id: #自己添加
            return ir.void #自己添加void
        elif ll_ty.type_id == nodes.metadata_ty_id: #自己添加
            return ir.metadata #自己添加metadata
        else:
            raise NotImplementedError(str(ll_ty))

    def emit(self, instruction):
        return self.builder.emit(instruction)

    # def get_next_block_name(self, block):
    #     # 获取名称中的数字部分
    #     block_number = int(block.replace("func1_block", ""))
    #     # 序号加一
    #     next_block_number = block_number + 1
    #     # 构造下一个块的名称
    #     next_block_name = "func1_block" + str(next_block_number)
    #     return next_block_name

    def get_icmp_type(self, int):
        mapping = { 32:"==", 33:"!=", 34:">", 35:">=", 36:"<", 37:"<=", 38:">",39:">=", 40:"<", 41:"<="  }
        icmp_type = mapping[int]
        return icmp_type

    # 嵌套生成cases语句
    def generate_nested_cjmp(self, i ,compare_val, cases, default_block, lldbg =""): #添加lldbg
        # 如果没有剩余的 cases，则直接返回默认块
        if not cases:
            return default_block
        else:
            # 获取当前 case
            # 提前获取下一个块的名字
            block0 = self.block_list[i]
            left_val = cases[0][0]
            cases = cases[1:]  # 剔除当前 case
            i += 1
            # 生成当前 case 的比较跳转语句
            a = ir.Switch(compare_val , left_val, block0, self.generate_nested_cjmp(i, compare_val, cases[0:], default_block), lldbg) #添加lldbg
            return a

