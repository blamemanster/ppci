import ctypes
import json
import logging
import time


lib = ctypes.CDLL("d:/File/gimli-master/target/debug/hongjun.dll")
lib.process_json_wrapper.argtypes = [ctypes.c_char_p]

class DwGenerator:
    """向 Rust 生成工具传递数据"""

    logger = logging.getLogger("Dwarf-gen")

    def __init__(self):
        self.result = []

    def generate(self, allnode):
        """编码 Dwarf 模块"""
        self.logger.debug("从 LLVM ir-code 生成 ir-code")
        
        # 将所有对象转换为字典
        allnode_dict = [node.__dict__ for node in allnode if node is not None]
        #[{'DW_AT_name': 'hello.c', 'DW_AT_producer': 'clang version 18.1.2', 'DW_AT_comp_dir': 'D:\\\\ADVDSP-5_15', 'DW_AT_language': 'DW_LANG_C11', 'DW_TAG_compile_unit': 'DW_TAG_compile_unit'}, {'DW_AT_name': 'add', 'DW_AT_type': '!12', 'DW_AT_low_pc': "None", 'DW_AT_high_pc': "None", 'DW_AT_external': "False", 'DW_TAG_subprogram': 'DW_TAG_subprogram'}]
        """------------方案一----------------"""
        # # 打开文件，以写入模式创建一个 JSON 文件
        # with open("dw.json", "w") as file:
        #     # 将字典数据写入 JSON 文件
        #     json.dump(allnode_dict, file, indent=4)
        
        """-------------方案二------------------"""
        print(allnode_dict)
        # 将 Python 字典列表转换为 JSON 字符串
        json_str = json.dumps(allnode_dict)
        # 调用动态库函数，生成当前路径下 hj.json 和 hj.o 文件
        lib.process_json_wrapper(ctypes.c_char_p(json_str.encode('utf-8')))
        self.logger.debug("数据已传递给 Rust 库函数")
        time.sleep(0.1) #休息0.1秒

        # 读取JSON文件
        with open('hj.json') as f:
            sections = json.load(f)
        

        return sections
