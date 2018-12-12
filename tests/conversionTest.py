import unittest
import lxml
import os.path
import glob
import subprocess
import subprocess
from texthammerparsing import TextPair

class ConversionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.makedirs("/tmp/texthammerparsing/", exist_ok=True)
        subprocess.Popen(["cp","-r", "examples/parsed_example/233088b7-636e-4802-9d87-4a7534245c99/", "/tmp/texthammerparsing/"])
        #cls.pair = TextPair("")

    def testCreateInstance(self):
        """
        Creating a TextPair object
        """
        pass
        #self.assertIsInstance(self.tmx, Tmxfile)

    @classmethod
    def tearDownClass(cls):
        print("cleaning up after the tests..")
        subprocess.Popen(["rm","-r", "/tmp/texthammerparsing/233088b7-636e-4802-9d87-4a7534245c99/"])
        #cls.pair = TextPair("")



if __name__ == '__main__':
    unittest.main()
