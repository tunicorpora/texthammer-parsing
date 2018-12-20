TEXTMINE-PARSING
================


This project contains the utilities needed to parse multilingual tmx files and convert them
to xml files with syntactic and morphological annotations. These xml files are intended to be used 
in the Texthammer or [Nexthammer](https://github.com/hrmJ/nexthammer) corpus projects.

The current version of the project has moved to using the new multilingual
Universal Dependencies -based [Turku neural parser](https://turkunlp.github.io/Turku-neural-parser-pipeline/),
which significantly simplifies and unifies the process of creating unified output. 
To examine the old version using several different parsers check out the
"dev" branch of this repository.


Installation
------------

### Prerequisites

The Turku neural parser mentioned above is a pre-requisite and we refer to the
excellent and easy-to-follow installation instructions at the project's
website.

### Installing using pip

The software has been built and tested on Ubuntu 18.04, but any linux platform
supporting python3 should be ok.
First, make sure you have pip3 installed (`sudo apt install python3-pip`)
and then install the project directly from github:

```
pip3 install git+https://github.com/tunicorpora/texthammer-parsing
```

Usage
-----

### Quick start

### Defining metadata

The documents sent to parsers through this script can contain xml tags at the beginning
of each file specifying the metadata related to the documents. The format of the 
tag is as follows:

```
<textdef code="FI_RF_consular_fi" title="Sopimus" subject="consular_real_estate" yearorig="2017" yeartr="2017" lang="fi" />
```

When using tmx input, such tags should be specified for each language / version
individually, for instance in the following way:

```
<textdef code="FI_RF_consular_fi" title="Sopimus" subject="consular_real_estate" yearorig="2017" yeartr="2017" lang="fi" />
<textdef code="FI_RF_consular_ru" title="Соглашение" subject="consular_real_estate" yearorig="2017" yeartr="2017" lang="ru" />
```

Each version / language must have a unique `code` attribute.

#### Parsing tmx

In order to parse a tmx file, run the program with the arguments 
`--input` and `--parserpath`. The former can be a list of tmx files
or a folder containing those files. The latter is the installation
folder of the turku neural parser.

Example:

```

texthammerparsing --input examples/tmx/ru_fi_short.tmx --parserpath ~/Turku-neural-parser-pipeline/

```

By default this will output the final xml file to `/tmp/texthammerparsing/[id]/xml` where `[id]`
is a unique id the program will generate for each tmx file. You can change this
behaviour and put all the output files to your desired location by using the `--output` option,
e.g. as follows:

```

texthammerparsing --input examples/tmx/ru_fi_short.tmx --parserpath ~/Turku-neural-parser-pipeline/ --output ~/texthammer_xml

```

Be default, the script cleans up the temporary files related to preparing the texts for parsers
etc. If you wish to  keep thees files,  add the `--keepfiles` option to the command, e.g.


```

texthammerparsing --input examples/tmx/ru_fi_short.tmx --parserpath ~/Turku-neural-parser-pipeline/ --output ~/texthammer_xml --keepfiles

```

All this can also be specified in a separate configuration file. This should
be a `yaml` file located at `~/.config/` and named `texthammerparsing.yaml`, i.e.
`~/.config/texthammerparsing.yaml`. Below is a short example configuration:

```yaml

- parserpath: ~/parserit/Turku-neural-parser-pipeline
- output: ~/texthammer_xml
- input: ~/corpusinput/tmx

```

Note, that anything specified explicitly as command line options will override
the default configuration. The configuration file can also be specified via
the `--conf` option, e.g.

```

texthammerparsing --input examples/tmx/ru_fi_short.tmx --conf myconf.yaml

```

#### Parsing monolingual files

The program can also be used for parsing regular text files containing 
material only in one language. For these kinds of files, 
it should be noted, that the program tries to mark paragraphs so that
it interprets each line to contain one paragraph.

In order to run this script on monolingual files, no special action is needed,
just run it as you would run it with tmx, e.g.:

```
texthammerparsing --input examples/fi/example.txt --parserpath ~/Turku-neural-parser-pipeline/
```

Note, that for monolingual files it is not obligatory to have `textdef` tags at
the beginning of each file. If the program cannot find those tags, it will,
however, prompt the user for the language of each document.

If you would rather not have the program try to mark the paragraphs, you
can use the `--nopara` option:

```
texthammerparsing --input examples/fi/example.txt --parserpath ~/Turku-neural-parser-pipeline/
```

### Individual actions

The command takes one mandatory argument, `action`, which 
by default is set to `run`.  This runs the full pipeline from
file preparation to xml output but, if needed, the job
can be split to substeps described below. The substeps
can be launched by specifying the following actions:

#### prepare

- separates each language from the tmx and stores possible metadata 
- use the `--input` option to specify the folder containing the files
- Example:

```
#Each file separately...
texthammerparsing prepare --input myfolder/myfile.tmx myfolder_b/myfile.tmx

#...or a folder
texthammerparsing prepare --input myfolder
```

#### parse

- Sends the prepared files (specified by ids) to the parser
- use the `--id` option to specify the ids of the prepared files (if left out, all the prepared files located at /tmp/texthammerparsing/ will be processed)
- use the `--parserpath` option to specify the folder containing the parser
- Example:

```bash
#With the id specified (useful for debugging a single file)
texthammerparsing parse --parserpath ~/parsers/Turku-neural-parser --id 09348021349lk4j-234lk234934
#Without the id (will parse everything found at /tmp/texthammerparsing)
texthammerparsing parse --parserpath ~/parsers/Turku-neural-parser 
```


#### get_xml

- combines the parsed files into a single xml file
- use the `--id` option to specify the ids of the prepared files (if left out, all the parsed files located at /tmp/texthammerparsing/ will be processed)

```
#With the id specified (useful for debugging a single file)
texthammerparsing get_xml --id 09348021349lk4j-234lk234934
#Without the id (will convert everything found at /tmp/texthammerparsing)
texthammerparsing get_xml 
```






