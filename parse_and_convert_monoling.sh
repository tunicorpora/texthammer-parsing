#!/bin/bash

#IF parsing English, remember to set the parser: [stanford/mate]
ENGPARSER=mate


#FIRST, lock the parser to prevent simultaneous usage

if [ -f .parser.lock ]; then
    echo "The script is ALREADY RUNNING!\nExiting.\nGet rid of this message by removing the file .parser.lock\n(if the lock file has been left there because of the script crashed etc)"
    exit
fi


#echo "locked" > .parser.lock


# Set these paths appropriately!
PARSERLOG=/tmp/parserlog.txt
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
METADATACSV=parsedmetadata.json

XMLFOLDER=/home/textmine/tact/database_insertion/xmloutput/

cleanprepared (){
  mkdir -p oldfiles
  if ls *prepared 1> /dev/null 2>&1; then
     mv *prepared oldfiles
  fi
  if ls $PREPARED/*prepared 1> /dev/null 2>&1; then
      cp $PREPARED/*prepared .
  else
      echo "ATTENTION! The preparing failed for $1. Aborting the script!"
      exit
  fi
}


mkdir -p $INPUTFOLDER
mkdir -p $PARSED
mkdir -p $PREPARED


#0. Remove old files

rm -f $PARSED/*
rm -f $PREPARED/*
rm -f $METADATACSV
rm -f longsentencelog.txt
rm -f xmloutput/*.xml 
rm -f skippedfiles.txt

#1. Save metadata 

#remove possible old files from an uncontrolled script finish
rm -f $INPUTFOLDER*.prepared


python3 txttoparserinput.py $INPUTFOLDER $PARSED

if [ -e "$METADATACSV" ]
then
    echo "Produced $METADATACSV with the following information: "
    cat $METADATACSV
    echo "\n"
else
    echo "ATTENTION! Preparing  the txt files failed. Aborting the script! Please look at **tmxtoparserinput.log** "
    rm -f .parser.lock
    exit
fi


#2.  Move  the prepared files:

if [ -f $INPUTFOLDER/*prepared ]; then
  mv $INPUTFOLDER/*.prepared $PREPARED/
else
  echo "ATTENTION! Preparing  the txt files failed. Aborting the script! Please look at **txttoparserinput.log** "
  rm -f .parser.lock
  exit
fi

echo "Moved the prepared files to $PREPARED"

echo "****************************************************************"
echo "*\n*\n* Now starting the actual parsing. This WILL take time. \n* To make tracking errors easier, the output of the parsers will not be shown here, but rather redirected to $PARSERLOG \n* To see the progress of the parsers in real time, launch another terminal and type this command: tail -f $PARSERLOG\n*\n*"
echo "****************************************************************"

date

case "$1" in

"fi") cd $TDTPARSER
       cleanprepared
       for file in *prepared
       do 
           cat $file | ./parser_wrapper.sh > $file.conll 2> $PARSERLOG
           mv  $file.conll  $PARSED/
       done
       ;;
"ru")  cd $SNPARSER
       # Cd to the SNparser directory and start parsing:
       cleanprepared
       for file in *prepared
       do 
           sh russian-malt.sh $file 2> $PARSERLOG
           cp $RUPARSEDNAME $PARSED/$file.conll
       done
       ;;
"en")  
    if [ "$ENGPARSER" = "stanford" ]; then
       cd $STANFORDPARSER
       cleanprepared
       for file in *prepared
       do 
           ./corenlp.sh -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -file $file -outputFormat conll > $PARSERLOG
           mv $file.conll $PARSED/
       done
   elif [ "$ENGPARSER" = "mate" ];then
       cd $MATEPARSER
       cleanprepared
       for file in *prepared
       do 
           sh parse_en.sh $file  > $PARSERLOG 2>&1
           mv prs-eng-out $PARSED/$file.conll
       done
    fi
       ;;
"de") cd $MATEPARSER
      cleanprepared
      for file in *prepared
      do 
          sh parse_ge.sh $file  > $PARSERLOG 2>&1
          mv parsed_ge.conll $PARSED/$file.conll
      done
      ;;
"fr") cd $MATEPARSER
      cleanprepared
      for file in *prepared
      do 
          sh parse_fr.sh $file  > $PARSERLOG 2>&1
          mv parsed_fr.conll $PARSED/$file.conll
      done
      ;;
"sv") cd $SWEPARSER
      cleanprepared
      for file in *prepared
      do 
          #note: the swedish tokenizer needs the source file as txt
          cp $file $file.txt
          sh parse.sh $file.txt 2> $PARSERLOG
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
      for file in *prepared
      do 
          echo "Parsing $file"
          sh parse_sp.sh $file > $PARSERLOG 2>&1
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

rm -f .parser.lock

if [ "$1" = "en" ]; then
    python3 conll_to_xml.py parsedmetadata.json $ENGPARSER
else
    python3 conll_to_xml.py parsedmetadata.json
fi


XMLFILES="$(ls xmloutput/*xml | wc -l)"
if [ "$XMLFILES" -gt "0" ]; then
  cp xmloutput/*.xml $XMLFOLDER
  echo "COPIED the xml files to $XMLFOLDER."
else
  echo "WARNING! No xml files produced!"
fi

echo "REMEMBER to check the log files (txtoparserinput.log and conll_to_xml.log) to see if some files did not pass."

if [ -f skippedfiles.txt ]; then
    echo "Skipped the following files:"
    cat skippedfiles.txt
    cat "\n"
fi
