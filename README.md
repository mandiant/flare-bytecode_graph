# bytecode_graph

Module designed to modify Python bytecode. 
Allows instructions to be added or removed from a Python bytecode string. The modified bytecode can be refactored to correct offsets and produce a new functional code object. 

You should use the same Python interpretor version as the bytecode being analyzed.

## Example - Inserting NOP instructions

The following example inserts a NOP instruction after each instruction in the `Sample` function:

```python

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
```

Disassembly of `Sample()`:
```
          0 640500  LOAD_CONST          5 (4)
          3 7d0000  STORE_FAST          0 (i)
          6 7c0000  LOAD_FAST           0 (i)
          9 640200  LOAD_CONST          2 (4)
         12 6b0200  COMPARE_OP          2 (==)
         15 721e00  POP_JUMP_IF_FALSE    30
         18 640300  LOAD_CONST          3 ('2 + 2 = %d')
         21 7c0000  LOAD_FAST           0 (i)
         24 16      BINARY_MODULO  
         25 47      PRINT_ITEM     
         26 48      PRINT_NEWLINE  
         27 6e0500  JUMP_FORWARD        5 (to 35)
    >>   30 640400  LOAD_CONST          4 ('oops')
         33 47      PRINT_ITEM     
         34 48      PRINT_NEWLINE  
    >>   35 640000  LOAD_CONST          0 (None)
         38 53      RETURN_VALUE   
```

Disassembly of `Sample()` with NOPs:
```
          0 640500  LOAD_CONST          5 (4)
          3 09      NOP            
          4 7d0000  STORE_FAST          0 (i)
          7 09      NOP            
          8 7c0000  LOAD_FAST           0 (i)
         11 09      NOP            
         12 640200  LOAD_CONST          2 (4)
         15 09      NOP            
         16 6b0200  COMPARE_OP          2 (==)
         19 09      NOP            
         20 722a00  POP_JUMP_IF_FALSE    42
         23 09      NOP            
         24 640300  LOAD_CONST          3 ('2 + 2 = %d')
         27 09      NOP            
         28 7c0000  LOAD_FAST           0 (i)
         31 09      NOP            
         32 16      BINARY_MODULO  
         33 09      NOP            
         34 47      PRINT_ITEM     
         35 09      NOP            
         36 48      PRINT_NEWLINE  
         37 09      NOP            
         38 6e0900  JUMP_FORWARD        9 (to 50)
         41 09      NOP            
    >>   42 640400  LOAD_CONST          4 ('oops')
         45 09      NOP            
         46 47      PRINT_ITEM     
         47 09      NOP            
         48 48      PRINT_NEWLINE  
         49 09      NOP            
    >>   50 640000  LOAD_CONST          0 (None)
         53 09      NOP            
         54 53      RETURN_VALUE   
         55 09      NOP    
```

Output of running modified code object:
```
2 + 2 = 4
```

To remove the NOPs append the following to the above example:
```python
nodes = [x for x in bcg.nodes()]
for n in nodes:
    #verify opcode is NOP
    if n.opcode == opmap['NOP']:
        #remove instruction node from the graph
        bcg.delete_node(n)
        
#create a new code object
new_code = bcg.get_code()
bytecode_graph.disassemble(new_code)
exec new_code
```

To load code from a PYC file:
```python
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
```

It is also possible to create control flow diagrams using GraphViz. The disassembly within the graph can include the output from a simple peephole decompiler. This can be helpful when reviewing bytecode that fails to decompile.

```python
import bytecode_graph


def Sample():
    i = 2 + 2
    if i == 4:
        print "2 + 2 = %d" % i
    else:
        print "oops"

bcg = bytecode_graph.BytecodeGraph(Sample.__code__)

graph = bytecode_graph.Render(bcg, Sample.__code__).dot()

graph.write_png('example_graph.png')

```

![Example_Graph](docs/example_graph.png?raw=true)
