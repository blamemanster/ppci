import re

# from ...common import make_num
from ...lang.llvmir.lexer import LlvmIrLexer
from . import nodes

class DwLexer(LlvmIrLexer):
    def __init__(self, context):
        super().__init__(context)