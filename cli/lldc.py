"""llvm 调试信息 compiler"""

import argparse
import string
from .base import base_parser, march_parser, LogSetup
from .base import get_arch_from_args
from .compile_base import compile_parser, do_compile
from .. import api
from ..binutils.objectfile import Section

parser = argparse.ArgumentParser(
    description=__doc__, parents=[base_parser, march_parser, compile_parser]
)
parser.add_argument("source", help="source file", type=argparse.FileType("r"))


def lldc(args=None):
    """ Compile llvm ir code into machine code """
    args = parser.parse_args(args)
    with LogSetup(args) as log_setup:
        march = get_arch_from_args(args)
        # 获取 dwarf 段
        sections = api.frontend.llvmdbg_to_dwarf(args.source)
        print(sections)
        print("!!!!!!success")
        # 汇编
        obj = api.asm(args.source, march, debug=args.g)

        for section in sections:
            if section['name'].startswith('.debug_'):
                s = Section(section['name'])
                s.add_data(bytes.fromhex(section['data']))
                obj.add_section(s)
        # Write object file to disk:
        with open(args.output, "w") as output:
            obj.save(output)       

if __name__ == "__main__":
    lldc()
