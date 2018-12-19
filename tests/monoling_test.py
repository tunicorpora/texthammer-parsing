import unittest
import lxml
import os.path
import glob
import subprocess
from texthammerparsing import Txtfile, parseFiles


class TxtToParserinputTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path = "examples/fi/example.txt"

    def testMarkParagraphs(self):
        self.txt = Txtfile(self.path)
        self.txt.ReadTextdefs()
        self.txt.CheckIfHardWrap()
        self.txt.CollectMetaDataAttributes()
        self.txt.MarkParagraphs()
        self.assertTrue(len(self.txt.output) > 1)

    def testSentenceFilter(self):
        self.txt = Txtfile(self.path)
        self.txt.ReadTextdefs()
        self.txt.CheckIfHardWrap()
        self.txt.CollectMetaDataAttributes()
        self.txt.MarkParagraphs()
        self.txt.FilterSentencesAndParagraphs()
        self.assertTrue(len(self.txt.output) > 1)

    def testPrintPrepared(self):
        self.txt = Txtfile(self.path)
        self.txt.ReadTextdefs()
        self.txt.CheckIfHardWrap()
        self.txt.CollectMetaDataAttributes()
        self.txt.MarkParagraphs()
        self.txt.FilterSentencesAndParagraphs()
        #print(self.txt.all_meta_attributes)
        self.txt.WritePreparedFiles()

    def testPrintPreparedNoTextdef(self):
        self.txt = Txtfile("examples/fi/example_no_textdef.txt")
        self.txt.ReadTextdefs()
        self.txt.CheckIfHardWrap()
        self.txt.CollectMetaDataAttributes()
        self.txt.MarkParagraphs()
        self.txt.FilterSentencesAndParagraphs()
        #print(self.txt.all_meta_attributes)
        self.txt.WritePreparedFiles()



class ParseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass
        #path = "examples/tmx/ru_fi_example.tmx"
        #path = "examples/tmx/multiversion_ex.tmx"
        #tmx = Tmxfile(path)
        #tmx.GetXml()
        #tmx.ReadTextdefs()
        #tmx.CollectMetaDataAttributes()
        #tmx.InitializeVersions("/tmp")
        #tmx.GetVersionContents()
        #tmx.WritePreparedFiles()
        #cls.id = tmx.pair_id




if __name__ == '__main__':
    unittest.main()
