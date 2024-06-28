from .tokens import isa
from ..generic_instructions import ArtificialInstruction, Alignment
from ..encoding import Instruction, Operand, Syntax, Constructor

class Pseudo_ADV32Instruction(ArtificialInstruction):
    isa = isa

"""定义伪指令+宏伪指令"""
class Align(Pseudo_ADV32Instruction):
    imm = Operand("imm", int)
    syntax = Syntax([".", "align", " ", imm])
    def render(self):
        self.rep = self.syntax.render(self)
        yield Alignment(self.imm, self.rep)

def render(self, obj):
    """ Return this syntax formatted for the given object. """
    return "".join(self._get_repr(e, obj) for e in self.syntax)

@staticmethod
def _get_repr(syntax_element, obj):
    """ Get the repr of a syntax part. Can be str or prop class,
    in refering to an element in the args list """
    if isinstance(syntax_element, str):
        return syntax_element
    elif isinstance(syntax_element, Operand):
        return str(syntax_element.__get__(obj))
    else:  # pragma: no cover
        raise NotImplementedError(str(syntax_element))
