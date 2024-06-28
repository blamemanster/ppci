import logging
from . import nodes
from ... import ir, irutils

class DwConvertor:

    logger = logging.getLogger("dwarf-con")
    def __init__(self):
        self.allnode = []

    def convert(self, dw_module):
        self.dw_module = dw_module
        self.logger.debug("生成dwarf节点")
        for item in dw_module.items.values():
            dw_node = self.con_sec(item)
            self.allnode.append(dw_node)
        return self.allnode

    def con_sec(self, item):
        if item.at_name == '!DICompileUnit': #数据转换
            return self.convert_CompileUnit(item)
        elif item.at_name == '!DISubprogram':
            return self.convert_Subprogram(item)
        elif item.at_name == '!DILocalVariable':
            return self.convert_LocalVariable(item)
        elif item.at_name == '!DIBasicType':
            return self.convert_BasicType(item)



    





    def convert_CompileUnit(self, item):
        kv = item.kv
        filename = self.dw_module.items[kv['file']].get_value('filename')
        directory = self.dw_module.items[kv['file']].get_value('directory')
        return nodes.DW_TAG_compile_unit(item.num, filename, kv.get('producer', None), directory, kv.get('language', None))
    
    def convert_Subprogram(self, item):
        kv = item.kv
        SubroutineType = self.dw_module.items[kv['type']].get_value('types') #!10
        type_table1 = self.dw_module.items[SubroutineType].kv[0] #类型列表第一个元素
        type = self.dw_module.items[type_table1].num # 基本类型 !12
        return nodes.DW_TAG_subprogram(item.num, kv.get('name', None), type)

    def convert_LocalVariable(self, item):
        kv = item.kv
        if "arg" in kv.keys():
            return nodes.DW_TAG_formal_parameter(item.num, kv.get('name', None), kv.get('type', None))
        else:
            return nodes.DW_TAG_variable(item.num, kv.get('name', None), kv.get('type', None))

    def convert_BasicType(self, item):
        kv = item.kv
        return nodes.DW_TAG_base_type(item.num, kv.get('name', None), kv.get('encoding', None), kv.get('size', None))


    
