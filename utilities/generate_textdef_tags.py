#!/usr/bin/python3
"""
The idea of this small utility script is to generate minimal textdef tags for
monolingual txt files, so that the bulk parsing script
(parse_and_convert_monoling.sh) can be used for quick parsing tasks


Usage (if execution permission given) : ./generate_textdef_tags.py <path_to_folder_with_files> <lang_of_the_files>

"""
import sys
import glob
import uuid
import os.path

def AddTextDef(path):
    """
    Prepends a textdef tag to a textfile

    - path: absolute path to the file th
    """
    with open(path,"r") as f:
        contents = f.read()
    textdef = "<textdef lang='{lang}' code='{code}' />".format(
         **{
             "lang": sys.argv[2],
             "code": str(uuid.uuid4())    
         }
        )

    if "textdef" not in contents:

        with open(path,"w") as f:
            f.write("{}\n\n{}".format(textdef, contents))



if __name__ == "__main__":

    for thisfile in glob.glob(os.path.join(sys.argv[1], "*.txt")):
        try:
            AddTextDef(thisfile)
        except Exception as e:
            print(e);

