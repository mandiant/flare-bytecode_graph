import bytecode_graph
from dis import opmap


def Sample():
    i = 2 + 2
    if i == 4:
        print "2 + 2 = %d" % i
    else:
        print "oops"

print bytecode_graph.disassemble(Sample.__code__)
print
bcg = bytecode_graph.BytecodeGraph(Sample.__code__)

nodes = [x for x in bcg.nodes()]
for n in nodes:
    bc = bytecode_graph.Bytecode(0, chr(opmap['NOP']))
    bcg.add_node(n, bc)

new_code = bcg.get_code()
print bytecode_graph.disassemble(new_code)
print
exec new_code

nodes = [x for x in bcg.nodes()]
for n in nodes:
    if n.opcode == opmap['NOP']:
        bcg.delete_node(n)
new_code = bcg.get_code()
print bytecode_graph.disassemble(new_code)
exec new_code
