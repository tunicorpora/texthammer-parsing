#!/bin/bash

#This script is supposed to be run from its own directory

#USAGE: parse_and_convert.sh list of languages included in the tmxfiles, e.g.
#parse_and_convert.sh fi en ru de 
#parse_and_convert.sh ru fi
#etc..

#IF parsing English, remember to set the parser: [stanford/mate]
ENGPARSER=mate

#FIRST, lock the parser to prevent simultaneous usage
if [ -f .parser.lock ]; then
    echo "The script is ALREADY RUNNING!\nExiting.\nGet rid of this message by removing the file .parser.lock\n(if the lock file has been left there because of the script crashed etc)"
    exit
fi

echo "locked" > .parser.lock



# Set these paths appropriately!
#1: input
TMXFOLDER=/home/textmine/corpusinput/tmx/

#2: parsers
SNPARSER=/home/textmine/parserit/russian_parser/
SWEPARSER=/home/textmine/parserit/swedish/
RUPARSEDNAME=tmpmalttext.parse
TDTPARSER=/home/textmine/parserit/Finnish-dep-parser/
STANFORDPARSER=/home/textmine/parserit/stanford/stanford-corenlp-full-2015-12-09/
MATEPARSER=/home/textmine/parserit/mate-tools/
ICEPARSER=/home/textmine/parserit/IceNLPCore/bat/icetagger/


#3: intermediate file locations
PARSED=/home/textmine/corpusinput/parsed
PREPARED=/home/textmine/corpusinput/prepared_for_parser

#4: script folder, metadata file
PYTHONFOLDER=/home/textmine/tact/database_insertion/
METADATACSV=/home/textmine/tact/database_insertion/parsedmetadata.csv


#0. Remove old files and create the directories if needed

for lang in "$@"
do
    mkdir -p $PARSED/$lang
    mkdir -p $PREPARED/$lang
    rm -f $PARSED/$lang/*
    rm -f $PREPARED/$lang/*
    rm longsentencelog.txt
done

rm -f $METADATACSV
rm -f $TMXFOLDER*.prepared


#0.1 Convert from utf-16 to utf-8 IF needed


for x in $TMXFOLDER/*tmx ; do
    fenc="$(file -bi  $x)"

    case "$fenc" in
          *utf-16*) 
              iconv -f UTF-16 -t UTF-8 $x > $x.tmp && mv $x.tmp $x;
              ;;
    esac
done

#1. Prepare tmxes


python3 tmxtoparserinput.py $TMXFOLDER $PARSED

if [ -e "$METADATACSV" ]
then
    echo "Prepared succesfully"
else
    echo "Something wrong with the tmx files, no metadata file produced. \nLook at the error messages from tmxtoparserinput.py.\nSuggestion: are some of the files tf-16?\nExiting"
    rm .parser.lock
    exit
fi


#2.  Move  the prepared files:

for lang in "$@"
do
    mv $TMXFOLDER/*_$lang.prepared $PREPARED/$lang/
    echo "Moved the prepared files to $PREPARED/$lang/"
done

echo "============================================================"


for lang in "$@"
do
    case "$lang" in

    "fi")  echo "Now starting to parse the FINNISH files.... THIS consumes most of the CPU power"
           #4. CD to TDT parsers directory and start parsing
           cd $TDTPARSER
           mkdir -p oldfiles
           mv *prepared oldfiles/
           cp $PREPARED/$lang/*prepared .
           #4.1 parse
           for file in *prepared
           do 
               cat $file | ./parser_wrapper.sh > $file.conll
               mv  $file.conll  $PARSED/$lang/
           done
           ;;
    "ru")  cd $SNPARSER
           # Cd to the SNparser directory and start parsing:
           mkdir -p oldfiles
           mv *prepared oldfiles/
           cp $PREPARED/$lang/*prepared .
           echo "Now starting to parse the Russian files, this probably takes long and consumes all available MEMORY!"
           echo "Be patient.."
           echo "**********************************************************************"
           #3.1 Parse:
           for file in *prepared
           do 
               sh russian-malt.sh $file
               cp $RUPARSEDNAME $PARSED/$lang/$file.conll
           done
           ;;
    "en")  
        if [ "$ENGPARSER" = "stanford" ]; then
           # Cd to the parser directory and start parsing:
           cd $STANFORDPARSER
           mkdir -p oldfiles
           mv *prepared oldfiles/
           cp $PREPARED/$lang/*prepared .
           echo "Now starting to parse the English files with $ENGPARSER"
           echo "Be patient.."
           echo "**********************************************************************"
           #3.1 Parse:
           for file in *prepared
           do 
               ./corenlp.sh -annotators tokenize,ssplit,pos,lemma,ner,parse,dcoref -file $file -outputFormat conll
               mv $file.conll $PARSED/$lang/
           done
       elif [ "$ENGPARSER" = "mate" ];then
           # Cd to the parser directory and start parsing:
           cd $MATEPARSER
           mkdir -p oldfiles
           mv *prepared oldfiles/
           cp $PREPARED/$lang/*prepared .
           echo "Now starting to parse the English files with $ENGPARSER"
           echo "Be patient.."
           echo "**********************************************************************"
           #3.1 Parse:
           for file in *prepared
           do 
               sh parse_en.sh $file
               mv prs-eng-out $PARSED/$lang/$file.conll
           done
        fi
           ;;
    "de") cd $MATEPARSER
          mkdir -p oldfiles
          mv *prepared oldfiles/
          cp $PREPARED/$lang/*prepared .
          echo "Now starting to parse the GERMAN files"
          echo "Be patient.."
          echo "**********************************************************************"
          #3.1 Parse:
          for file in *prepared
          do 
              echo "Parsing $file"
              sh parse_ge.sh $file
              mv parsed_ge.conll $PARSED/$lang/$file.conll
          done
          ;;
    "fr") cd $MATEPARSER
          mkdir -p oldfiles
          mv *prepared oldfiles/
          cp $PREPARED/$lang/*prepared .
          echo "Now starting to parse the FRENCH files"
          echo "Be patient.."
          echo "**********************************************************************"
          #3.1 Parse:
          for file in *prepared
          do 
              echo "Parsing $file"
              sh parse_fr.sh $file
              mv parsed_fr.conll $PARSED/$lang/$file.conll
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
              mv outfile.conll $PARSED/$lang/$file.conll
              #remove the temporary txt file
              rm $file.txt
          done
          ;;
    "is") cd $ICEPARSER
        #ICELANDIC: TODO, just faking and using the German parser
          mkdir -p oldfiles
          mv *prepared oldfiles/
          cp $PREPARED/$lang/*prepared .
          echo "Now starting to parse the ICELANDIC files (NO SYNTAX)"
          echo "Be patient.."
          echo "**********************************************************************"
          #3.1 Parse:
          for file in *prepared
          do 
              echo "Parsing $file"
              sh icetagger.sh -i $file -o out.txt -lem
              mv out.txt $PARSED/$lang/$file.conll
          done
          #FIX tokenization:
          cd $PYTHONFOLDER
          for file in $PARSED/$lang/*.conll
          do 
              echo "Fixing $file"
              python3 fix_is_tokens.py $file
          done
          ;;
    *) echo "Unknown language: no parser specified for $lang. Exiting..."
        rm .parser.lock
        exit
         ;;

    esac

done

echo "DONE!\nNow producing the xml file for insertion into the database."

cd $PYTHONFOLDER
rm .parser.lock

python3 conll_to_xml.py parsedmetadata.csv $ENGPARSER
