#! /usr/bin/env python
import sys
import csv
import glob
import os
import uuid
import re
from lxml import etree
from python_tools import MissingMetaError
from tmxtoparserinput import CountMetaAttributes, ReadMetaData, WriteMetaData, FixQuotes, FilterLongSentences
from conll_to_xml import Logger, logging


def ReadXml(sourcefile):
    root = None

    #Add full stops for sentences longer than a specified threshold
    with open(sourcefile, "r") as f:
        rawstring = f.read()
    rawstring = FilterLongSentences.FilterByCharCount(rawstring, sourcefile)
    lines = rawstring.splitlines()

    #with open(sourcefile, "r") as f:
    #    lines = f.readlines()

    metalineidx = None
    for idx, line in enumerate(lines):
        if "<textdef" in line:
            root = etree.fromstring(line)
            metalineidx = idx
        line = line.strip()
    #Remove the metadata tag from the actual prepared output
    try:
        del lines[metalineidx]
    except TypeError:
        raise MissingMetaError("No metadata (textdef-tag) given in the input file {}, exiting..".format(sourcefile))

    lines = CheckIfHardWrap(lines, sourcefile)
    #NOTE: completely removing empty lines from the input (see the list comprehension inside join)
    #This is because paragraphs are defined by a SINGLE line break. Always.
    txtoutput = "{0}{1}{0}".format("\n","?"*10).join([thisline for thisline in lines if thisline])
    txtoutput = FixQuotes(txtoutput)

    return [root, txtoutput]

def CheckIfHardWrap(lines, fname):
    """
    Try to determine, whether or not this text is hard-wrapped.
    this is done by checking the amount of lines with  no sentence-terminating punctuation at the end.
    If the function suspects hard wrapping, ask the user for action and give
    the possibility to terminate the script.

    lines: all the lines of the text as a list
    fname: the name of the file that is being processed
    """
    terminating_punctuation_marks = [".",";","!","?",":"]
    no_terminating_punct = 0
    terminating_punct = 0
    empty_lines = 0
    unwrapped_lines = [""]
    for line in lines:
        if line:
            if line.strip()[-1] not in terminating_punctuation_marks:
                #Check if this is potentially a header:
                words = re.split(r"\s+", line)
                if(len(words)>4):
                    no_terminating_punct += 1
            else:
                terminating_punct += 1
            #Just in case: make a list of real paragraphs assuming this text is
            #hard-wrapped
            if unwrapped_lines[-1].strip():
                unwrapped_lines[-1] += " "
            unwrapped_lines[-1] += line
        else:
            empty_lines += 1
            if unwrapped_lines[-1].strip():
                unwrapped_lines.append("")
    noterm_percentage = no_terminating_punct / (no_terminating_punct + terminating_punct) *100
    if noterm_percentage > 40 and empty_lines > 2:
        logging.warning("""
            A NOTE ABOUT PARAGRAPHS in this file:
            
            It seems like this text ({}) 
            is hard-wrapped i.e.  paragraph breaks are marked by empty lines.
            The parsing script, however, always assumes that a paragraph is
            *soft-wrapped* i.e. all the sentences are on the same line and the
            paragraphs are separated from each other by a single line break.
            To ensure correct parsing, you should probably check the file.

            This script is now going to automatically convert the file into
            a soft-wrapped version.
            """.format(fname))
        return lines
    return lines


def WritePreparedOutput(sourcefile, metadata, preparedinput,text_idx):
    filename = '{}.prepared'.format(sourcefile)
    #Write the prepared file
    with open(filename, 'w') as f:
        f.write(preparedinput.strip())
    #Save the filename of the file after parsing in the dict for future use
    k = sourcefile.rfind("/")
    mere_file = sourcefile[k+1:]
    metadata[text_idx]["filename"] = '{}/{}.prepared.conll'.format(sys.argv[2],mere_file)

def main():
    thislogger = Logger("txttoparserinput.log")
    try:
        sourcefile = sys.argv[1]
        parsedfolder = sys.argv[2]
        if sys.argv[2][-1] == "/":
            sys.argv[2] = sys.argv[2][:-1]
    except:
        print('Usage: {} <path to source txt or folder containing multiple txts> <folder to save the parsed files>'.format(sys.argv[0]))
        sys.exit(0)

    attrnames = list()

    if os.path.isdir(sourcefile):
        metadata = list()
        if sourcefile[-1] == "/":
            slash = ""
        else:
            slash = "/"

        #Get all the attributes in the metadata
        for filename in glob.glob(sourcefile + slash + '*'):
            inputdata = ReadXml(filename)
            root = inputdata[0]
            attrnames = CountMetaAttributes(root, attrnames)

        #Process the txt files
        for idx, filename in enumerate(glob.glob(sourcefile + slash + '*')):
            inputdata = ReadXml(filename)
            root = inputdata[0]
            if not metadata:
                metadata = ReadMetaData(root, attrnames)
            else:
                metadata.extend(ReadMetaData(root, attrnames))
            WritePreparedOutput(filename, metadata, inputdata[1],idx)
    else:
        #No folder, a single file given
        inputdata = ReadXml(sourcefile)
        root = inputdata[0]
        attrnames = CountMetaAttributes(root, attrnames)
        metadata = ReadMetaData(root, attrnames)
        WritePreparedOutput(sourcefile, metadata, inputdata[1],0)

    WriteMetaData(metadata)


if __name__ == "__main__":
    main()
