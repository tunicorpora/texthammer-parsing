#!/usr/bin/python3
import argparse
import logging
import os.path
import sys
import shutil
import progressbar
from texthammerparsing import getFiles, prepareTmx, parseFiles


def main():
    #TODO: rcfile with default folder location
    parser = argparse.ArgumentParser(description='Programmatically runs dependency parsers and outputs to texthammer xml')
    parser.add_argument('action', 
            metavar = 'action',
            choices = ["prepare", "get_xml", "parse"], help="The action to run")
    parser.add_argument('--input',  '-i',
            metavar = 'inputfiles',
            nargs = "*",
            help="Path to the folder containing the input files")
    parser.add_argument('--id', 
            metavar = 'ids',
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
    args = parser.parse_args()

    ids = []

    if args.action == "prepare":
        files = getFiles(args.input)
        for f in files:
            if ".tmx" in f:
                ids.append(prepareTmx(f))
            else:
                pass
                #monolings?

    if args.output_ids:
        with open(args.output_ids, "w") as f:
            f.write("\n".join(ids))


    if args.action == "parse":
        if not args.id:
            print("Please specify the ids of the prepared files with the --id option")
            sys.exit(0)

        # TODO: .rcfile
        parserpath = args.parserpath

        if not parserpath:
            print("Please specify the location of the parser with the --parserpath option")
            sys.exit(0)

        if os.path.isfile(args.id[0]):
            #ids can be supplied via a file
            with open(args.id[0], "r") as f:
                ids = f.read().splitlines()
        else:
            ids = args.id

        for this_id in ids:
            parseFiles(this_id, parserpath)

    if args.action == "get_xml":
        for pair_id in args.id:
            fname = "/tmp/texthammerparsing/" + pair_id + "/parsed/"


    if args.cleanup:
        shutil.rmtree("/tmp/texthammerparsing/", ignore_errors=True)


    print("Ids: \n" + "\n".join(ids))



if __name__ == '__main__':
    main()



