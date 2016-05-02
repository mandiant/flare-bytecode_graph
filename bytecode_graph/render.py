from dis import opmap

import pydot

from utils import *

CONST = 2
TRUE = 1
FALSE = 0


class Render:
    def __init__(self, bcg, code_object, colors=None):
        self.bcg = bcg
        self.co = code_object

        if colors is None:
            self.colors = {CONST: "blue", TRUE: "green", FALSE: "red"}
        else:
            self.colors = colors

        return

    def get_blocks(self):
        blocks = []
        prev = None

        targets = []

        for x in self.bcg.nodes():
            if x.target is None:
                continue

            targets.append(x.target.addr)

        for x in self.bcg.nodes():
            if prev is None:
                prev = x

            if x.next is not None and x.next.addr in targets:
                blocks.append((prev, x))
                prev = None
                continue
            if x.target is None:
                continue

            blocks.append((prev, x))
            prev = None

        blocks.append((prev, x))
        return blocks

    def get_edges(self, blocks):
        edges = []
        for start, x in blocks:

            if x.opcode in true_branches:
                edges.append((start, x.target, TRUE))
                edges.append((start, x.next, FALSE))

            elif x.opcode in false_branches:
                edges.append((start, x.target, FALSE))
                edges.append((start, x.next, TRUE))

            elif x.opcode in const_branches:
                edges.append((start, x.target, CONST))

            elif x.opcode in loop_branches:
                edges.append((start, x.target, CONST))
                edges.append((start, x.next, CONST))
            else:
                if x.next is not None:
                    edges.append((start, x.next, CONST))

        return edges

    def get_comments(self, start, stop):

        rvalue = []
        current = stop
        while True:

            prev, dec_str = decompile(self.co, current)
            if(dec_str is not None) and (prev != current.prev):
                rvalue.append((current.addr, dec_str, current.co_lnotab))

            if prev is not None:
                current = prev
            else:
                current = current.prev

            if current is None:
                break

            if current == start or current.addr <= start.addr:
                break

        return rvalue

    def dot(self, splines="ortho", show_comments=True, show_hex=False):

        graph = pydot.Dot(graph_type='digraph', splines=splines, rankdir="TD")
        
        graph.set_node_defaults(shape="box",
                                fontname="Courier New",
                                fontsize = "9")
        
        blocks = self.get_blocks()
        edges = self.get_edges(blocks)

        for start, stop in blocks:
            lbl = disassemble(self.co, start=start.addr, stop=stop.addr+1,
                              show_labels=False, show_hex=show_hex)

            if show_comments:
                comments = self.get_comments(start, stop)

                for addr, comment, lineno in comments:
                    m = re.search("^[ ]*%d .*$" % addr, lbl, re.MULTILINE)
                    if m is None:
                        continue

                    lbl = lbl[:m.end(0)] + "\n\n# %d " % lineno +\
                        comment + "\n" + lbl[m.end(0):]
                        
            # left alignment
            lbl = lbl.replace("\n", "\\l")
            lbl += "\\l"
            
            tmp = pydot.Node("%08x" % start.addr, label=lbl)
            graph.add_node(tmp)

        for edge in edges:
            tmp = pydot.Edge("%08x" % edge[0].addr,
                             "%08x" % edge[1].addr,
                             color=self.colors[edge[2]])
            graph.add_edge(tmp)

        return graph
