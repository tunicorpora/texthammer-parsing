#!/Gin/bash

#This script is supposed to be run from its own directory

# Set these paths appropriately!
TMXFOLDER=/home/textmine/corpusinput/tmx/
SNPARSER=/home/textmine/parserit/russian_parser/
TDTPARSER=/home/textmine/parserit/Finnish-dep-parser/
RUPREPARED=/home/textmine/corpusinput/prepared_for_parser/ru/
FIPREPARED=/home/textmine/corpusinput/prepared_for_parser/fi/
PARSED=/home/textmine/corpusinput/parsed
FIPARSED=$PARSED/fi/
RUPARSED=$PARSED/ru/
RUPARSEDNAME=tmpmalttext.parse
PYTHONFOLDER=/home/textmine/tact/database_insertion/


mkdir -p $TMXFOLDER
mkdir -p $RUPREPARED
mkdir -p $FIPREPARED
mkdir -p $RUPARSED
mkdir -p $FIPARSED

#0. Remove old files

#rm $FIPARSED*
#rm $RUPARSED*
#rm $FIPREPARED*
#rm $RUPREPARED*

#1. Prepare tmxes

python3 tmxtoparserinput.py $TMXFOLDER $PARSED
echo "Prepared succesfully."


#2.  Move  the prepared files:

mv $TMXFOLDER/*_fi.prepared $FIPREPARED
mv $TMXFOLDER/*_ru.prepared $RUPREPARED
echo "Moved the prepared files to $FIPREPARED AND $RUPREPARED."
echo "============================================================"

exit 1

#3. Cd to the SNparser directory and start parsing:
cd $SNPARSER
mkdir -p oldfiles
mv *prepared oldfiles/
cp $RUPREPARED/*prepared .
echo "Now starting to parse the Russian files, this probably takes long and consumes all available MEMORY!"
echo "Be patient.."
echo "**********************************************************************"
#3.1 Parse:
for file in *prepared
do 
    sh russian-malt.sh $file
    cp $RUPARSEDNAME $RUPARSED/$file.conll
done


echo "Now starting to parse the FINNISH files.... THIS consumes most of the CPU power"
#4. CD to TDT parsers directory and start parsing
cd $TDTPARSER
mkdir -p oldfiles
mv *prepared oldfiles/
cp $FIPREPARED/*prepared .
#4.1 parse
for file in *prepared
do 
    cat $file | ./parser_wrapper.sh > $file.conll
    mv  $file.conll  $FIPARSED/
done

echo "DONE!\nNow producing the xml file for insertion into the database."

cd $PYTHONFOLDER

python3 conll_to_xml.py parsedmetadata.csv

