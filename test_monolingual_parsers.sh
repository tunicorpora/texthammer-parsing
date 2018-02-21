#!/bin/bash
#Script for testing all the monolingual parsers

INPUTFOLDER=/home/textmine/corpusinput/monoling
rm -f $INPUTFOLDER/*
for lang in en de sv fi ru es fr; do 
    echo $lang
    cp examples/$lang/example.txt $INPUTFOLDER
    sh parse_and_convert_monoling.sh $lang
done
