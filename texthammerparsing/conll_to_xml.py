#!/usr/bin/python3
from lxml import etree
import sys
import string
from csv import DictReader
import os
import re
from texthammerparsing.python_tools import AlignMismatch, TrimList, MissingTextError, ArgumentError
from texthammerparsing.configs import getConf
from collections import OrderedDict
import os.path
import logging
import json
import glob

class ParserInfo():
    """The parsers' conll output format may vary.
    To control the different kinds of orderings of the conll columns,
    this class record information about the parser.
    """
    parsername = "unspecified"

class TextPair():
    """A collection of the source text and its translations.
    Pair is actually somewhat misleading: these objects consist of a source
    text and as many translations as specified
    
    - pair_id a unique id identifying the source tmx / txt file 
    - source lang (optionally): specify which language is the source 
    """

    def __init__(self, pair_id, source_lang=None):
        self.pair_id = pair_id
        self.tl_texts = []
        self.GetParsedDocuments(source_lang)
        self.root = etree.Element("text")

    def GetParsedDocuments(self, source_lang):
        """
        Iterates through the folder specified by the pair id
        and reads the parsed files

        - source lang: specify which language is the source 
        """
        langs = {}
        sourcetext = None
        for filename in glob.glob('/tmp/texthammerparsing/{}/parsed/**/*'.format(self.pair_id), recursive=True):
            if filename[-5:] != ".json" and os.path.isfile(filename):
                lang = re.search(r"[^/]+$",filename[:filename.rfind("/")])
                if not lang:
                    print("Error in determinig languages")
                elif lang.group(0) not in langs:
                    langs[lang.group(0)] = [os.path.basename(filename)]
                else:
                    langs[lang.group(0)].append(os.path.basename(filename))

        if source_lang:
            self.sl_text = ParsedText(langs[source_lang][0], 'source', self.pair_id)
        else:
            #No source lang specified, pick whichever comes first
            text_type = "source"
            for lang, versions in langs.items():
                for version in versions:
                    text = ParsedText(version, text_type, lang, self.pair_id)
                    if text_type == "source":
                       self.sl_text = text
                       text_type = "target"
                    else:
                        self.tl_texts.append(text)

        #Read segmentwise metadata from a separate json file identified by the id of the text pair
        #(only if there is such a file, i.e. if this is a tmx we are parsing)

        metafile = "/tmp/texthammerparsing/{}/metadata.json".format(self.pair_id)
        with open(metafile, "r") as f:
            self.segment_meta = json.load(f)

    def FormatMetaData(self, metaline):
        """Write the metadata for this language as a 'textdef' tag"""
        del(metaline['filename'])
        if 'pair_id' in metaline:
            del(metaline['pair_id'])
        metatag = etree.SubElement(self.root, "textdef", metaline)

    def LoopThroughSentences(self):
        for idx, paragraph in enumerate(self.sl_text.paragraphs):
            #start a new paragraph and a new sentencce
            linesofparagraph = paragraph.splitlines()
            processed = True
            if any(linesofparagraph):
                #If not an empty paragraph
                self.current_p = etree.SubElement(self.root, "p")
                #import ipdb;ipdb.set_trace()
                self.current_s = etree.SubElement(self.current_p, "s")
                processed = self.ProcessWordsOfSegment(paragraph.splitlines(), self.sl_text)
            if not processed:
                return False
        return True

    def LoopThroughSegments(self):
        for idx, segment in enumerate(self.sl_text.alignsegments):
            #Split each segment into lines (line=word with all the morphological and syntactic information)
            self.current_align = etree.SubElement(self.root, "align")
            #Process the source text
            self.current_seg = etree.SubElement(self.current_align, "seg", lang = self.sl_text.language, code = self.sl_text.code)
            #Add metadata about the segment for the source language
            if self.segment_meta:
                self.AddMetaToSegment(idx, self.sl_text.language)
                for meta_attr, meta_val in self.segment_meta[self.sl_text.language][idx].items():
                    if  not meta_val:
                        self.current_seg.attrib[meta_attr] = "unspecified"
            #start a new sentence in the beginning of the segment
            self.current_s = etree.SubElement(self.current_seg, "s")
            processed = self.ProcessWordsOfSegment(segment.splitlines(),self.sl_text)
            #Process the target texts
            for tl_text in self.tl_texts:
                #Get the correct align segment by number
                segs = tl_text.alignsegments
                seg1 = tl_text.alignsegments[0]
                seg2 = tl_text.alignsegments[-1]
                try:
                    segment = tl_text.alignsegments[idx]
                except IndexError:
                    import ipdb;ipdb.set_trace()
                    logging.info("Something wrong! The segments don't match!\n\nId of the text: {}\n\n Last segment to be processed: {}".format(self.sl_text.code,tl_text.alignsegments[-1]))
                    return False
                self.current_seg = etree.SubElement(self.current_align, "seg", lang = tl_text.language, code = tl_text.code)
                #Add metadata about the segment for the current target language
                if self.segment_meta:
                    self.AddMetaToSegment(idx, tl_text.language)
                # Add a new sentence 
                self.current_s = etree.SubElement(self.current_seg, "s")
                processed = self.ProcessWordsOfSegment(segment.splitlines(), tl_text)
                if not processed:
                    return False
        return True

    def WriteXml(self, outputpath=""):
        """
        - outputpath the folder to output the xml files to
        """
        if not outputpath:
            outputpath = "/tmp/texthammerparsing/{}/xml".format(self.pair_id)
            os.makedirs(outputpath, exist_ok=True)

        if outputpath[-1] != r"/":
            outputpath += r"/"

        xmlstring = etree.tounicode(self.root, pretty_print=True)
        filename = outputpath + self.sl_text.code + '.xml'
        with open(filename,'w') as f:
            f.write(xmlstring)
        print('Done. Wrote {}'.format(filename))

    def ProcessWordsOfSegment(self, tokenlines, text, singlesentence=False):
        """Pick lemma + pos + morhpology + dependency information from each line of the conll formatted input
        - The singlesentence property is for monolingual texts
        """
        tokenlines = TrimList(tokenlines)
        #Separate beginning and ending quotes for each segment.
        #should this be done earlier?
        self.squotetype='begin'
        self.dquotetype='begin'
        if singlesentence:
            self.current_s = etree.SubElement(self.root, "s")
        for idx, word in enumerate(tokenlines):
            if idx ==0 and not word:
                #If the first line is empty, skip it
                continue
            #read all the information about the word
            if word == '':
                #empty lines are sentence breaks
                try:
                    self.current_s = etree.SubElement(self.current_seg, "s")
                except AttributeError:
                    #if this is a monolingual file with no segment division
                    self.current_s = etree.SubElement(self.current_p, "s")
            else:
                columns = word.split('\t')
                if len(columns)==1:
                    columns = word.split(' ')
                    if len(columns)==1:
                        #If only a number on a line, skip this word
                        continue
                #Collect properties from the conll formatted row
                tokenproperties = text.CollectTokenProperties(columns)
                #Set the words properties as xml elements according to the texthammer xml schema
                #1. The token tag
                try:
                    if tokenproperties['token'] in string.punctuation:
                        #Should punctuation marks also have headid etc?
                        attributes = OrderedDict([("type","punct"), ("punctype",self.SetPunctType(tokenproperties['token'])) ])
                    else:
                        attributes = OrderedDict([("type","word"),
                                                  ("tokenid",str(tokenproperties['tokenid'])),
                                                  ("lemma",str(tokenproperties['lemma'])),
                                                  ("pos",str(tokenproperties['pos'])),
                                                  ("frm",str(tokenproperties['feat'])),
                                                  ("deprel",str(tokenproperties['deprel'])),
                                                  ("headid",str(tokenproperties['head'])),
                                                      ])
                except TypeError:
                    sys.exit("Error in determining token properties. Guess: The script not yet configured for this language?")
                try:
                    self.current_word = etree.SubElement(self.current_s, "token", attributes)
                except Exception as e:
                    logging.info("Something wrong! Id of the text: {}\n. Error message {}. Number of segments: {} ".format(text.code, e, len(text.alignsegments)))
                    return False
                self.current_word.text = tokenproperties['token']
        return True

    def SetPunctType(self, tokentext):
        """Decide, whether the punctuation makr is a sentence end marker,
        opening/closing punctuation mark, a dash etc"""

        if tokentext in ('(','[','{'):
            return 'open'
        elif tokentext in (')',']','}'):
            return 'close'
        elif tokentext in ('.','?','!'):
            return 'sent'
        #Special treatment of quotation marks depending on whether this is the first, second etc in the segment.
        elif tokentext == "'" :
            if self.squotetype == 'begin':
                self.squotetype = 'end'
                return 'open'
            elif self.squotetype == 'end':
                self.squotetype = 'begin'
                return 'close'
        elif tokentext == '"': 
            if self.dquotetype == 'begin':
                self.dquotetype = 'end'
                return 'open'
            elif self.dquotetype == 'end':
                self.dquotetype = 'begin'
                return 'close'
        else:
            #gen = general punctuation mark
            return 'gen'

    def AddMetaToSegment(self, idx, lang):
        """
        Adds metadata (e.g. the current speaker) to segment 
        - idx : the id of the current segment
        - lang : language code for the language being processed
        TODO: what about retranslations?
        """
        for meta_attr, meta_val in self.segment_meta[lang][idx].items():
            if not meta_val:
                self.current_seg.attrib[meta_attr] = "unspecified"
            else:
                self.current_seg.attrib[meta_attr] = meta_val

class ParsedText():
    """
    A conll formatted text file that is seperated into align segments 

    - inputfile: the filename of the source (= the code of the file)
    - status: source or target
    - language: a two-letter language code
    - pair_id: the unique identifier of the document

    """

    def __init__(self, inputfile, status, language, pair_id):
        #Read the data from the file and save it in a list called 'alignsegments'
        self.inputfile = '/tmp/texthammerparsing/{}/parsed/{}/{}'.format(pair_id, language, inputfile)
        self.code = inputfile
        self.status = status
        self.language = language
        self.haserrors = False
        try:
            with open(self.inputfile, 'r') as f:
                raw = f.read()
            #Removing all irrelevant comment lines
            conllinput = "\n".join([line 
                    for line in raw.splitlines() 
                    if not re.search("^#", line) or re.search("^# [a-z]+split", line)])
        except UnicodeDecodeError:
            msg = "Encoding error! Id of the text: {}\n ".format(code)
            logging.info(msg)
            #Logger.loggederrors.append(msg)
            self.haserrors = True
        if not self.haserrors:
            #This is only needed for multilingual aligned files
            self.alignsegments = TrimList(re.split("# " + getConf("segmentsplit"), conllinput))
            #This is still experimental in june 2016:
            #self.paragraphs = TrimList(re.split(getConf("segmentsplit"), conllinput))
            ##This is only needed for monolingual files
            #self.sentences = TrimList(re.split(self.sentencesplitpattern, conllinput))


    def CollectTokenProperties(self, columns):
        """Collect the data about a single word and give it reasonable labels"""
        if len(columns)  < 7:
            #If an empty segment encountered
            print('Note: an empty segment encountered')
            return {'align_id' : '', 'sentence_id' : '', 'text_id' : '',  'tokenid' : 1, 'token' : 'EMPTYSEGMENT', 'lemma' : 'EMPTYSEGMENT', 'pos' : 'EMPTYSEGMENT', 'feat' : 'EMPTYSEGMENT', 'head' : 0, 'deprel' : 'EMPTY'}
        else:
            return  {'tokenid'     : columns[0],
                    'token'       : columns[1],
                    'lemma'       : columns[2],
                    'pos'         : columns[3],
                    'feat'        : columns[5],
                    'head'        : columns[6],
                    'deprel'      : columns[7]}

def ReadFiledata(csvpath):
    """Read information about the files to be converted from a csv file. 
    Create File pair objects based on the information provided by the csv file."""
    pair_ids = list()
    textpairs = list()
    with open(csvpath, "r") as f:
        texts = json.load(f)
    for pair_id, text in texts.items():
        failedpairs = list()
        for version in text:
            if pair_id not in failedpairs:
                #Separate text pairs by user-defined ids
                #Assume that the first text with a given ID is the source text
                if pair_id not in pair_ids:
                    pair_ids.append(pair_id)
                    textpairs.append(TextPair(version, pair_id))
                else:
                    #For the target language files
                    textpairs[-1].tl_texts.append(ParsedText(version['filename'], 'target', version['lang'], version['code']))
                    if textpairs[-1].sl_text.haserrors or textpairs[-1].tl_texts[-1].haserrors:
                        #check if errors in reading the data to sl and tl text objects
                        failedpairs.append(pair_id)
                        del textpairs[-1]
                #Add a tag for the metadata
                textpairs[-1].FormatMetaData(version)
    return textpairs

class Logger():

    loggederrors = list()

    def __init__(self, fname = "conll_to_xml.log"):
        """Start a logger"""
        with open(fname,"w") as f:
            f.write("")
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s ---> %(asctime)s: %(message)s')

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)

        fh = logging.FileHandler(fname)
        fh.setLevel(logging.DEBUG)

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        root.addHandler(fh)
        root.addHandler(ch)
        logging.info('Writing LOG to {}'.format(fname))



#==================================================


def main(csvdata):
    """The actual script for making the xml"""
    thislogger = Logger()
    textpairs = ReadFiledata(csvdata)

    for textpair in textpairs:
        if textpair.tl_texts:
            #If the text is an aligned multilingual text
            pairok = textpair.LoopThroughSegments()
        else:
            #if the text is a monolingual text
            pairok = textpair.LoopThroughSentences()

        if pairok:
            textpair.WriteXml()
        else:
            msg = "PROBLEMS with the text {}. Skipping!".format(textpair.sl_text.code)
            logging.info(msg)
            Logger.loggederrors.append(msg)

    if Logger.loggederrors:
        print("The following ERRORS occured: \n" + "\n".join(Logger.loggederrors))


if __name__ == "__main__":
    try:
        if os.path.isfile(sys.argv[1]):

            if len(sys.argv)>2:
                #The second cl argument gives information about the parser that has been used
                ParserInfo.parsername = sys.argv[2]

            main(sys.argv[1]) 
            
        else:
            print('The path {} is not a valid filename'.format(sys.argv[1]))
    except IndexError:
        raise ArgumentError('Usage: {} <path to the csv file containing metadata and file paths> [optional: parser name]'.format(sys.argv[0]))
