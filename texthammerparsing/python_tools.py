import re 

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

def Prettify(s):
    """Add newlines around some of the xml tags in order to make sure that all
    segments will be processed. """
    lines = s.splitlines()
    output = ""
    for line in lines:
        if "<tu>" in line:
            output +=  "\n"
        output +=  line + "\n"
        if r"</tu>" in line:
            output +=  "\n"
    return output

def FixQuotes(fixedstring):
    """Force spaces around any type of quotation marks"""
    fixedstring =  re.sub(r"[^a-za-öа-я](\')"," \\1 ",fixedstring, flags=re.I)
    return re.sub(r"([\"]|&quot;)"," \\1 ",fixedstring)


def printHeading(text, hmark = "="):
    print("\n{0}\n{1}\n{0}".format(hmark*len(text), text))
