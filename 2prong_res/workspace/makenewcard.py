#!/bin/env python3

import files
import sys
import tempfile
import subprocess
import pathlib
import os


###### main function ######
def main(wmass, pmass):
    cardname = "combine.txt"
    newfilenames = []

    # skip the first two bins if we're doing the control region
#    for bin in range(1,26):
    for bin in range(3,26):
        binstr=str(bin)
        for eta in ["B","E"]:
            oldfile = open(cardname, "r")
            newfile = tempfile.NamedTemporaryFile(delete=False, mode='wt', dir='.')
            path = pathlib.Path(newfile.name)
            newfilenames.append(path.name)
            for line in oldfile:
                newline=line.replace("BIN","bin"+binstr+eta)
                newline=newline.replace("WORKSPACEFILE",files.sigworkspacefn(wmass,pmass))
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
    if len(sys.argv)<3:
        print("makenewcard.py wmass pmass")
        exit(1)
    
    main(float(sys.argv[1]), float(sys.argv[2]))



