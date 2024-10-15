#!/bin/env python3

import sys
import tempfile
import subprocess
import pathlib
import os
import makeworkspace as ws


###### main function ######
def main():
    cardname = "combine.txt"
    newfilenames = []

    for ptbin in ws.ptbins:
        for btagbin in ws.btagbins:

            if ptbin!=ws.ptbins[0]: continue
            
            oldfile = open(cardname, "r")
            newfile = tempfile.NamedTemporaryFile(delete=False, mode='wt', dir='.')
            path = pathlib.Path(newfile.name)
            newfilenames.append(path.name)
            for line in oldfile:
                newline=line.replace("BIN",btagbin+"_"+ptbin)
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



