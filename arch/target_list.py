""" Contains a list of instantiated targets. """

from functools import lru_cache
from ppci.arch.c240x.arch import c240xArch
from .arm import ArmArch
from .avr import AvrArch
from .example import ExampleArch
from .msp430 import Msp430Arch
from .x86_64 import AMD64Arch
from .m68k import M68kArch
from .mcs6500 import Mcs6500Arch
from .mips import MipsArch
from .microblaze import MicroBlazeArch
from .or1k import Or1kArch
from .riscv import RiscvArch
from .stm8 import Stm8Arch
from .xtensa import XtensaArch
from .c240x import c240xArch
from .adv32 import adv32Arch
target_classes = [
    ArmArch,
    AvrArch,
    ExampleArch,
    M68kArch,
    Mcs6500Arch,
    MicroBlazeArch,
    MipsArch,
    Msp430Arch,
    Or1kArch,
    RiscvArch,
    Stm8Arch,
    AMD64Arch,
    XtensaArch,
    c240xArch,
    adv32Arch,
]


target_class_map = {t.name: t for t in target_classes}
target_names = tuple(sorted(target_class_map.keys()))


@lru_cache(maxsize=30)
def create_arch(name, options=None):
    """ Get a target architecture by its name. Possibly arch options can be
        given.
    """
    # Create the instance!
    target = target_class_map[name](options=options)
    return target
