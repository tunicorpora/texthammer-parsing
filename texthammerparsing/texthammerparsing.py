#!/usr/bin/python3
import argparse
import logging
import os.path
import datetime
import glob
import sys
import shutil
import progressbar
from texthammerparsing import getFiles, prepareTmx, parseFiles, checkDefaults, getPairIds, convertFiles, prepareTxt, addCodes
from texthammerparsing.python_tools import printHeading
from termcolor import colored


def main():
    # TODO: rcfile with default folder location
    parser = argparse.ArgumentParser(
        description='Programmatically runs dependency parsers and outputs to texthammer xml')
    parser.add_argument('action',
                        metavar='action',
                        nargs='?',
                        default='run',
                        choices=["run", "prepare", "get_xml", "parse", "version", "addcodes"], help="The action to run")
    parser.add_argument('--input',  '-i',
                        metavar='inputfiles',
                        nargs="*",
                        help="Path to the folder containing the input files")
    parser.add_argument('--lang',  '-l',
                        metavar='language',
                        nargs="?",
                        help="specify the language used in a utility operation (e.g. addcodes)")
    parser.add_argument('--port',  '-ports',
                        metavar='ports',
                        nargs="?",
                        help="which parser port is listening for this language")
    parser.add_argument('--output',  '-o',
                        metavar='outputfolder',
                        help="Path to the desired destination folder")
    parser.add_argument('--id',
                        metavar='ids',
                        default=[],
                        nargs="*", help="The ids of the input files to be processed. These are produced by the 'prepare' action of this program")
    parser.add_argument('--parserpath',
                        metavar='path',
                        help="Path to the folder containing the parser")
    parser.add_argument('--conf',
                        metavar='file',
                        help="a yaml configuration file")
    parser.add_argument('--nopara',
                        metavar='',
                        nargs="?",
                        const=True,
                        help="if set, the program will not try ti mark paragraphs for monolingual files")
#    parser.add_argument('--filetype',
#            metavar = 'file ending',
#            help="Restrict the input files to a certain file type only (eg. tmx / txt)")
    parser.add_argument('--keepfiles',
                        metavar='',
                        nargs="?",
                        const=True,
                        default=False,
                        help="Whether or not to keep the temporary files at /tmp/texthammerparsing/[id]")

    # Check the rc file for defaults
    args = checkDefaults(parser.parse_args())

    if args.action == 'addcodes':
        if not args.lang:
            print(colored("Please specify a language code", "red"))
            sys.exit(0)
        files = getFiles(args.input)
        for f in files:
            addCodes(f, args.lang)
        sys.exit(0)

    os.makedirs("/tmp/texthammerparsing/", exist_ok=True)
    logfile = "/tmp/texthammerparsing/log_" + \
        str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")
    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(asctime)s %(message)s')
    print("Starting.\nVisit https://github.com/utacorpora/texthammer-parsing  or run texthammerparsing --help to get more instructions.")
    print("Writing Logfile at " + logfile)

    if args.action in ["run", "prepare"]:
        printHeading("Preparing files")
        if not args.input:
            print(colored(
                "Please specify the files to parse or the folder containing the files using the --input option", "red"))
            sys.exit(0)
        files = getFiles(args.input)
        for f in files:
            success = False
            if ".tmx" in f:
                success = prepareTmx(f)
            else:
                success = prepareTxt(f, args.nopara)
            if success:
                args.id.append(success)
            else:
                print(colored("Preparation failed for " + f, "red"))
        if args.id:
            print("Prepared {} files to /tmp/texthammerparsing".format(len(args.id)))

    if args.id:
        if args.action in ["run", "parse"]:
            printHeading("Parsing files")
            print("This is going to take time.")
            print("Look at the log files at /tmp/texthammerparsing/parserlog (hint: use tail -f for realtime updates).")
            print("For less verbose output check out " + logfile)
            if not args.parserpath:
                print(colored(
                    "Please specify the location of the parser with the --parserpath option", "red"))
                sys.exit(0)
            for this_id in progressbar.progressbar(args.id):
                parseFiles(this_id, args.parserpath)
    if args.id:
        if args.action in ["run", "get_xml"]:
            printHeading("Outputting xml")
            for this_id in args.id:
                if os.path.isdir("/tmp/texthammerparsing/{}/parsed".format(this_id)):
                    convertFiles(this_id, args.output, args.nopara)

    if not args.keepfiles:
        # Default: clean up the temporary files when finished
        for folder in glob.glob("/tmp/texthammerparsing/*"):
            if os.path.isdir(folder) and os.path.basename(folder) in args.id:
                shutil.rmtree(folder, ignore_errors=True)


if __name__ == '__main__':
    main()
