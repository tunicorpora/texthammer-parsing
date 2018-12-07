Trying out the new Finnish dep parser at [https://turkunlp.github.io/Turku-neural-parser-pipeline/](https://turkunlp.github.io/Turku-neural-parser-pipeline/).

The parser should be run in a virtual environment:

```

source venv-parser-neural/bin/activate

cat file.txt | python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml --pipeline parse_plaintext > output.conllu
echo "Я играю на гармошке. Он занимается спортом. Путин любит футбол."| python3 full_pipeline_stream.py --conf models_ru_syntagrus/pipelines.yaml --pipeline parse_plaintext > output.conllu


```

