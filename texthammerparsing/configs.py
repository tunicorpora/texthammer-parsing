import sys
import os.path
import yaml


#TODO: read rcfiles
def getConf(key):
    """
    Returns the value of an individual config parameter

    - key: the name of the key in the config dict
    """

    config = {
                "segmentsplit" :  "segmentsplit",
                "paragraphsplit" : "paragraphsplit",
                "sentencesplit" : "sentencesplit",
                "models": {
                        "fi" : "models_fi_tdt",
                        "ru" : "models_ru_syntagrus",
                        "en" : "models_en_ewt",
                        "fr" : "models_fr_gsd",
                        "sv" : "models_sv_talbanken",
                        "de" : "models_de_gsd",
                        "es" : "models_es_ancora",
                        }
            }

    yamldata = checkDefaults(None, True)
    if yamldata:
        if "models" in yamldata:
            for lang, model in yamldata["models"].items():
                config["models"][lang] = "models_" + model
        for thiskey in ["segmentsplit", "paragraphsplit","sentencesplit"]:
            if thiskey in yamldata:
                config[thiskey] = yamldata[thiskey]

    return config[key]

def checkDefaults(args, getYaml=False):
    """
    Returns the value of an individual config parameter

    - args: argparser argument object

    """
    config = {}
    fnames = [os.path.expanduser("~/.config/texthammerparsing.yaml"),
            os.path.expanduser("~/.config/texthammerparsing.yml")]
    if hasattr(args, 'conf'):
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
        if getYaml:
            return config
        for key, item in config.items():
            if key not in ["models"]:
                if not getattr(args, key):
                    setattr(args, key, item)

    return args

#def requireArg(arg):
#    if not arg:
#        print("The following option must be specified in order to continue with this action: " + )
#        sys.exit(0)
