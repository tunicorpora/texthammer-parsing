#!/bin/bash

#This script is supposed to be run from its own directory
#USAGE: parse_and_convert_monoling.sh <language (fi,ru,en,dec)> 

#IF parsing English, remember to set the parser: [stanford/mate]
ENGPARSER=mate


#FIRST, lock the parser to prevent simultaneous usage

if [ -f .parser.lock ]; then
    echo "The script is ALREADY RUNNING!\nExiting.\nGet rid of this message by removing the file .parser.lock\n(if the lock file has been left there because of the script crashed etc)"
    exit
fi

echo "locked" > .parser.lock



# Set these paths appropriately!
INPUTFOLDER=/home/textmine/corpusinput/monoling/

SNPARSER=/home/textmine/parserit/russian_parser/
SWEPARSER=/home/textmine/parserit/swedish/
RUPARSEDNAME=tmpmalttext.parse
TDTPARSER=/home/textmine/parserit/Finnish-dep-parser/
STANFORDPARSER=/home/textmine/parserit/stanford/stanford-corenlp-full-2015-12-09/
MATEPARSER=/home/textmine/parserit/mate-tools/

PARSED=/home/textmine/corpusinput/parsed/$1
PREPARED=/home/textmine/corpusinput/prepared_for_parser/$1

PYTHONFOLDER=/home/textmine/textmine-parsing/
METADATACSV=parsedmetadata.csv

XMLFOLDER=/home/textmine/tact/database_insertion/xmloutput/


mkdir -p $INPUTFOLDER
mkdir -p $PARSED
mkdir -p $PREPARED


#0. Remove old files

rm -f $PARSED/*
rm -f $PREPARED/*
rm -f $METADATACSV
rm longsentencelog.txt

#1. Save metadata to csv

#remove possible old files from an uncontrolled script finish
rm -f $INPUTFOLDER*.prepared

python3 txttoparserinput.py $INPUTFOLDER $PARSED

if [ -e "$METADATACSV" ]
then
    echo "Prepared succesfully"
else
    echo "Something wrong with the input files, no metadata file produced. \nLook at the error messages from txtoparserinput.py.\nSuggestion: are some of the files utf-16?\nExiting"
    rm .parser.lock
    exit
fi


#2.  Move  the prepared files:

mv $INPUTFOLDER/*.prepared $PREPARED/


echo "Moved the prepared files to $PREPARED"
echo "============================================================"


case "$1" in

"fi")  echo "Now starting to parse the FINNISH files.... THIS consumes most of the CPU power"
       #4. CD to TDT parsers directory and start parsing
       cd $TDTPARSER
       mkdir -p oldfiles
       mv *prepared oldfiles/
       cp $PREPARED/*prepared .
       #4.1 parse
       for file in *prepared
       do 
           cat $file | ./parser_wrapper.sh > $file.conll
           mv  $file.conll  $PARSED/
       done
       ;;
"ru")  cd $SNPARSER
       # Cd to the SNparser directory and start parsing:
       mkdir -p oldfiles
       mv *prepared oldfiles/
       cp $PREPARED/*prepared .
       echo "Now starting to parse the Russian files, this probably takes long and consumes all available MEMORY!"
       echo "Be patient.."
       echo "**********************************************************************"
       #3.1 Parse:
       for file in *prepared
       do 
           sh russian-malt.sh $file
           cp $RUPARSEDNAME $PARSED/$file.conll
       done
       ;;
"en")  
    if [ "$ENGPARSER" = "stanford" ]; then
       # Cd to the parser directory and start parsing:
       cd $STANFORDPARSER
       mkdir -p oldfiles
       mv *prepared oldfiles/
       cp $PREPARED/*prepared .
       echo "Now starting to parse the English files with $ENGPARSER"
       echo "Be patient.."
       echo "**********************************************************************"
       #3.1 Parse:
       for file in *prepared
       do 
           ./corenlp.sh -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -file $file -outputFormat conll
           mv $file.conll $PARSED/
       done
   elif [ "$ENGPARSER" = "mate" ];then
       # Cd to the parser directory and start parsing:
       cd $MATEPARSER
       mkdir -p oldfiles
       mv *prepared oldfiles/
       cp $PREPARED/*prepared .
       echo "Now starting to parse the English files with $ENGPARSER"
       echo "Be patient.."
       echo "**********************************************************************"
       #3.1 Parse:
       for file in *prepared
       do 
           sh parse_en.sh $file
           mv prs-eng-out $PARSED/$file.conll
       done
    fi
       ;;
"de") cd $MATEPARSER
      mkdir -p oldfiles
      mv *prepared oldfiles/
      cp $PREPARED/*prepared .
      echo "Now starting to parse the GERMAN files"
      echo "Be patient.."
      echo "**********************************************************************"
      #3.1 Parse:
      for file in *prepared
      do 
          sh parse_ge.sh $file
          mv parsed_ge.conll $PARSED/$file.conll
      done
      ;;
"fr") cd $MATEPARSER
      mkdir -p oldfiles
      mv *prepared oldfiles/
      cp $PREPARED/*prepared .
      echo "Now starting to parse the FRENCH files"
      echo "Be patient.."
      echo "**********************************************************************"
      #3.1 Parse:
      for file in *prepared
      do 
          echo "Parsing $file"
          sh parse_fr.sh $file
          mv parsed_fr.conll $PARSED/$file.conll
      done
      ;;
"sv") cd $SWEPARSER
      mkdir -p oldfiles
      mv *prepared oldfiles/
      cp $PREPARED/*prepared .
      echo "Now starting to parse the SWEDISH files"
      echo "Be patient.."
      echo "**********************************************************************"
      #3.1 Parse:
      for file in *prepared
      do 
          #note: the swedish tokenizer needs the source file as txt
          cp $file $file.txt
          sh parse.sh $file.txt
          mv outfile.conll $PARSED/$file.conll
          #remove the temporary txt file
          rm $file.txt
      done
      ;;
"es") cd $MATEPARSER
      mkdir -p oldfiles
      mv *prepared oldfiles/
      cp $PREPARED/*prepared .
      echo "Now starting to parse the SPANISH files"
      echo "Be patient.."
      echo "**********************************************************************"
      #3.1 Parse:
      for file in *prepared
      do 
          echo "Parsing $file"
          sh parse_sp.sh $file
          mv parsed_es.conll $PARSED/$file.conll
      done
      ;;
*) echo "Unknown language: no parser specified for $1. Exiting..."
    rm .parser.lock
    exit
     ;;

esac


echo "DONE!\nNow producing the xml file for insertion into the database."


cd $PYTHONFOLDER

rm .parser.lock

if [ "$1" = "en" ]; then
    python3 conll_to_xml.py parsedmetadata.csv $ENGPARSER
else
    python3 conll_to_xml.py parsedmetadata.csv
fi


cp xmloutput/*.xml $XMLFOLDER

echo "COPIED the xml files (if there were any) to $XMLFOLDER."

