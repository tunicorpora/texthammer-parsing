#!/usr/bin/python3
import argparse
import logging
import os.path
import glob

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


def main():
    #TODO: rcfile with default folder location
    parser = argparse.ArgumentParser(description='Programmatically runs dependency parsers and outputs to texthammer xml')
    parser.add_argument('action', 
            metavar = 'action',
            choices = ["prepare"], help="The action to run")
    parser.add_argument('--input',  '-i',
            metavar = 'inputfiles',
            nargs = "*",
            help="Path to the folder containing the input files")
    args = parser.parse_args()

    if args.action == "prepare":
        files = getFiles(args.input)
        print(files)



if __name__ == '__main__':
    main()
