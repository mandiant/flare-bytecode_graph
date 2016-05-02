import bytecode_graph
from dis import opmap
import sys
import marshal


pyc_file = open(sys.argv[1], "rb").read()
pyc = marshal.loads(pyc_file[8:])

bytecode_graph.disassemble(pyc)
print

bcg = bytecode_graph.BytecodeGraph(pyc)

nodes = [x for x in bcg.nodes()]
for n in nodes:
    bc = bytecode_graph.Bytecode(0, chr(opmap['NOP']))
    bcg.add_node(n, bc)

new_code = bcg.get_code()
bytecode_graph.disassemble(new_code)
print

nodes = [x for x in bcg.nodes()]
for n in nodes:
    if n.opcode == opmap['NOP']:
        bcg.delete_node(n)

new_code = bcg.get_code()
bytecode_graph.disassemble(new_code)
print
