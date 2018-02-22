#! /usr/bin/env python
import sys
import csv
import glob
import os
import uuid
from lxml import etree
from xml.sax.saxutils import unescape
import re
import FilterLongSentences
from conll_to_xml import Logger, logging
import json
from python_tools import Prettify, FixQuotes

class Document:
    """
    Represents a single file that is going to be prepared for parsing. This can be
    a tmx containing multiple 'versions' of the same text or just a text file
    containing a text to be parsed. Notice that these files have to 
    contain <textdef>-tags with some crucial metadata, minimally  the language of the document
    """
    def __init__(self, sourcefile):
        """
        Initializes the object by reading the content. 
        Also launches the metadata reader.

        - sourcefile: the full path  of the tmx file
        """
        self.pair_id = str(uuid.uuid4())
        self.dumpfile = "{}/{}/{}.json".format(os.path.dirname(os.path.abspath(__file__)), "auxiliary_files", self.pair_id)
        self.errors = []
        self.warnings = []
        self.filename = sourcefile
        k = sourcefile.rfind("/")
        self.mere_file = sourcefile[k+1:]
        with open(sourcefile, "r") as f:
            try:
                self.content = f.read()
            except UnicodeDecodeError:
                problem = "Tiedostossa {} koodausongelma. Luultavasti utf-16 pitäisi muuttaa utf-8:aan.".format(sourcefile)
                self.errors.append(problem)
                return False

    def CollectMetaDataAttributes(self):
        """
        Counts the number of different metadata attributes provided in the textdef tags
        In addition, checks if some of the versions are retranslations
        """

        try:
            self.translations_per_language = dict()
            #First, we have to collect all the available attributes
            self.all_meta_attributes = []
            self.metadata_for_versions = []
            for textdef in self.textdefs:
                self.metadata_for_versions.append(dict())
                for attrname, attr in textdef.items():
                    if attrname in ['language','lang']:
                        #Count the number of versions per language
                        #Note: Always use the lang tag instead of language
                        attrname = 'lang'
                        try:
                            self.translations_per_language[attr] += 1
                        except KeyError:
                            self.translations_per_language[attr] = 1
                    if attrname not in self.all_meta_attributes:
                        self.all_meta_attributes.append(attrname)
                    self.metadata_for_versions[-1][attrname] = attr
        except Exception as e:
            self.errors.append("Problem in collecting the metadata attributes from the textdef tags: {}".format(e))

    def ReportProblems(self, thiserror=None):
        """
        Print all the error or messages related to this file.
        - returns true or false depending on whether serious problems were found
        """
        if not self.errors:
            if thiserror:
                logging.error(thiserror)
            #logging.info("Great! No critical problems found with the file {}".format(self.filename))
        else:
            for error in self.errors:
                logging.error(error)
            with open("skippedfiles.txt","a") as f:
                f.write("\n" + self.filename)
            return True
        for warning in self.warnings:
            logging.warning(warning)
        return False

class Tmxfile(Document):
    """
    Represents the text as a whole: all the versions, including retranslations.
    """
    def __init__(self, sourcefile):
        self.filetype = "tmx"
        super().__init__(sourcefile)
        #Metadata for each text
        self.metafile = "{}/{}/{}_segment_meta.json".format(os.path.dirname(os.path.abspath(__file__)), "auxiliary_files", self.pair_id)
        self.versions = []

    def GetXml(self):
        """
        Reads the xml contents to an lxml etree object
        """
        try:
            self.content = unescape(self.content.replace('encoding="utf-8"',''),{"&apos;":"'","&quot;":"\""})
            self.content = Prettify(self.content.replace('encoding = "utf-8"','').strip())
            self.root = etree.fromstring(self.content.strip())
        except Exception as e:
            self.errors.append("Problem in reading the xml of the file: {}".format(e))

    def ReadTextdefs(self):
        """
        Reads the metadata attributes included in the textdef tags
        """
        self.textdefs = self.root.xpath("//textdef")
        if not self.textdefs:
            self.errors.append("""You have not provided metadata for
                the texts. The metadata should be provided as <textdef> tags
                including, minimally, the attributes code and lang""")

    def InitializeVersions(self):
        """
        Initializes each text as a separate 'Version' object, which can be either 
        a regular text or a retranslation.
        """
        for thisversion in self.metadata_for_versions:
            if self.translations_per_language[thisversion["lang"]] == 1:
                self.versions.append(Translation(thisversion["lang"],thisversion["code"],self.filename, self.pair_id))
            else:
                self.versions.append(Retranslation(thisversion["lang"],thisversion["code"],self.filename, self.pair_id))
            #Add metadata for this version
            for attr in self.all_meta_attributes:
                try:
                    self.versions[-1].metadata[attr] = thisversion[attr]
                except KeyError:
                    #Add even the values not specified (as empty)
                    self.versions[-1].metadata[attr] = ""

    def GetVersionContents(self):
        """
        Reads the contents of a tmx file and extracts each version of the text.
        """
        tu_tags = self.root.xpath("//tu")
        #Iterate over every single tu tag in the tmx
        #the tu tags represent segments
        for tu_idx, tu in enumerate(tu_tags):
            for version in self.versions:
                tuvs = tu.xpath(version.tuvpattern)
                segment_text = ""
                if tuvs:
                    #Just for debugging
                    version.number_of_segments += 1
                    tuv = tuvs[0]
                    #Check for additional metadata such as information about the current speaker
                    version.segment_meta.append({"speaker":tuv.get("speaker")})
                    if not tuv.getchildren():
                        segment_text = tuv.text
                    else:
                        for seg in tuv.getchildren():
                            if seg.text:
                                if segment_text:
                                    segment_text += " "
                                segment_text += seg.text
                    if segment_text:
                        segment_text = FixQuotes(segment_text)
                        #Note: the sentences are filtered in case of two long sentences to parse
                        #see longsentencelog.txt and FilterLongSentences.py
                        segment_text = FilterLongSentences.FilterByCharCount(segment_text, version.code)
                else:
                    #If this version (language or retranslation) doesn't have this particular segment at all
                    segment_text = "-"
                    version.segment_meta.append({"speaker":""})
                    logging.warning("Segment number {} DOESN'T EXIST for {} (language {})".format(tu_idx +1, version.code,version.lang))
                version.segments.append(segment_text.strip())

    def WritePreparedFiles(self):
        """
        Write all the prepared files to the specified destinations.
        Also, write an auxiliary file containing segment-specific metadata.
        """
        segment_meta = {}
        for version in self.versions:
            logging.info("Writing {}. Number of segments: {}".format(version.prepared_filename, version.number_of_segments))
            with open(version.prepared_filename,"w") as f:
                f.write(version.segmentsplitpattern.join(version.segments))
            segment_meta[version.lang] = version.segment_meta

        #Save the collected metadata about segments to a separate json dump
        with open(self.metafile,"w") as f:
            json.dump(segment_meta, f, ensure_ascii=False)

class Version:
    """
    Represents a single version of the text, which is itself represented as one single tmx file.
    Most often the tmx file consists of 2 or more versions, one of which is the source text
    while the others are target texts. It should be noted, that some versions are actually
    retranslations, so that one language may contain several versions
    """

    def __init__(self, lang, code, sourcefile, pair_id):
        self.segmentsplitpattern = "\n" + "!"*15 + "\n"
        self.lang = lang
        self.pair_id = pair_id
        self.code = code
        self.segments = []
        self.metadata = {}
        #This is for saving segment specific meta information such as speakers in a dialogue context
        self.segment_meta = []
        self.prepared_filename = '{}_{}_{}.prepared'.format(sourcefile, self.code, self.lang)
        k = sourcefile.rfind("/")
        self.mere_file = sourcefile[k+1:]
        self.parsed_filename  = '{}/{}/{}_{}_{}.prepared.conll'.format(sys.argv[2], self.lang, self.mere_file, self.code, self.lang)
        self.metadata["filename"] = self.parsed_filename
        #Just as a useful information: collect the number of segments in each version
        self.number_of_segments = 0

class Translation(Version):
    """
    If the version we are dealing with is a regular translation, it is represented by this class
    OR if this is the source text, the Translation class will be used anyway.
    """
    def __init__(self, lang, code, sourcefile, pair_id):
        super().__init__(lang, code, sourcefile, pair_id)
        self.tuvpattern = "tuv[@xml:lang='{}' or  @xml:lang='{}']".format(self.lang, self.lang.upper())
        self.versiontype = "regular"
                
class Retranslation(Version):
    """
    If the version we are dealing with is actually a retranslation, it is represented by this class
    """
    def __init__(self, lang, code, sourcefile, pair_id):
        super().__init__(lang, code, sourcefile, pair_id)
        self.tuvpattern = "tuv[(@xml:lang='{}' or @xml:lang='{}') and @code='{}']".format(self.lang, self.lang.upper(), self.code)
        self.versiontype = "retranslation"

def FireScript(msg, loggerfilenamename, filetype):
    """
    Only fire the script off if the user has supplied correct parameters

    - msg: The message to show if the parameters haven't been right
    - loggerfilenamename: Where to save the logging messages
    - filetype: what kind of files do you expect as input (tmx, txt)
    - returns a list of the files that will be processed
    """
    try:
        sourcefile = sys.argv[1]
        parsedfolder = sys.argv[2]
        if sys.argv[2][-1] == "/":
            sys.argv[2] = sys.argv[2][:-1]
    except:
        print(msg)
        sys.exit(0)

    thislogger = Logger(loggerfilenamename)

    if os.path.isdir(sourcefile):
        #Processing a whole folder 
        slash = "" if sourcefile[-1] == "/" else "/"
        files = glob.glob(sourcefile + slash + '*' + filetype)
    else: 
        files = [sourcefile]

    return files

def main():
    msg = "Usage: {} <path to source tmx or folder containing multiple tmxs> <folder to save the parsed files>'".format(sys.argv[0])
    files = FireScript(msg, "tmxtoparserinput.log","tmx")
    #Output = Information about the prepared files will be stored in this dict, which will be dumped as a json file
    output = {}
    for filename in files:
        logging.info("Starting to analyze the following tmx file: {}.".format(filename))
        thisfile = Tmxfile(filename)
        try:
            thisfile.GetXml()
            thisfile.ReadTextdefs()
            thisfile.CollectMetaDataAttributes()
            thisfile.InitializeVersions()
            thisfile.GetVersionContents()
            if not thisfile.ReportProblems():
                thisfile.WritePreparedFiles()
                output[thisfile.pair_id] = [version.metadata for version in thisfile.versions]
        except Exception as e:
            thisfile.ReportProblems(e)
    if output:
        with open("parsedmetadata.json","w") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
    else:
        logging.error("No output produced.")


if __name__ == "__main__":
    main()
