TEXTMINE-PARSING
================


This project contains the utilities needed to parse multilingual tmx-files and convert them
to xml files with syntactic and morphological annotations. These xml files are intended to be used 
in the Texthammer or [Nexthammer](https://github.com/hrmJ/nexthammer) corpus projects.

The current version of the project has moved to using the new multilingual
Universal Dependencies -based [Turku neural parser](https://turkunlp.github.io/Turku-neural-parser-pipeline/),
which significanty simplifies and unifies the process of creating unified output. 
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
pip3 install git+https://github.com/utacorpora/texthammer-parsing
```

Usage
-----

Installing with the above instructions creates a command called `texthammerparsing`. It's 
a command line utility with the following specifications:

    texthammerparsing [-h] [--input [inputfiles [inputfiles ...]]]
                         [--output outputfolder] [--id [ids [ids ...]]]
                         [--output_ids filename or path] [--parserpath path]
                         [--cleanup ]
                         action


The command takes one mandatory argument, `action`, which can be one of the following:

- run: runs the full pipeline to produce xmls from tmx

The run command is what you usually need. If needed  (for debugging or otherwise),
the program can be run in separate stages with the following commands:

### prepare

- separates each language from the tmx and stores possible metadata 
- use the `--input` option to specify the folder containing the files
- Example:

```bash
#Each file separately...
texthammerparsing prepare --input myfolder/myfile.tmx myfolder_b/myfile.tmx

#...or a folder
texthammerparsing prepare --input myfolder
```

### parse

- Sends the prepared files (specified by ids) to the parser
- use the `--id` option to specify the ids of the prepared files or the 
- use the `--parserpath` option to specify the folder containing the parser
- Example:

```bash
#Each file separately...
texthammerparsing prepare --input myfolder/myfile.tmx myfolder_b/myfile.tmx

#...or a folder
texthammerparsing prepare --input myfolder
```



- parse: sends the prepared files to the parser
- get_xml: combines the parsed files into a single xml file

### Parsing TMX

In order to parse a single tmx file

### Creating a default configuration




