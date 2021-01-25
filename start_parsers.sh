#!/bin/bash

while test $# -gt 0
do
    case "$1" in
        "fi") echo "Starting the Finnish parser"
            docker rm -f parser_fi 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_fi -d -p 15000:7689 parser_fi server fi_tdt parse_plaintext
            docker ps
            ;;
        ru) echo "Starting the Russian parser"
            docker rm -f parser_ru 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_ru -d -p 15001:7689 parser_ru server ru_syntagrus parse_plaintext
            docker ps
            ;;
        en) echo "Starting the English parser"
            docker rm -f parser_en 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_en -d -p 15002:7689 parser_en server en_ewt parse_plaintext
            ;;
        fr) echo "Starting the French parser"
            docker rm -f parser_fr 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_fr -d -p 15003:7689 parser_fr server fr_gsd parse_plaintext
            ;;
        sv) echo "Starting the Swedish parser"
            docker rm -f parser_sv 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_sv -d -p 15004:7689 parser_sv server sv_talbanken parse_plaintext
            ;;
        de) echo "Starting the German parser"
            docker rm -f parser_de 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_de -d -p 15005:7689 parser_de server de_gsd parse_plaintext
            ;;
        es) echo "Starting the Spanish parser"
            docker rm -f parser_es 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_es -d -p 15006:7689 parser_es server es_ancora parse_plaintext
            ;;
        pl) echo "Starting the Polish parser"
            docker rm -f parser_pl 2>/dev/null && echo 'Removed old container' 
            docker run --name parser_pl -d -p 15007:7689 parser_pl server pl_lfg parse_plaintext
            ;;
        *) echo "Unkown language code!"
            ;;
    esac
    shift
done

exit 0



