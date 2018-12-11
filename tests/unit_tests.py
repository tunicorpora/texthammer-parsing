import unittest
import lxml
import os.path
import glob
import subprocess
from texthammerparsing import Tmxfile, parseFiles


class TmxToParserinputTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = "examples/tmx/ru_fi_example.tmx"
        path = "examples/tmx/multiversion_ex.tmx"
        cls.tmx = Tmxfile(path)

    def testCreateTmxFile(self):
        """
        Creating a Tmxfile object
        """
        self.assertIsInstance(self.tmx, Tmxfile)

    def testReadXml(self):
        """
        Read the xml of the tmx
        """
        self.tmx.GetXml()
        self.assertFalse(self.tmx.errors)

    def testReadTextdefs(self):
        """
        Reads the textdef tags
        """
        self.tmx.GetXml()
        self.tmx.ReadTextdefs()
        self.assertFalse(self.tmx.errors)

    def testCollectMetaDataAttributs(self):
        """
        Collects metadata
        """
        self.tmx.GetXml()
        self.tmx.ReadTextdefs()
        self.tmx.CollectMetaDataAttributes()
        self.assertFalse(self.tmx.errors)


    def testInitializeVersions(self):
        """
        Initializes versions
        """
        self.tmx.GetXml()
        self.tmx.ReadTextdefs()
        self.tmx.CollectMetaDataAttributes()
        self.tmx.InitializeVersions("/tmp")
        self.assertFalse(self.tmx.errors)

    def testGetVersionContents(self):
        """
        Gets the versions' content
        """
        self.tmx.GetXml()
        self.tmx.ReadTextdefs()
        self.tmx.CollectMetaDataAttributes()
        self.tmx.InitializeVersions("/tmp")
        self.tmx.GetVersionContents()
        self.assertFalse(self.tmx.errors)


    def testOutputPrepared(self):
        """
        Test's outputting the prepared files 
        """
        self.tmx.GetXml()
        self.tmx.ReadTextdefs()
        self.tmx.CollectMetaDataAttributes()
        self.tmx.InitializeVersions("/tmp")
        self.tmx.GetVersionContents()
        self.tmx.WritePreparedFiles()
        #self.assertTrue(os.path.isfile("/tmp/" + self.tmx.pair_id + ".json"))

class ParseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = "examples/tmx/ru_fi_example.tmx"
        path = "examples/tmx/multiversion_ex.tmx"
        tmx = Tmxfile(path)
        tmx.GetXml()
        tmx.ReadTextdefs()
        tmx.CollectMetaDataAttributes()
        tmx.InitializeVersions("/tmp")
        tmx.GetVersionContents()
        tmx.WritePreparedFiles()
        cls.id = tmx.pair_id

    def testListFilesToParse(self):
        for f in glob.glob("/tmp/texthammerparsing/" + self.id + "/prepared/*"):
            #cat myfile.txt | python3 full_pipeline_stream.py --conf models_fi_tdt/pipelines.yaml --pipeline parse_plaintext > myfile.conllu
            self.assertTrue(os.path.isfile(f))



if __name__ == '__main__':
    unittest.main()
