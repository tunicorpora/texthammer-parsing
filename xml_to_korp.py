#!/usr/bin/python3
from lxml import etree
import string
import sys
import os
import re
from collections import OrderedDict

def ParseFileName(fname):
    dot = fname.rfind(".")
    slash = fname.rfind("/")
    return sys.argv[2] + fname[slash+1:dot]

class XmlDoc():
    """Xml sisään, valinnaisia formaatteja ulos"""
    def __init__(self, fname, doctype, plain=False):
        self.fname = fname
        self.outputname = ParseFileName(fname)
        self.isplain = plain
        self.doctype = doctype
        self.ReadXml()
        self.getAligns()

    def ReadXml(self):
        with open(self.fname,"r") as f:
            xmlinput = f.read()

        self.root = etree.fromstring(xmlinput)
        self.metadatas = self.root.xpath("//textdef")

        #Get languages and how many translations exist in each language
        self.langnames = dict()
        for entry in self.metadatas:
            if entry.get('lang') not in self.langnames:
                self.langnames[entry.get('lang')] = [0]
            else:
                self.langnames[entry.get('lang')].append(self.langnames[entry.get('lang')][-1]+1)

    def getAligns(self):
        self.aligns = self.root.xpath('//align')

    def ParseTextHammer(self):

        self.languages = dict()
        self.languagemetas = dict()

        for lang in self.langnames:
            self.languages[lang] = dict()
            self.languagemetas[lang] = dict()

        for lang, count in self.langnames.items():
            self.languages[lang] = {}
            metas = self.root.xpath('textdef[@lang="{}"]'.format(lang))
            for idx, meta in enumerate(metas):
                self.languagemetas[lang][idx] = ""
                for attrname, attrvalue in meta.attrib.items():
                    self.languagemetas[lang][idx] += '{}="{}" '.format(attrname, attrvalue)

        for align in self.aligns:
            for lang in self.langnames.keys():
                langsegs = align.xpath('seg[@lang="{}"]'.format(lang))
                for idx, seg in enumerate(langsegs):
                    if idx not in self.languages[lang]:
                        self.languages[lang][idx] = list()
                    self.languages[lang][idx].append(self.GetSegmentText(seg, lang))

    def GetAlNos(self):
        self.al_nos = list()
        self.languages = dict()
        for align in self.aligns:
            if self.doctype == 'mustikka':
                no = align.get('al_no')
                lang = align.get('lng')
                if no not in self.al_nos:
                    self.al_nos.append(no)
                if lang not in self.languages:
                    self.languages[lang] = dict()

    def OutPutForParser(self):
        """ Tee kullekin kielelle omat tiedostonsa"""
        versions = dict()
        for langname, langdict in self.languages.items():
            for version, segments in langdict.items():
                version_name = "{}_{}{}.vrt".format(self.outputname, langname, version+1) #+1 ettei ala nollasta
                if version_name not in versions:
                    versions[version_name] = '<text {}>\n'.format(self.languagemetas[langname][version])
                    for idx, segment in enumerate(segments):
                        versions[version_name] += '<align id="{}">\n{}\n</align>\n'.format(idx+1,segment)
                    versions[version_name] += '</text>'

        for name, version in versions.items():
            with open(name,'w') as f:
                f.write(version)

    def GetSegmentText(self, segment, lang):
            printsentences = list()
            sentences = segment.getchildren()
            for sentence in sentences:
                printsentence = list()
                self.last_tokenid = 0
                tokens = sentence.getchildren()
                for token in tokens:
                    printsentence.append(self.GetTHtoken(token, lang))
                printsentences.append('<s>\n' + '\n'.join(printsentence) + '\n</s>')

            return '\n'.join(printsentences)

    def GetTHtoken(self, token, lang):
        if token.get('type') == 'punct':
            headid = self.last_tokenid
            self.last_tokenid += 1
        else:
            self.last_tokenid = int(token.get('tokenid'))

        last_tokenid = self.last_tokenid

        #Käännä tämä todeksi/epätodeksi riippuen siitä, haluatko yksinkertaistaa välimerkkien esitystapaa
        simplifypunct=False

        if lang == 'ru':
            if token.get('type') == 'punct':
                if simplifypunct:
                    tokeninfo = [token.text, str(last_tokenid),  'pun', 'pun']
                else:
                    if token.text in [',',':',"'",'"']:
                        tokeninfo = [token.text, str(last_tokenid),  token.text, token.text, token.text, 'PUNC', str(headid)]
                    else:
                        tokeninfo = [token.text,str(last_tokenid), token.text, 'S', 'SENT', 'PUNC', str(headid)]
            else:
                tokeninfo = [token.text,str(last_tokenid), token.get('lemma'), token.get('pos'), token.get('frm'), token.get('deprel'), token.get('headid')]

        elif lang == 'fi':
            if token.get('type') == 'punct':
                if simplifypunct:
                    tokeninfo = [token.text, str(last_tokenid),  'pun', 'pun']
                else:
                    tokeninfo = [token.text, str(last_tokenid), token.text, 'PUNCT', '_', 'punct', str(headid)]
            else:
                tokeninfo = [token.text, token.get('tokenid'), token.get('lemma'), token.get('pos'), token.get('frm'), token.get('deprel'), token.get('headid')]


        return '\t'.join(tokeninfo)

if __name__ == '__main__':
    if len(sys.argv)<3:
        sys.exit("Usage: {} <{l}> <{}>".format(sys.argv[0],"source file", "target folder"))
    thisxml = XmlDoc(sys.argv[1],'texthammer')
    thisxml.GetAlNos()
    thisxml.ParseTextHammer()
    thisxml.OutPutForParser()
