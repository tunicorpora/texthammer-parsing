#!/bin/bash

#a quick setup for installing the turku neural parser
#and downloading some language models
#this is just a straight-forward copy of the instructions
#at https://turkunlp.github.io/Turku-neural-parser-pipeline/

sudo apt install -y build-essential python3-dev python3-venv python3-tk
git clone https://github.com/TurkuNLP/Turku-neural-parser-pipeline.git
cd Turku-neural-parser-pipeline
git submodule update --init --recursive
python3 -m venv venv-parser-neural
source venv-parser-neural/bin/activate
pip3 install wheel
pip3 install -r requirements-cpu.txt
python3 fetch_models.py fi_tdt
python3 fetch_models.py ru_syntagrus
