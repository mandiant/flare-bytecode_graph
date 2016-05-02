import bytecode_graph

def Sample():
    i = 2 + 2
    if i == 4:
        print "2 + 2 = %d" % i
    else:
        print "oops"

bcg = bytecode_graph.BytecodeGraph(Sample.__code__)

graph = bytecode_graph.Render(bcg, Sample.__code__).dot()

path = "C:\\Program Files\\Graphviz2.38\\bin\\"
tmp = {'dot': path+"dot.exe",
       'twopi': path+"twopi.exe",
       'neato': path+"neato.exe",
       'circo': path+"circo.exe",
       'fdp': path+"fdp.exe"}
graph.set_graphviz_executables(tmp)

graph.write_png('example1_graph.png')

print graph.to_string()
