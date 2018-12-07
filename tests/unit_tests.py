import unittest
import lxml
import os.path
from texthammerparsing import Tmxfile


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


if __name__ == '__main__':
    unittest.main()
