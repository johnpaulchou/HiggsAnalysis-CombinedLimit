#!/bin/env python3

import sys
import tempfile
import subprocess
import pathlib
import os
import argparse
import makeworkspace as sf


###### main function ######
def main():
    cardname = "combine.txt"
    newfilenames = []

    for ptbin in sf.ptbins:

        oldfile = open(cardname, "r")
        newfile = tempfile.NamedTemporaryFile(delete=False, mode='wt', dir='.')
        path = pathlib.Path(newfile.name)
        newfilenames.append(path.name)
        for line in oldfile:
            newline=line.replace("BIN",ptbin)
            newfile.write(newline)
        newfile.close()
        oldfile.close()

    runexec= ["combineCards.py"]
    runexec.extend(newfilenames)
    with open("newcard.txt","w") as outfile:
        subprocess.run(runexec,stdout=outfile)

    # delete the files
    for tfiles in newfilenames:
        os.remove(tfiles)
###### main function ######

if __name__ == "__main__":
    main()
