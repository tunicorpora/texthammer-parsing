#Fix the tokenization of icelandic texts: the punctuation is by default not right.
import sys
import subprocess
import re

with open(sys.argv[1],"r") as f:
    text = f.read()

lines = ""
punctuation = r"\.,!\?:;\(\)\"\'"
parseraddress = "/home/textmine/parserit/IceNLPCore/bat/icetagger/"

print("Fixing the tokenization process for icelandic, this may take a while...")
for idx, line in enumerate(text.splitlines()):
    print("{}/{}".format(idx,len(text.splitlines())))
    if re.search("^[^" + punctuation  + "]+[" + punctuation + "]", line):
        word = re.search(r"[^" + punctuation + r"\s]+", line).group(0)
        with open(parseraddress + "input.txt", "w") as f:
            f.write(word)
        print("Parsing {}\r".format(word))
        subprocess.call(["sh","icetagger.sh", "-i","input.txt","-o","output.txt","-lem"],cwd=parseraddress,stdout=subprocess.DEVNULL)
        with open(parseraddress + "output.txt", "r") as f:
            word = f.read()
        lines += word.strip() + "\n"
        lines += "{} punct punct \n".format(re.search("[" + punctuation + "]", line).group(0))
    else: 
        lines += line + "\n"


with open(sys.argv[1],"w") as f:
    f.write(lines)

print("\nDone.")
