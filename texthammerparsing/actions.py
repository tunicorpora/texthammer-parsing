import os
import glob
import subprocess
from texthammerparsing import Tmxfile, TextPair

def getPairIds():
    """
    Finds all the processed files in /tmp/texthammerparsing

    """

    ids = [  ]
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
        dirname = files[0] if files[0][-1] == "/"  else files[0] + "/"
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
    finally:
        pass
        #do some cleaning up...?

    if thisfile:
        return thisfile.pair_id

def parseFiles(pair_id, parserpath):
    """
    Sends all the language files in the document identified by pair_id to the parser
    and captures the output

    - pair_id the unique id of a source file
    - parserpath path to the Turku neural parser installation

    """

    #TODO: select which model if multiple available (rcfile?)

    if parserpath[-1] != r"/":
        parserpath += r"/"

    models = {
            "fi" : "models_fi_tdt",
            "ru" : "models_ru_syntagrus"
            }
    # Use the parser's virtual env
    python_bin = parserpath + "venv-parser-neural/bin/python3"
    script_file = parserpath + "full_pipeline_stream.py"
    parsed_dir = "/tmp/texthammerparsing/{}/parsed".format(pair_id)
    os.makedirs(parsed_dir, exist_ok=True)
    prepared_dir = "/tmp/texthammerparsing/" + pair_id + "/prepared/"

    for lang in os.listdir(prepared_dir):
        lang = lang.replace(r"/","")
        langdir = parsed_dir + "/" + lang 
        os.makedirs(langdir, exist_ok=True)
        for f in glob.glob(prepared_dir + lang + "/*"):
            p1 = subprocess.Popen(["cat", f], stdout=subprocess.PIPE)
            output = subprocess.check_output([python_bin, script_file, 
                "--conf", parserpath + models[lang] + "/pipelines.yaml", 
                "--pipeline", "parse_plaintext"], stdin=p1.stdout, cwd=parserpath)
            with open(parsed_dir + "/" + lang + "/" + os.path.basename(f), "w") as f:
                f.write(output.decode("utf-8"))


def convertFiles(pair_id, outputpath=""):
    """
    Converts the prepared and parsed files to texthammer's xml format

    - pair_id the unique id of a source file
    - outputpath were to output the xml

    """

    pair = TextPair(pair_id)
    pair.LoopThroughSegments()
    pair.WriteXml(outputpath)



