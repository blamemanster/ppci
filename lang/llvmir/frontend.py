from venv import logger
from . import nodes
from .lexer import LlvmIrLexer
from .parser import LlvmIrParser
from .codegenerator import CodeGenerator


def llvm_to_ir(source):
    """ Convert llvm assembly code into an IR-module """
    llvm = LlvmIrFrontend()
    ir_module = llvm.compile(source)
    logger.info("IR转换完成")
    return ir_module


class LlvmIrFrontend:
    def __init__(self):
        context = nodes.Context()
        self.lexer = LlvmIrLexer(context)
        self.parser = LlvmIrParser(context)
        self.codegen = CodeGenerator()

    def compile(self, f):
        with open(f.name, 'r', encoding='utf-8') as file:
            src = file.read() 
            # src = f.read() 
        if f.name:
            self.lexer.filename = f.name
        tokens = self.lexer.tokenize(src, eof=True) 
        self.parser.init_lexer(tokens) 
        #这里
        module = self.parser.parse_module() 
        return self.codegen.generate(module) 
