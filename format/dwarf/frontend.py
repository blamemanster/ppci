from venv import logger
from . import nodes
from .lexer import DwLexer
from .parser import DwParser
from .convertor import DwConvertor
from .codegenerator import DwGenerator
from .function import extract_metadata

def llvmdbg_to_dwarf(source):
    llvmdbg = DwFrontend()
    allnode = llvmdbg.compile(source)
    logger.info("Dw节点获取完成")
    return allnode

class DwFrontend:
    def __init__(self):
        context = nodes.Context()
        self.lexer = DwLexer(context)
        self.parser = DwParser(context)
        self.conver = DwConvertor()
        self.codegen = DwGenerator()

    def compile(self, f):
        with open(f.name, 'r', encoding='utf-8') as file:
            src = file.read() 
            # src = f.read() 
            src = extract_metadata(src)
        if f.name:
            self.lexer.filename = f.name
        tokens = self.lexer.tokenize(src, eof=True) 
        self.parser.init_lexer(tokens) 
        #这里
        dw_module = self.parser.parse_module() 
        allnode = self.conver.convert(dw_module)
        return self.codegen.generate(allnode) 