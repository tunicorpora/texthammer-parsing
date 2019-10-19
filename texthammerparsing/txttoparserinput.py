#! /usr/bin/env python
import sys
import glob
import logging
import os
import uuid
import re
import json
from lxml import etree
from texthammerparsing.python_tools import MissingMetaError
from texthammerparsing.configs import getConf
from texthammerparsing import FilterLongSentences
from texthammerparsing.tmxtoparserinput import FixQuotes,  Document

class Txtfile(Document):
    """
    Represents the text file as a whole.
    """

    def __init__(self, sourcefile):
        self.filetype = "txt"
        super().__init__(sourcefile)
        self.lines = self.content.splitlines()
        # If the script is used just for fixing possibly too long txt files, use the following attribute
        self.justfixing = False

    def ReadTextdefs(self):
        """
        Reads the metadata attributes included in the textdef tags
        """
        try:
            self.textdefs = []
            metalineidx = None
            for idx, line in enumerate(self.lines):
                if "<textdef" in line:
                    line = line.replace(' ',' ') # remove soft spaces
                    self.textdefs.append(etree.fromstring(line))
                    metalineidx = idx
                line = line.strip()
        except Exception as e:
            self.errors.append("Problem in reading the metadata from the textdef tags: {}".format(e))
        #Remove the metadata tag from the actual prepared output
        try:
            del self.lines[metalineidx]
        except TypeError:
            ignore = True
            if len(sys.argv) > 3:
                if sys.argv[3] == "justfix":
                    ignore = True
                    self.justfixing = True
            if not ignore:
                self.errors.append("""You have not provided metadata for
                    the texts. The metadata should be provided as <textdef> tags
                    including, minimally, the attributes code and lang""")

    def MarkParagraphs(self, justfixing):
        """
        Mark the place of paragraphs by using a predefined pattern
        """ 
        pattern = "\n" + "###C:" + getConf("paragraphsplit") + "\n"
        if not justfixing:
            ##NOTE: completely removing empty lines from the input (see the list comprehension inside join)
            self.output = pattern.join([thisline for thisline in self.lines if thisline])
        else:
            self.output = "\n".join([thisline for thisline in self.lines if thisline])

    def WritePreparedFiles(self):
        """
        Writes the prepared file
        """

        try:
            lang = self.metadata_for_versions[0]["lang"]
        except:
            lang = input("Please specify the language of the document ({}) using a two-character language code \n>".format(self.filename))
        try:
            code = self.metadata_for_versions[0]["code"]
        except:
            code = re.sub(r"([^.]+)\.\w+$",r"\1",os.path.basename(self.filename))

        root = "/tmp/texthammerparsing/" + self.pair_id + "/"  
        langdir = "/tmp/texthammerparsing/" + self.pair_id + "/prepared/" + lang + "/"

        os.makedirs(root, exist_ok=True)
        os.makedirs(langdir, exist_ok=True)

        self.output = FixQuotes(self.output)
        logging.info("Writing {}".format(langdir + code))
        with open(langdir + code,"w") as f:
            f.write(self.output)
        try:
            with open(root + "versionmetadata.json","w") as f:
                json.dump(self.metadata_for_versions[0], f, ensure_ascii=False, indent=4)
        except:
            with open(root + "versionmetadata.json","w") as f:
                json.dump({"lang" : lang, "code": code}, f, ensure_ascii=False, indent=4)

    def CheckIfHardWrap(self):
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
        for line in self.lines:
            if line.strip():
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
        #print("No term percentage: {}".format(noterm_percentage))
        #print("empty_lines: {}".format(empty_lines))
        if noterm_percentage > 40:
            self.warnings.append(
                """
                A NOTE ABOUT PARAGRAPHS in this file:
                
                It seems like this text ({}) is hard-wrapped i.e.  paragraph
                breaks are marked by empty lines or not marked at all.  This
                conclusion is based on the fact that  **the text has suspiciously
                many ({} %)** lines that are not terminated by punctuation marks.
                The parsing script always assumes that a paragraph is
                *soft-wrapped* i.e. all the sentences are on the same line and
                the paragraphs are separated from each other by a single line
                break.  To ensure correct parsing, you should probably check
                the file.

                This script is now going to automatically convert the file into
                a soft-wrapped version.
                """.format(self.filename,round(noterm_percentage,2)))

    def FilterSentencesAndParagraphs(self, justfixing):
        """
        Run filters in order to strip or sentences that are too long to parse
        """ 
        pattern = "\n" + "###C:" + getConf("paragraphsplit") + "\n"
        if not justfixing:
            #Note: the sentences are filtered in order to detect sentences too long to parse
            #see longsentencelog.txt and FilterLongSentences.py
            self.output = FilterLongSentences.FilterByCharCount(self.output, self.filename, True, pattern)
        else:
            self.output = FilterLongSentences.FilterByCharCount(self.output, self.filename, True,"\n")

def main():
    msg = 'Usage: {} <path to source txt or folder containing multiple txts> <folder to save the parsed files>'.format(sys.argv[0])
    files = FireScript(msg, "txttoparserinput.log","txt")
    #Output = Information about the prepared files will be stored in this dict, which will be dumped as a json file
    output = {}
    for filename in files:
        logging.info("Starting to analyze the following txt file: {}.".format(filename))
        thisfile = Txtfile(filename)
        try:
            thisfile.ReadTextdefs()
            thisfile.CheckIfHardWrap()
            thisfile.CollectMetaDataAttributes()
            thisfile.MarkParagraphs()
            thisfile.FilterSentencesAndParagraphs()
            if not thisfile.ReportProblems():
                thisfile.WritePreparedFiles()
                #Note: making this a list in order to be compatible with tmxs
                if not thisfile.justfixing:
                    output[thisfile.pair_id] = [thisfile.metadata]
        except Exception as e:
            thisfile.ReportProblems(e)

    if output:
        with open("parsedmetadata.json","w") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
    else:
        if not thisfile.justfixing:
            logging.error("No output produced.")

if __name__ == "__main__":
    main()
