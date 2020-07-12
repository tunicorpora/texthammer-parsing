#! /usr/bin/env python
import sys
#import csv
#import glob
import os
import uuid
from lxml import etree
from xml.sax.saxutils import unescape
#import re
from  texthammerparsing.FilterLongSentences import FilterByCharCount
import json
from texthammerparsing.python_tools import Prettify, FixQuotes
import logging
import traceback


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
        self.errors = []
        self.warnings = []
        self.filename = sourcefile
        k = sourcefile.rfind("/")
        self.mere_file = sourcefile[k+1:]
        with open(sourcefile, "r") as f:
            try:
                self.content = f.read()
            except UnicodeDecodeError:
                problem = "Encoding problem with file {}. Possible reason: utf-16 should be converted to utf-8.".format(sourcefile)
                self.errors.append(problem)
                self.content = ''
                return False
            except:
                problem = "Unknown error reading the file {} ".format(sourcefile)
                self.errors.append(problem)
                self.content = ''

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
                logging.error("Check the file /tmp/detailed_error_log.txt for more details on why and where the python script failed.")
                with open("/tmp/detailed_error_log.txt","w") as f:
                    f.write(traceback.format_exc())
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

    def InitializeVersions(self, output_folder="/tmp"):
        """
        Initializes each text as a separate 'Version' object, which can be either 
        a regular text or a retranslation.
        """
        for thisversion in self.metadata_for_versions:
            if self.translations_per_language[thisversion["lang"]] == 1:
                self.versions.append(Translation(thisversion["lang"],thisversion["code"],self.filename, self.pair_id, output_folder))
            else:
                self.versions.append(Retranslation(thisversion["lang"],thisversion["code"],self.filename, self.pair_id, output_folder))
            #Add metadata for this version
            for attr in self.all_meta_attributes:
                try:
                    self.versions[-1].metadata[attr] = thisversion[attr]
                except KeyError:
                    #Add even the values not specified (as empty)
                    self.versions[-1].metadata[attr] = ""

    def AddCodes(self, lang, filename):
        tuvpattern = "tuv[@xml:lang='{}' or  @xml:lang='{}']".format(lang, lang.upper())
        langversions = []
        for ver in self.versions:
            if ver.lang == lang or ver.lang.upper() == lang:
                langversions.append(ver.code)
        tu_tags = self.root.xpath("//tu")
        for tu_idx, tu in enumerate(tu_tags):
            tuvs = tu.xpath(tuvpattern)
            for tuv_idx, tuv in enumerate(tuvs):
                tuv.attrib['code'] = langversions[tuv_idx]

        xmlstring = etree.tounicode(self.root, pretty_print=True)
        with open(filename.replace('.tmx','_with_codes.tmx'),'w') as f:
            f.write(xmlstring)
        print('Done. Wrote a new file: {}'.format(filename))


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
                    tuv = tuvs[0]
                    #Check for additional metadata such as information about the current speaker
                    version.segment_meta.append({"speaker":tuv.get("speaker")})
                    if not tuv.getchildren():
                        segment_text = tuv.text
                    else:
                        #If this text uses seg tags
                        for seg in tuv.getchildren():
                            if seg.text:
                                if segment_text:
                                    segment_text += " "
                                segment_text += seg.text
                if segment_text:
                    version.AddRealSegment(segment_text)
                else:
                    version.AddEmptySegment(tu_idx +1)

    def WritePreparedFiles(self):
        """
        Write all the prepared files to the specified destinations.
        Also, write an auxiliary file containing segment-specific metadata.
        """
        root = "/tmp/texthammerparsing/" + self.pair_id
        # First, let's create a temporary directory for each tmx
        os.makedirs(root, exist_ok=True)
        os.makedirs(root + "/prepared", exist_ok=True)
        segment_meta = {}
        for version in self.versions:
            langdir = root + "/prepared/" + version.lang
            os.makedirs(langdir, exist_ok=True)
            if logging:
                logging.info("Writing {}. Number of segments: {}".format(version.code, version.number_of_segments))
            with open(langdir +  "/" + version.code,"w") as f:
                f.write(version.segmentsplitpattern.join(version.segments))
            segment_meta[version.lang] = version.segment_meta

        #Save the collected metadata about segments to a separate json dump
        with open(root + "/metadata.json","w") as f:
            json.dump(segment_meta, f, ensure_ascii=False)
        #Finally, write the metadata about each version 
        with open(root + "/versionmetadata.json","w") as f:
            json.dump([version.metadata for version in self.versions], f, ensure_ascii=False, indent=4)

class Version:
    """
    Represents a single version of the text, which is itself represented as one single tmx file.
    Most often the tmx file consists of 2 or more versions, one of which is the source text
    while the others are target texts. It should be noted, that some versions are actually
    retranslations, so that one language may contain several versions
    """

    def __init__(self, lang, code, sourcefile, pair_id, output_folder):
        self.segmentsplitpattern = "\n" + "###C:segmentsplit" + "\n"
        self.lang = lang
        self.pair_id = pair_id
        self.code = code
        self.segments = []
        self.metadata = {}
        #This is for saving segment specific meta information such as speakers in a dialogue context
        self.segment_meta = []

        k = sourcefile.rfind("/")
        self.mere_file = sourcefile[k+1:]
        self.parsed_filename  = '{}/{}/{}_{}_{}.prepared.conll'.format(output_folder, self.lang, self.mere_file, self.code, self.lang)
        self.metadata["filename"] = self.parsed_filename

        #Just as a useful information: collect the number of segments in each version
        self.number_of_segments = 0

    def AddRealSegment(self, segment_text):
        """
        Adds the segment to the list of segments for this version.
        """
        segment_text = FixQuotes(segment_text.strip())
        self.segments.append(segment_text)
        #Note: the sentences are filtered in order to detect sentences too long to parse
        #see longsentencelog.txt and FilterLongSentences.py
        segment_text = FilterByCharCount(segment_text, self.code)
        self.number_of_segments += 1

    def AddEmptySegment(self, seg_no):
        """
        Adds an empty segment in case there really was nothing present in a segment.
        (wither nothin inside seg-tags or nothing inside tuv-tags)
        An empty segment is marked by emptysegmentmarker
        - seg_no: number of the segment where the error occured
        """
        emptysegmentmarker = "-"
        self.segment_meta.append({"speaker":""})
        self.segments.append(emptysegmentmarker)
        logging.warning("Segment number {} DOESN'T EXIST for {} (language {})".format(seg_no, self.code, self.lang))

class Translation(Version):
    """
    If the version we are dealing with is a regular translation, it is represented by this class
    OR if this is the source text, the Translation class will be used anyway.
    """
    def __init__(self, lang, code, sourcefile, pair_id, output_folder):
        super().__init__(lang, code, sourcefile, pair_id, output_folder)
        self.tuvpattern = "tuv[@xml:lang='{}' or  @xml:lang='{}']".format(self.lang, self.lang.upper())
        self.versiontype = "regular"
                
class Retranslation(Version):
    """
    If the version we are dealing with is actually a retranslation, it is represented by this class
    """
    def __init__(self, lang, code, sourcefile, pair_id, output_folder):
        super().__init__(lang, code, sourcefile, pair_id, output_folder)
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
        try:
            thisfile = Tmxfile(filename)
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
