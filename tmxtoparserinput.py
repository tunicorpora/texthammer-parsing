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


def ReadXml(sourcefile):
    with open(sourcefile, "r") as f:
        try:
            xmlstring = f.read()
        except UnicodeDecodeError:
            print("Tiedostossa {} koodausongelma. luultavasti utf-16 pitäisi muuttaa utf-8:aan.".format(sourcefile))
            sys.exit()
    xmlstring = unescape(xmlstring.replace('encoding="utf-8"',''),{"&apos;":"'","&quot;":"\""})
   # with open ("text.tmx","w") as f:
   #     f.write(xmlstring)
   # print(xmlstring)
    xmlstring = Prettify(xmlstring.replace('encoding = "utf-8"','').strip())
    xmlstring = FilterLongSentences.FilterByCharCount(xmlstring, sourcefile)
    root = etree.fromstring(xmlstring.strip())
    return root

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

def CountMetaAttributes(root, attrs):
    """Count all the possible different metadata 
    attributes included in the tmx files provided"""

    texts = root.xpath("//textdef")
    for text in texts:
        for attrname, attr in text.items():
            #Always use the lang tag instead of language
            if attrname == 'language':
                attrname = 'lang'
            if attrname not in attrs:
                attrs.append(attrname)
    return attrs

def ReadMetaData(root, attrs):
    """Read metadata from textdef tags included in the tmx"""
    texts = root.xpath("//textdef")
    #Save metadata from textdef tags to a dict
    languagetexts = list()
    #separete texts with uinique ids
    pair_id = uuid.uuid4()
    for text in texts:
        languagetexts.append(dict())
        for attrname, attr in text.items():
            if attrname == 'language':
                attrname = 'lang'
            if attrname == 'code':
                #Make sure the code tag does not contain spaces (because it will be used as a part of a filename)
                attr = attr.replace(' ','')
            if attrname == 'lang':
                #Force lower case language codes to make sure file names will be correct
                attr = attr.lower()
            languagetexts[-1][attrname] = attr
            languagetexts[-1]["pair_id"] = pair_id


    #For source texts lacking the translator attribute or other attributes found in only some textdef tags or files
    for languagetext in languagetexts:
        for attr in attrs:
            if not attr in languagetext:
                languagetext[attr]= ""

    return languagetexts

def WriteMetaData(metadata):
    """Write the information about the parsed files to a csv file"""
    with open('parsedmetadata.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=metadata[0].keys())
        writer.writeheader()
        for text in metadata:
            writer.writerow(text)

def ReadTmxData(sourcefile, attrs):
    """Read the contents of a tmx file"""
    root = ReadXml(sourcefile)
    #find out what languages involved and what are the metadata
    metadata = ReadMetaData(root, attrs)
    #Create a dictionary for saving additional information about the segments (such as speakers)
    segment_meta = dict()
    #check if there are multiple translations to one language
    textsperlanguage = TestIfRetrans(metadata)
    #Loop through each language in the tmx
    seglength = dict()
    seglengths = list()
    for idx, text in enumerate(metadata):
        if textsperlanguage[text["lang"]]==1:
            #if no retranslations
            xpathq = "//tuv[@xml:lang='{}' or  @xml:lang='{}']".format(text["lang"], text["lang"].upper())
        else:
            #if retranslations present
            xpathq = "//tuv[(@xml:lang='{}' or @xml:lang='{}') and @code='{}']".format(text["lang"],text["lang"].upper(), text["code"])
        tuvs = root.xpath(xpathq)
        print("{}:{} segments".format(text["lang"],len(tuvs)))
        #Initialize a list for saving the possible metadata about each segment
        segment_meta[text["lang"]] = list()
        #--
        seglength[text["lang"]] = len(tuvs)
        seglengths.append(len(tuvs))
        preparedinput = ""
        if not tuvs:
            #If nothing found, inform the user
            input('Warning! The preparing script returned an empty string for text {} in the file {} (language:{}). Press Ctr-c to cancel.'.format(text["code"], sourcefile,text["lang"]))
        else:
            #if all went well, loop through each align segment
            for tuv in tuvs:
                preparedinput += "\n" + "!"*15 + "\n"
                #Check for additional metadata such as information about the current speaker
                segment_meta[text["lang"]].append({"speaker":tuv.get("speaker")})
                #then, each segment inside
                if not tuv.getchildren():
                    preparedinput += FixQuotes(tuv.text)
                else:
                    for seg in tuv.getchildren():
                        preparedinput += " "
                        if seg.text:
                            preparedinput += FixQuotes(seg.text)
            filename = '{}_{}_{}.prepared'.format(sourcefile,text["code"],text["lang"])
            #Write the prepared file
            with open(filename, 'w') as f:
                f.write(preparedinput.strip())
            #Save the filename of the file after parsing in the dict for future use
            k = sourcefile.rfind("/")
            mere_file = sourcefile[k+1:]
            text["filename"] = '{}/{}/{}_{}_{}.prepared.conll'.format(sys.argv[2],text["lang"],mere_file,text["code"],text["lang"])
    #Check that all the texts have the same number of segents
    lengths = list()
    halt = False
    segnumbers = ""
    for lang, thislength in seglength.items():
        segnumbers += "{}: {} / ".format(lang, thislength)
        for l in seglengths:
            if l != thislength:
                halt = True
                break
    if halt:
        raise ValueError("Different number of segments in this file:\n\n {}".format(segnumbers))

    # Finally, save the collected metadata about segments to a separate json dump
    metafile = "{}/{}/{}.json".format(os.path.dirname(os.path.abspath(__file__)), "auxiliary_files", mere_file)
    with open(metafile,"w") as f:
        json.dump(segment_meta, f, ensure_ascii=False)

    return metadata

def TestIfRetrans(metadata):
    """test if the specified language is used in multiple textdef tags"""
    translations_per_language = dict()
    for text in metadata:
        try:
            translations_per_language[text["lang"]] += 1
        except KeyError:
            translations_per_language[text["lang"]] = 1
    return translations_per_language

def main():
    try:
        sourcefile = sys.argv[1]
        parsedfolder = sys.argv[2]
        if sys.argv[2][-1] == "/":
            sys.argv[2] = sys.argv[2][:-1]
    except:
        print('Usage: {} <path to source tmx or folder containing multiple tmxs> <folder to save the parsed files>'.format(sys.argv[0]))
        sys.exit(0)

    attrnames = list()
    thislogger = Logger("tmxtoparserinput.log")

    if os.path.isdir(sourcefile):
        metadata = list()
        if sourcefile[-1] == "/":
            slash = ""
        else:
            slash = "/"

        #Get all the attributes in the metadata
        shall_i_proceed = {}
        for filename in glob.glob(sourcefile + slash + '*tmx'):
            logging.info("Starting to analyze the following tmx file: {}.".format(filename))
            try:
                root = ReadXml(filename)
                attrnames = CountMetaAttributes(root, attrnames)
                shall_i_proceed[filename] = True
            except Exception as e:
                logging.warning("Cannot read the XML in {}. This file won't be processed. The exact error message is: {}".format(filename, e))
                shall_i_proceed[filename] = False

        #Process the tmxs
        for filename in glob.glob(sourcefile + slash + '*tmx'):
            if shall_i_proceed[filename]:
                try:
                    if not metadata:
                        metadata = ReadTmxData(filename, attrnames)
                    else:
                        metadata.extend(ReadTmxData(filename, attrnames))
                except ValueError as e:
                    logging.error("Error with {}: \n{}. This file won't be processed.".format(filename, e))

    else:
        #No folder, a single file given
        root = ReadXml(sourcefile)
        attrnames = CountMetaAttributes(root, attrnames)
        metadata = ReadTmxData(sourcefile, attrnames)
    WriteMetaData(metadata)


if __name__ == "__main__":
    main()
