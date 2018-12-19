import sys

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

    return args

#def requireArg(arg):
#    if not arg:
#        print("The following option must be specified in order to continue with this action: " + )
#        sys.exit(0)
