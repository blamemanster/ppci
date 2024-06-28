""" 这个模块帮助读写asm到二进制。
"""


LANG_TYPES = {
    "i32": b"\x7f",
    "i64": b"\x7e",
    "f32": b"\x7d",
    "f64": b"\x7c",
    "funcref": b"\x70",
    "func": b"\x60",
    "emptyblock": b"\x40",  # pseudo type for representing an empty block_type
}
LANG_TYPES_REVERSE = {v[0]: k for k, v in LANG_TYPES.items()}
