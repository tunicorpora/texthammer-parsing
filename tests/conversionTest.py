import unittest
import lxml
import os.path
import glob
import subprocess
import subprocess
import re
from texthammerparsing import TextPair

class ConversionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs("/tmp/texthammerparsing/", exist_ok=True)
        subprocess.Popen(["cp","-r", "examples/parsed_example/233088b7-636e-4802-9d87-4a7534245c99/", "/tmp/texthammerparsing/"])
        pair_id = "233088b7-636e-4802-9d87-4a7534245c99"
        cls.pair = TextPair(pair_id)

    def testLoopingThrough(self):
        """
        Try to collect all the information
        """
        self.pair.LoopThroughSegments()
        xml = lxml.etree.tounicode(self.pair.root, pretty_print=True)
        self.assertTrue(re.search("lemma=.российский.",xml))

    @classmethod
    def tearDownClass(cls):
        print("cleaning up after the tests..")
        #subprocess.Popen(["rm","-r", "/tmp/texthammerparsing/233088b7-636e-4802-9d87-4a7534245c99/"])
        #cls.pair = TextPair("")



if __name__ == '__main__':
    unittest.main()
