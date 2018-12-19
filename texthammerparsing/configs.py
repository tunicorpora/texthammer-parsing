import sys
import os.path
import yaml

#TODO: read rcfiles
def getConf(key):
    """
    Returns the value of an individual config parameter

    - key: the name of the key in the config dict
    """
    rcfile = False
    if not rcfile:
        config = {
                    "segmentsplit" :  "segmentsplit",
                    "paragraphsplit" : "paragraphsplit",
                    "sentencesplit" : "sentencesplit"
                }

    return config[key]

def checkDefaults(args):
    """
    Returns the value of an individual config parameter

    - args: argparser argument object

    """
    config = {}
    fnames = [os.path.expanduser("~/.config/texthammerparsing.yaml"),
            os.path.expanduser("~/.config/texthammerparsing.yml")]
    if args.conf:
        fnames = [args.conf]
    for fname in fnames:
        if os.path.isfile(fname):
            with open(fname, "r") as f:
                raw = f.read()
            yamlconfig = yaml.load(raw)
            for item in yamlconfig:
                if not config:
                    config = item
                else:
                    config.update(item)
            break
    if config:
        for key, item in config.items():
            if not getattr(args, key):
                setattr(args, key, item)
    print(args)


    return args

#def requireArg(arg):
#    if not arg:
#        print("The following option must be specified in order to continue with this action: " + )
#        sys.exit(0)
