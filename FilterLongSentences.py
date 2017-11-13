import sys
import re

loggerfile = "longsentencelog.txt"

def LogLongParagraph(par, newpar):
    """If a too long sentence was met, log the changes that were made"""
    with open(loggerfile,"a") as f:
        f.write("\n\n{}:\n{}\n{}\n\n>>>>>>\n\n{}\n\n".format(Paragraph.filename,"="*40,par, newpar))

class Paragraph():
    """A paragraph delimited by to newlines"""

    long_paragraph_treshold = 300
    toomuch_characters_per_sentence = 1000
    filename = "unknown file"

    def __init__(self, rawtext):
        """Find large paragraphs"""
        self.text = rawtext
        if self.IsThisParagraphLong():
            #Only if the paragraph is longer than the threshold, process the sentences
            self.ProcessSentences()

    def IsThisParagraphLong(self):
        """Measure the length of the paragraph by words (it's okay to have only a rough estimate with whitespaces)"""
        if len(self.text.split()) > Paragraph.long_paragraph_treshold:
            return True
        return False

    def ProcessSentences(self):
        """For the long paragraphs, split into sentences and measure the length of each."""
        nostopcount = 0
        stopchars = [".","?","!"]
        newtext = ""
        insertstop = False
        for char in self.text:
            if char not in stopchars:
                nostopcount += 1
            else:
                nostopcount = 0

            if nostopcount > Paragraph.toomuch_characters_per_sentence:
                insertstop = True

            if insertstop and char in [",",":",";"]:
                #Add a full stop if maximum sentence length by characters exceeded
                #(do the adding at the next COMMA/semicolon/colon)
                insertstop = False
                char = "."
                nostopcount = 0

            newtext += char
        if newtext != self.text:
            LogLongParagraph(self.text, newtext)
        self.text = newtext

def FilterByCharCount(rawtext, filename):

    #Clear the log file
    #with open(loggerfile,"w") as f:
    #    f.write("")

    Paragraph.filename = filename

    # Split the text into paragraphs
    paragraphs = re.split(r"\n{2,}", rawtext)

    processed = ""
    for p in paragraphs:
        p_object = Paragraph(p)
        processed += "\n\n" + p_object.text

    return processed
