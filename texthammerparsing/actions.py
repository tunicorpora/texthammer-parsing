import os
import logging
import glob
import subprocess
from texthammerparsing import Tmxfile, TextPair, Txtfile
from texthammerparsing.configs import getConf
import requests


def getPairIds():
    """
    Finds all the processed files in /tmp/texthammerparsing

    """

    ids = []
    for fname in glob.glob("/tmp/texthammerparsing/*"):
        if os.path.isdir(fname):
            ids.append(os.path.basename(fname))
    return ids


def getFiles(files):
    """
    Parses the list of files specified by the user

    - a list of files or a string representing the path to the folder containing the files
    """

    ofiles = []
    if len(files) == 1 and os.path.isdir(files[0]):
        dirname = files[0] if files[0][-1] == "/" else files[0] + "/"
        for fname in glob.glob(dirname + "*.*"):
            ofiles.append(fname)
    else:
        ofiles = files

    return ofiles


def prepareTmx(filename):
    """
    Prepares  tmx files for parsing

    - filename the name of the tmx file
    - returns the id of the file
    """

    thisfile = Tmxfile(filename)
    try:
        thisfile.GetXml()
        thisfile.ReadTextdefs()
        thisfile.CollectMetaDataAttributes()
        thisfile.InitializeVersions()
        thisfile.GetVersionContents()
        if not thisfile.ReportProblems():
            thisfile.WritePreparedFiles()
    except Exception as e:
        thisfile.ReportProblems(e)
        print("Problems in preparing " + filename + ". Check out the log file at " +
              logging.getLoggerClass().root.handlers[0].baseFilename)
    finally:
        pass
        # do some cleaning up...?

    if thisfile:
        if not thisfile.errors:
            return thisfile.pair_id


def prepareTxt(filename, nopara):
    """
    Prepares  txt files for parsing

    - nopara: if set, will not try to mark paragraphs
    - filename: the name of the txt file
    - returns the id of the file
    """

    thisfile = Txtfile(filename)
    try:
        thisfile.ReadTextdefs()
        thisfile.CheckIfHardWrap()
        thisfile.CollectMetaDataAttributes()
        thisfile.MarkParagraphs(nopara)
        thisfile.FilterSentencesAndParagraphs(nopara)
        if not thisfile.ReportProblems():
            thisfile.WritePreparedFiles()
    except Exception as e:
        thisfile.ReportProblems(e)
        print("Problems in preparing " + filename + ". Check out the log file at " +
              logging.getLoggerClass().root.handlers[0].baseFilename)
    finally:
        pass
        # do some cleaning up...?

    if thisfile:
        if not thisfile.errors:
            return thisfile.pair_id


def addCodes(filename, lang):
    thisfile = Tmxfile(filename)
    thisfile.GetXml()
    thisfile.ReadTextdefs()
    thisfile.CollectMetaDataAttributes()
    thisfile.InitializeVersions()
    thisfile.AddCodes(lang, filename)


def getPortForLanguage(lang):
    ports = getConf('ports')
    return ports[lang]


def parseFiles(pair_id, parserpath):
    """
    Sends all the language files in the document identified by pair_id to the parser
    and captures the output

    - pair_id the unique id of a source file
    - parserpath path to the Turku neural parser installation

    """

    if parserpath[-1] != r"/":
        parserpath += r"/"

    # TODO: select which model if multiple available (rcfile?)
    models = getConf("models")

    # Use the parser's virtual env
    python_bin = parserpath + "venv-parser-neural/bin/python3"
    script_file = parserpath + "full_pipeline_stream.py"
    parsed_dir = "/tmp/texthammerparsing/{}/parsed".format(pair_id)
    log_dir = "/tmp/texthammerparsing/parserlog/"
    os.makedirs(parsed_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    prepared_dir = "/tmp/texthammerparsing/" + pair_id + "/prepared/"

    for lang in os.listdir(prepared_dir):
        lang = lang.replace(r"/", "")
        langdir = parsed_dir + "/" + lang
        os.makedirs(langdir, exist_ok=True)
        logging.info(
            "Starting to parse the files in the following language: " + lang)
        for f in glob.glob(prepared_dir + lang + "/*"):
            code = os.path.basename(f)
            logging.info("Starting to parse the following file: " + code)

            with open(f, 'rb') as payload:
                headers = {'content-type': 'text/plain; charset = utf-8'}
                output = requests.post('http://localhost:{}'.format(getPortForLanguage(lang)),
                                       data=payload, verify=False, headers=headers)

            with open(parsed_dir + "/" + lang + "/" + code, "w") as f:
                f.write(output.decode("utf-8"))


def convertFiles(pair_id, outputpath="", nopara=None):
    """
    Converts the prepared and parsed files to texthammer's xml format

    - pair_id the unique id of a source file
    - outputpath were to output the xml

    """

    pair = TextPair(pair_id)
    if pair.tl_texts:
        pair.LoopThroughSegments()
    else:
        pair.LoopThroughSentences(nopara)
    pair.WriteXml(outputpath)
