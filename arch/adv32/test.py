from ppci.arch.adv32.registers import Xar0
#from ppci.arch.adv32.instructions import ADDb,C7
from ppci.arch.adv32.instructions import ADDBXARnImm7,C7
a1 = ADDBXARnImm7(Xar0,C7(8))
str(a1)
a1.encode()

############################################################
from ppci.arch.adv32.instructions import addb
a1 = addb(2) 
str(a1)
a1.encode()