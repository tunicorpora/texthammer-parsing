#!/usr/bin/python3
import argparse
import logging
import os.path
import datetime
import sys
import shutil
import progressbar
from texthammerparsing import getFiles, prepareTmx, parseFiles, checkDefaults, getPairIds, convertFiles


def main():
    #TODO: rcfile with default folder location
    parser = argparse.ArgumentParser(description='Programmatically runs dependency parsers and outputs to texthammer xml')
    parser.add_argument('action', 
            metavar = 'action',
            nargs = '?',
            default = 'run',
            choices = ["run","prepare", "get_xml", "parse", "version"], help="The action to run")
    parser.add_argument('--input',  '-i',
            metavar = 'inputfiles',
            nargs = "*",
            help="Path to the folder containing the input files")
    parser.add_argument('--output',  '-o',
            metavar = 'outputfolder',
            help="Path to the desired destination folder")
    parser.add_argument('--id', 
            metavar = 'ids',
            default = [],
            nargs = "*", help="The ids of the input files to be processed. These are produced by the 'prepare' action of this program")
    parser.add_argument('--output_ids', 
            metavar = 'filename or path',
            help="A temporary file for the ids to be stored in")
    parser.add_argument('--parserpath', 
            metavar = 'path',
            help="absolute path to the folder containing the parser")
    parser.add_argument('--cleanup', 
            metavar = '',
            nargs = "?",
            const = True,
            default = False,
            help="Weather or not to clean the /tmp/texthammerparsing/ folder")

    #Check the rc file for defaults
    args = checkDefaults(parser.parse_args())

    logfile = "/tmp/texthammerparsing_log_"  + str(datetime.datetime.now()).replace(" ","_").replace(":","-")
    logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s')
    print("Starting.\nIn case of problems take a look at the logfile at " + logfile + "\n"*2)

    if args.action in ["run", "prepare"]:
        if not args.input:
            print("Please specify the files to parse or the folder containing the files using the --input option")
            sys.exit(0)
        files = getFiles(args.input)
        for f in files:
            if ".tmx" in f:
                success = prepareTmx(f)
                if success:
                    args.id.append(success)
                else:
                    print("Preparation failed for " + f)
            else:
                pass
                #monolings?

    if args.output_ids and args.id:
        with open(args.output_ids, "w") as f:
            f.write("\n".join(args.id))

    if args.id:
        if os.path.isfile(args.id[0]):
            #ids can be supplied via a file
            with open(args.id[0], "r") as f:
                args.id = f.read().splitlines()

    if args.action in ["parse", "get_xml", "run"] and not args.id:
        args.id = getPairIds()
        if not args.id:
            print("Please specify the ids of the prepared files with the --id option")
            sys.exit(0)

    if args.action in ["run", "parse"]:
        if not args.parserpath:
            print("Please specify the location of the parser with the --parserpath option")
            sys.exit(0)
        for this_id in args.id:
            parseFiles(this_id, args.parserpath)

    if args.action in ["run", "get_xml"]:
        for this_id in args.id:
            if os.path.isdir("/tmp/texthammerparsing/{}/parsed".format(this_id)):
                convertFiles(this_id, args.output)

    if args.cleanup:
        shutil.rmtree("/tmp/texthammerparsing/", ignore_errors=True)



if __name__ == '__main__':
    main()



