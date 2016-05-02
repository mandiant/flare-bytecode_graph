import dis
from dis import opmap, cmp_op
import re

binary_ops = {opmap["BINARY_MODULO"]: "%",
              opmap["BINARY_ADD"]: "+",
              opmap["BINARY_SUBTRACT"]: "-",
              opmap["BINARY_SUBSCR"]: "[]",
              opmap["BINARY_LSHIFT"]: "<<",
              opmap["BINARY_RSHIFT"]: ">>",
              opmap["BINARY_AND"]: "&",
              opmap["BINARY_XOR"]: "^",
              opmap["BINARY_OR"]: "|"}

const_branches = [opmap["JUMP_FORWARD"], opmap["JUMP_ABSOLUTE"]]
loop_branches = [opmap["SETUP_EXCEPT"]]
false_branches = [opmap["POP_JUMP_IF_FALSE"],
                  opmap["JUMP_IF_FALSE_OR_POP"],
                  opmap["FOR_ITER"]]
true_branches = [opmap["POP_JUMP_IF_TRUE"], opmap["JUMP_IF_TRUE_OR_POP"]]

cond_branches = false_branches + true_branches

loads = [opmap["LOAD_CONST"], opmap["LOAD_GLOBAL"], opmap["LOAD_FAST"]]


def disassemble(c, lasti=-1, start=0, stop=None,
                show_labels=True, show_hex=False):
    '''
    Modified disassemble from dis module that includes hex output for opcodes
    '''
    if hasattr(c, 'co_code'):
        code = c.co_code
        varnames = c.co_varnames
        names = c.co_names
        constants = c.co_consts
    else:
        code = c
        varnames = None
        names = None
        constants = None

    labels = dis.findlabels(code)

    rvalue = ""

    if stop is None:
        n = len(code)
    else:
        n = stop

    i = start
    while i < n:
        c = code[i]
        op = ord(c)
        if show_labels:
            if i == lasti:
                rvalue += '-->'
            else:
                rvalue += '   '
            if i in labels:
                rvalue += '>>'
            else:
                rvalue += '  '

        rvalue += repr(i).rjust(4) + " "

        if op < dis.HAVE_ARGUMENT:
            if show_hex:
                rvalue += ('%02x' % op).ljust(7) + " "
            rvalue += dis.opname[op].ljust(15) + " "
        i = i+1
        if op >= dis.HAVE_ARGUMENT:
            if show_hex:
                rvalue += code[i-1:i+2].encode("hex").ljust(7) + " "
            rvalue += dis.opname[op].ljust(15) + " "
            oparg = ord(code[i]) + ord(code[i+1])*256
            i = i+2
            rvalue += repr(oparg).rjust(5) + " "
            if op in dis.hasconst:
                if constants:
                    rvalue += '(' + repr(constants[oparg]) + ')'
                else:
                    rvalue += '(%d)' % oparg
            elif op in dis.hasname:
                if names is not None:
                    rvalue += '(' + names[oparg] + ')'
                else:
                    rvalue += '(%d)' % oparg
            elif op in dis.hasjrel:
                rvalue += '(to ' + repr(i + oparg) + ')'
            elif op in dis.haslocal:
                if varnames:
                    rvalue += '(' + varnames[oparg] + ')'
                else:
                    rvalue += '(%d)' % oparg
            elif op in dis.hascompare:
                rvalue += '(' + dis.cmp_op[oparg] + ')'
        rvalue += '\n'
    return rvalue[:-1]


def decompile(co, bc):
    '''
    A simple peephole decompiler
    '''

    if bc is None:
        return (None, None)

    if bc.opcode == opmap["LOAD_ATTR"]:
        prev, tmp = decompile(co, bc.prev)

        if tmp is None:
            return (None, None)

        return (prev, tmp + "." + co.co_names[bc.oparg])

    elif bc.opcode == opmap["STORE_ATTR"]:
        prev, tmp = decompile(co, bc.prev)
        if tmp is None:
            return (None, None)

        prev, val = decompile(co, prev)
        if val is None:
            return (None, None)

        return (prev, tmp + "." + co.co_names[bc.oparg] + " = " + val)

    elif bc.opcode == opmap["STORE_FAST"] or \
         bc.opcode == opmap["STORE_GLOBAL"]:

        prev, arg0 = decompile(co, bc.prev)
        if arg0 is None:
            return None, None
        return (prev, co.co_varnames[bc.oparg] + " = " + arg0)

    elif bc.opcode == opmap["PRINT_ITEM"]:
        prev, arg0 = decompile(co, bc.prev)
        if arg0 is None:
            return None, None
        return (prev, "print(%s)" % arg0)

    elif bc.opcode == opmap["POP_TOP"]:
        prev, arg0 = decompile(co, bc.prev)
        if arg0 is None:
            return None, None
        return (prev, arg0)

    elif bc.opcode == opmap["NOP"]:
        prev, arg0 = decompile(co, bc.prev)
        return (prev, arg0)

    elif bc.opcode == opmap["COMPARE_OP"]:
        prev, arg0 = decompile(co, bc.prev)
        if arg0 is None:
            return None, None

        prev, arg1 = decompile(co, prev)
        if arg1 is None:
            return None, None

        tmp = "(%s %s %s)" % (arg1, cmp_op[bc.oparg], arg0)
        return (prev, tmp)

    elif bc.opcode in binary_ops:
        prev, arg0 = decompile(co, bc.prev)
        if arg0 is None:
            return None, None

        prev, arg1 = decompile(co, prev)
        if arg1 is None:
            return None, None

        if bc.opcode == opmap["BINARY_SUBSCR"]:
            tmp = "%s[%s]" % (arg1, arg0)
        else:
            tmp = "%s %s %s" % (arg1, binary_ops[bc.opcode], arg0)
        return (prev, tmp)

    elif bc.opcode == opmap["CALL_FUNCTION"]:
        prev = bc.prev
        args = ""

        pos_args = bc.oparg & 0xff
        key_args = (bc.oparg >> 8) & 0xff

        for n in range(key_args):
            prev, name = decompile(co, prev)
            if name is None:
                return None, None

            prev, arg = decompile(co, prev)
            if arg is None:
                return None, None

            args = "%s=%s" % (arg, name) + ", " + args

        for n in range(pos_args):
            prev, tmp_arg = decompile(co, prev)
            if tmp_arg is None:
                return None, None

            args = tmp_arg + ", " + args

        if args != "":
            args = args[:-2]

        prev, fname = decompile(co, prev)
        if fname is None:
            return None, None

        return (prev, "%s(%s)" % (fname, args))

    elif bc.opcode == opmap["BUILD_TUPLE"]:
        prev = bc.prev
        args = ""
        for n in range(bc.oparg):
            prev, tmp_arg = decompile(co, prev)
            if tmp_arg is None:
                return None, None

            args = tmp_arg + ", " + args

        if args != "":
            args = args[:-2]

        return (prev, "(%s)" % (args))

    elif bc.opcode in cond_branches:
        prev, dec_str = decompile(co, bc.prev)

        if(dec_str is None):
            return None, None

        dec_str = "if %s:" % (dec_str)
        return (prev, dec_str)

    if bc.opcode in dis.hasconst:
        return (bc.prev, repr(co.co_consts[bc.oparg]))

    elif bc.opcode in dis.hasname:
        return (bc.prev, co.co_names[bc.oparg])

    elif bc.opcode in dis.haslocal:
        return (bc.prev, co.co_varnames[bc.oparg])

    return (None, None)
