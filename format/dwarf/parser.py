from collections import namedtuple
import logging
from ...lang.llvmir.parser import LlvmIrParser
from ...lang.tools import baselex #自己添加
from . import nodes
class DwParser(LlvmIrParser):
    def __init__(self, context):
        super().__init__(context)

    def parse_module(self):
        """解析llvm-ir调试信息模块"""
        self.logger.debug("Parsing llvm-ir debug module")
        self.module = nodes.Module(self.context)

        while not self.at_end:
            if self.peek == "!":
                item = self.parse_standalone_metadata()
                self.module.items.update({item.num:item})
            else:
                self.consume()
        return self.module

    def parse_standalone_metadata(self):
        """ Parse meta data starting with '!' 'num' """
        self.consume("!")
        num = '!' + str(self.parse_number())
        if self.peek == "=":
            self.consume("=")
        else:
            self.consume()
            return
        if self.peek == "distinct":
            self.consume("distinct")
        if self.peek == "!":
            self.consume("!")
            at_name = '!'
        if self.peek == "MDVAR":
            at_name = self.consume("MDVAR").val
        kv = self.parse_md_node_vector()
        return nodes.Attribute(num, at_name, kv)

    def parse_md_node_vector(self):
        if self.peek == "{":
            self.consume("{")
            elements = []
            while self.peek != "}":
                # self.consume()
                # TODO: parse meta data!
                metadata = self.parse_metadata()
                elements.append(metadata)
                if self.peek != "}":
                    self.consume(',')
            self.consume("}")
        else : #自己添加解析调试信息
            self.consume("(")
            elements={}
            while self.peek != ")":
                # self.consume()
                # TODO: parse meta data!
                metadata = self.parse_metadata1() # 仿
                elements.update(metadata)
                if self.peek != ")":
                    self.consume(',')
            self.consume(")")
        print(elements)
        return elements

    def parse_metadata(self):
        """ Parse meta data

        i32 1
        !42
        !{...}
        !"string"
        
        """
        if self.peek == "!":
            self.consume("!")
            metadata = '!'
            if self.peek == "{":
                # 添加 Parse metadata node
                metadata = metadata + self.parse_md_node_vector()
            elif self.peek == "STR":
                # 添加 Parse string metadata
                metadata = metadata + "\"" + self.parse_string_constant() + "\""
            elif self.peek == "NUMBER":
                # 添加 Parse number metadata
                metadata = metadata + str(self.parse_number())
        elif self.peek == "type":
            self.consume("type")
                # 添加 Parse number metadata
            metadata = self.parse_number()
        else :
            metadata = self.peek
            self.consume()

        return metadata

    def parse_metadata1(self): #自己仿造
            """ Parse meta data

            name : "lock"
            scope : !2
            line : 45
            !DIExpression()

            """
            tem1 = self.consume("LBL").val
            tem1 = tem1[:-1] # 除去 :
            tem2 = None
            if self.peek == "!":
                self.consume("!")
                tem2 ='!'
            if self.peek == "NUMBER":
                if tem2 == '!':
                    tem2 = tem2 + str(self.parse_number())
                else:
                    tem2 = self.parse_number()
            elif self.peek == "STR":
                tem2 = self.parse_string_constant()
            elif self.peek == "MDVAR":
                tem2 = self.parse_md_node_vector()
            else : #匹配ID类型
                tem2 = self.peek
                self.consume()
            metadata = {tem1 : tem2}

            return metadata