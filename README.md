TEXTMINE-PARSING
================


This project contains the utilities needed to parse multilingual tmx-files and convert them
to xml files with syntactic and morphological annotations. These xml files are meant to be used 
in the Texthammer or [Nexthammer](https://github.com/hrmJ/nexthammer) corpus projects.

Information about the parsers installed 
========================================


name|language|developer|url|reference|additional information
----------|------|-----------------|----|----|
Finnish dependency parser by the  Turku NLP group (TDT parser)|fi|Filip Ginter et al |http://turkunlp.github.io/Finnish-dep-parser/|[1]|we are using the UD version, cf. [8]. 
Dependency parser for Russian by  Sharoff and Nivre |ru|Serge Sharoff, Joakim Nivre|http://corpus.leeds.ac.uk/mocky/|[2]|
SweMalt:  MaltParser with a pre-trained model for Swedish|sv|Joakim Nivre et al?|http://www.maltparser.org/mco/swedish_parser/swemalt.html|[3] +  [4]|The parser was trained on the Swedish Treebank (Nivre et al., 2008) and the SUC PoS tagset with morphological features
Mate parser with a pre-trained model for English |en|Bernd Bohnet et al |https://code.google.com/archive/p/mate-tools/|[5] + [6]|
Mate parser with a pre-trained model for German |de|Bernd Bohnet et al|https://code.google.com/archive/p/mate-tools/|[5] + [6]|
Mate parser with a pre-trained model for French |fr|Bernd Bohnet et al|https://code.google.com/archive/p/mate-tools/|[5] + [6] + [7]|
Mate parser with a pre-trained model for Spanish|es|Bernd Bohnet et al|https://code.google.com/archive/p/mate-tools/|[5] + [6] + [9]|the Spanish parsing pipeline uses Stanford CoreNLP [https://stanfordnlp.github.io/CoreNLP/](https://stanfordnlp.github.io/CoreNLP/) for tokenization, cf. citation no [9]. 


[1] Haverinen, Katri, et al. "Building the essential resources for Finnish: the Turku Dependency Treebank." Language Resources and Evaluation 48.3 (2014): 493-531. DOI: 10.1007/s10579-013-9244-1

[2] Sharoff, Serge, and Joakim Nivre. "The proper place of men and machines in language technology: Processing Russian without any linguistic knowledge." Proc. Dialogue 2011, Russian Conference on Computational Linguistics. 2011. http://www.dialog-21.ru/digests/dialog2011/materials/en/pdf/58.pdf

[3] Nivre, Joakim, Johan Hall, and Jens Nilsson. "Maltparser: A data-driven parser-generator for dependency parsing." Proceedings of LREC. Vol. 6. 2006. http://lrec-conf.org/proceedings/lrec2006/pdf/162_pdf.pdf

[4] Nivre, Joakim, et al. "Cultivating a Swedish treebank." Resourceful Language Technology (2008): 111. http://stp.lingfil.uu.se/~nivre/docs/saagvall1.pdf

[5] Björkelund, A., Bohnet, B., Hafdell, L., & Nugues, P. (2010, August). A high-performance syntactic and semantic dependency parser. In Proceedings of the 23rd International Conference on Computational Linguistics: Demonstrations (pp. 33-36). Association for Computational Linguistics. https://dl.acm.org/citation.cfm?id=1944293

[6] Bohnet, B., Nivre, J., Boguslavsky, I., Farkas, R., Ginter, F., & Hajič, J. (2013). Joint morphological and syntactic analysis for richly inflected languages. Transactions of the Association for Computational Linguistics, 1, 415-428. https://www.transacl.org/ojs/index.php/tacl/article/view/158/77

[7] Marie Candito, Benoˆıt Crabb´e, Pascal Denis. Statistical French dependency parsing: treebank conversion and first results. Seventh International Conference on Language Resources and Evaluation - LREC 2010, May 2010, La Valletta, Malta. European Language Resources Association (ELRA), pp.1840-1847, 2010. https://hal.inria.fr/file/index/docid/495196/filename/LREC2010-canditocrabbedenis-final.pdf

[8] Pyysalo, S., Kanerva, J., Missilä, A., Laippala, V., & Ginter, F. (2015, May). Universal dependencies for Finnish. In Proceedings of the 20th Nordic Conference of Computational Linguistics, NODALIDA 2015, May 11-13, 2015, Vilnius, Lithuania (No. 109, pp. 163-172). Linköping University Electronic Press. http://www.ep.liu.se/ecp/109/021/ecp15109021.pdf

[9] Manning, Christopher D., Mihai Surdeanu, John Bauer, Jenny Finkel, Steven J. Bethard, and David McClosky. 2014. The Stanford CoreNLP Natural Language Processing Toolkit In Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics: System Demonstrations, pp. 55-60


Instructions for parsing
========================

Multilingual tmx files
----------------------

1. Put the files you want to ~/corpusinput/tmx
    - note: the files must all include <textdef> tags for all languages (containing metadata)

2. Cd to textmine-parsing

3. run: `sh parse_and_convert.sh ` + abbreviations for all the languages included, e.g. `sh parse_and_convert.sh en fi ru`


