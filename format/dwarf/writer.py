# from .line import AdvanceLin


from ppci.format.dwarf.line import LineNumberProgram


def emit_dwarf(debug_info, obj):
    """ 将调试信息以dwarf格式存储到给定的目标文件中 """
    line_number_program = LineNumberProgram()
    data = line_number_program.encode()
    obj.add_section("debug_line", data)


class DwarfWriter:
    pass
