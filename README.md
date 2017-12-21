TEXTMINE-PARSING
================


This project contains the utilities needed to parse multilingual tmx-files and convert them
to xml files with syntactic and morphological annotations. These xml files are meant to be used 
in the Textmine corpus project.

Instructions for parsing
========================

Multilingual tmx files
----------------------

1. Put the files you want to ~/corpusinput/tmx
    - note: the files must all include <textdef> tags for all languages (containing metadata)

2. Cd to textmine-parsing

3. run: `sh parse_and_convert.sh ` + abbreviations for all the languages included, e.g. `sh parse_and_convert.sh en fi ru`
