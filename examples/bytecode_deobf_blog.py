from dis import opmap
import StringIO

import bytecode_graph
import pefile


def clean_ROT_TWO(bcg, skip_xrefs=True):
    '''
    Replace two sequential ROT_TWO sequences with NOPS
    '''
    count = 0

    for current in bcg.nodes():
        if current.next is None:
            break

        if current.opcode == opmap['ROT_TWO'] and \
           current.next.opcode == opmap['ROT_TWO']:
            if current.next.xrefs != [] and skip_xrefs:
                continue
            else:
                current.opcode = opmap['NOP']
                current.next.opcode = opmap['NOP']
                count += 1
    return count


def clean_ROT_THREE(bcg, skip_xrefs=True):
    '''
    Replace three sequential ROT_THREE sequences with NOPS
    '''
    count = 0

    for current in bcg.nodes():
        if current.next is None or current.next.next is None:
            break

        if current.opcode == opmap['ROT_THREE'] and \
                current.next.opcode == opmap['ROT_THREE'] and \
                current.next.next.opcode == opmap['ROT_THREE']:

            if (current.next.xrefs != [] or current.next.next.xrefs != []) \
                    and skip_xrefs:
                        continue
            else:
                    current.opcode = opmap['NOP']
                    current.next.opcode = opmap['NOP']
                    current.next.next.opcode = opmap['NOP']
                    count += 1
    return count


def clean_LOAD_POP(bcg, skip_xrefs=True):
    '''
    Replace LOAD_CONST/POP_TOP sequences with NOPS
    '''
    count = 0

    for current in bcg.nodes():
        if current.next is None:
            break

        if current.opcode == opmap['LOAD_CONST'] and \
                current.next.opcode == opmap['POP_TOP']:

            if current.next.xrefs != [] and skip_xrefs:
                continue
            else:
                current.opcode = opmap['NOP']
                current.next.opcode = opmap['NOP']
                count += 1
    return count


def clean_NOPS(bcg):
    '''
    Remove NOP instrustions from bytecode
    '''
    count = 0

    for current in bcg.nodes():
        if current.opcode == opmap['NOP']:
            bcg.delete_node(current)
            count += 1

    return count


def clean(code, skip_xrefs=True):

    bcg = bytecode_graph.BytecodeGraph(code)

    rot_two = clean_ROT_TWO(bcg, skip_xrefs)
    rot_three = clean_ROT_THREE(bcg, skip_xrefs)
    load_pop = clean_LOAD_POP(bcg, skip_xrefs)
    nops = clean_NOPS(bcg)

    # return new code object if modifications were made
    if rot_two > 0 or rot_three > 0 or load_pop > 0 or nops > 0:
        return bcg.get_code()

    return None


def decompile(code, version="2.7"):

    import meta
    from uncompyle2 import uncompyle

    try:
        source = StringIO.StringIO()
        uncompyle(version, code, source)
        source = source.getvalue()
    except:
        try:
            code_obj = meta.decompile(code)
            source = meta.dump_python_source(code_obj)
        except:
            return None

    return source.lstrip(' \n')


def get_rsrc(pe, name):

    for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        rsrc_name = str(resource_type.name)

        if str(resource_type.name) != name:
            continue

        for resource_id in resource_type.directory.entries:
            if not hasattr(resource_id, 'directory'):
                continue

            entry = resource_id.directory.entries[0]

            rsrc = pe.get_data(entry.data.struct.OffsetToData,
                               entry.data.struct.Size)
            return rsrc
    return None


if __name__ == "__main__":

    import sys
    import marshal

    if len(sys.argv) < 3:
        print "usage: %s [exe to parse] [output file]" % sys.argv[0]
        sys.exit(0)

    pe = pefile.PE(sys.argv[1])
    rsrc = get_rsrc(pe, "PYTHONSCRIPT")

    if rsrc is not None and rsrc[:4] == "\x12\x34\x56\x78":
        offset = rsrc[0x010:].find("\x00")
        if offset >= 0:
            py2exe_code = marshal.loads(rsrc[0x10 + offset + 1:])
            code = clean(py2exe_code[-1])

            if code is None:
                print "No obfuscation detected"
                sys.exit(0)

            src = decompile(code)

            if src is not None:
                open(sys.argv[2], "wb").write(src)
            else:
                print "Decompile failed"
        else:
            print "Failed to find end of header"
    else:
        print "Failed to find PYTHONSCRIPT resource"
