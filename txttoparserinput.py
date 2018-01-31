#! /usr/bin/env python
import sys
import csv
import glob
import os
import uuid
from lxml import etree
from python_tools import MissingMetaError
from tmxtoparserinput import CountMetaAttributes, ReadMetaData, WriteMetaData, FixQuotes, FilterLongSentences


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

    #NOTE: completely removing empty lines from the input (see the list comprehension inside join)
    #This is because paragraphs are defined by a SINGLE line break. Always.
    txtoutput = "{0}{1}{0}".format("\n","?"*10).join([thisline for thisline in lines if thisline])
    txtoutput = FixQuotes(txtoutput)

    return [root, txtoutput]

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
