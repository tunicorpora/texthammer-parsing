import sys
import re
import string

loggerfile = "longsentencelog.txt"

def LogLongParagraph(par, newpar):
    """If a too long sentence was met, log the changes that were made"""
    with open(loggerfile,"a") as f:
        f.write("\n\n{}:\n{}\n{}\n\n>>>>>>\n\n{}\n\n".format(Paragraph.filename,"="*40,par, newpar))

class Paragraph():
    """A paragraph delimited by two newlines"""

    long_paragraph_treshold = 300
    toomuch_characters_per_sentence = 1000
    filename = "unknown file"

    def __init__(self, rawtext):
        """Find large paragraphs"""
        self.text = rawtext
        self.length = len(self.text.split())

    def IsThisParagraphLong(self):
        """Measure the length of the paragraph by words (it's okay to have only a rough estimate with whitespaces)"""
        if self.length > Paragraph.long_paragraph_treshold:
            print("Warning: an exceptionally long paragraph found. ({} words). This might be difficult for the parser to parse.".format(len(self.text.split())))
            return True
        return False


    def FilterPunctuationMarkWithNoSpaces(self):
        """
        whatch out for cases where no whitespace after terminating punct
        """
        stopchars = [".","?","!"]
        pat = re.compile("[{}]".format("".join(stopchars)))
        npunct = len(pat.findall(self.text))
        if not re.search("[" + "".join(stopchars) + r"]\s", self.text) and npunct > 2:
            #Add spaces after the term. punct if none.
            rep = re.sub("([a-öа-я])([" + "".join(stopchars) + r"])([a-öа-я])",
                    r"\1\2 \3",
                    self.text,
                    flags=re.IGNORECASE)
            print("WARNING: no whitespace after any terminating punctuation in this paragraph. Adding some, so that the parser won't have problems.")
            self.text = rep




    def ProcessSentences(self):
        """For the long paragraphs, split into sentences and measure the length of each."""
        nostopcount = 0
        stopchars = [".","?","!"]
        newtext = ""
        insertstop = False

        non_terminating_punct = [",",":",";"]
        insert_punct_immediately = False

        #Checking also if no punctuation at all (including non-terminating punctuation)
        pat = re.compile("[{}]".format("".join(non_terminating_punct)))
        how_many_non_term = len(pat.findall(self.text))
        try:
            non_term_ratio = int(len(self.text) / how_many_non_term)
            if non_term_ratio > Paragraph.toomuch_characters_per_sentence - 100:
                #If can't detect enough non-terminating puncts either, force punctuation at first possible occasion
                insert_punct_immediately = True
        except ZeroDivisionError:
            print("NOTE: No non-terminating punctuation marks at all in this paragraph.")
            insert_punct_immediately = True


        for ch_idx, char in enumerate(self.text):
            if char not in stopchars:
                nostopcount += 1
            else:
                if ch_idx > 1 and ch_idx < len(self.text)-1:
                    #Don't count if no white space after
                    if not re.search(r"\s", self.text[ch_idx + 1]):
                        nostopcount += 1
                    else:
                        nostopcount = 0
                else:
                    nostopcount = 0

            if nostopcount > Paragraph.toomuch_characters_per_sentence:
                insertstop = True

            if  (
                    insertstop and (
                        char in non_terminating_punct or
                        (insert_punct_immediately and char==" ") or 
                        nostopcount > 1100
                    )
                ):
                #Add a full stop if maximum sentence length by characters exceeded
                #(do the adding at the next COMMA/semicolon/colon)
                insertstop = False
                char = ". "
                nostopcount = 0

            newtext += char

        if newtext != self.text:
            LogLongParagraph(self.text, newtext)
            msg = "Inserted some full stops because the sentences were too long to parse. Check out longsentencelog.txt!"
            try:
                logging.warning(msg)
            except NameError:
                print(msg)
        else:
            msg = "Checked the text. Probably no reason to worry: it is split into sentences with reasonable lengths.\n"
            #msg += "({} consecutive chars without terminating punctuation of total {})\n".format(nostopcount, len(self.text))
            msg += "If you want to check it out, take a look at /tmp/long_sent_ok.log"
            try:
                logging.warning(msg)
            except NameError:
                print(msg)
            with open("/tmp/long_sent_ok.log","a") as f:
                f.write(self.text)
        self.text = newtext

def FilterByCharCount(rawtext, filename, predefined_paragraphs=False, split_pattern="\n\n"):
    """

    - predefined_paragraphs: if paragraphs already defined
    - the pattern by which the p's have been marked

    """

    Paragraph.filename = filename
    with open("/tmp/long_sent_ok.log","w") as f:
        f.write(filename + "\n\n")

    if predefined_paragraphs:
        paragraphs = rawtext.split(split_pattern)
    else:
        # Split the text into paragraphs
        paragraphs = re.split(r"\n{2,}", rawtext)

    processed = ""
    for p in paragraphs:
        p_object = Paragraph(p)
        if p_object.IsThisParagraphLong():
            #Only if the paragraph is longer than the threshold, process the sentences
            p_object.ProcessSentences()
        if p_object.length > 100:
            #if loonger than 20 words, check for white space + punctuation
            p_object.FilterPunctuationMarkWithNoSpaces()
        processed += split_pattern + p_object.text

    return processed
