class MissingTextError(Exception):
    pass

class AlignMismatch(Exception):
    pass

class ArgumentError(Exception):
    pass

class MissingMetaError(Exception):
    pass

def TrimList(clist):
    """Checks if the first or the  last element of a list is empty"""
    try:
        if clist[0] == '':
            clist = clist[1:]
        if clist[-1] == '':
            clist = clist[:-1]
    except IndexError:
        clist = clist
    return clist
