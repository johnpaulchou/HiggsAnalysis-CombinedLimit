#!/usr/bin/env python3

import sys
import subprocess
import shutil
import sys
import tempfile
import pathlib
import os

import makesigworkspace as ws

# omega and phi mass points to run over
wmasspoints = (1.0, 1.5, 2.0)
pmasspoints = (1000, 1500, 2000, 2500)

if len(sys.argv)<2:
    print("Didn't pass an argument: run.py JobId")
    exit(1)
jobid = int(sys.argv[1])

### function to make the combine card
def makecard(wmass, pmass):
    cardname = "combine.txt"
    newfilenames = []

    # skip the first two bins if we're doing the control region
    for bin in range(3,26):
        binstr=str(bin)
        for eta in ["B","E"]:
            oldfile = open(cardname, "r")
            newfile = tempfile.NamedTemporaryFile(delete=False, mode='wt', dir='.')
            path = pathlib.Path(newfile.name)
            newfilenames.append(path.name)
            for line in oldfile:
                newline=line.replace("BIN","bin"+binstr+eta)
                newline=newline.replace("PMASS",str(pmass))
                newline=newline.replace("WMASS",str(wmass))
                newfile.write(newline)
            newfile.close()
            oldfile.close()

    runexec= ["combineCards.py"]
    runexec.extend(newfilenames)
    print(runexec)
    with open("newcard.txt","w") as outfile:
        subprocess.run(runexec,stdout=outfile)

    # delete the files
    for files in newfilenames:
        os.remove(files)
### end makecard()


# make the signal workspace followed by the card
cntr=0
for wmasspnt in wmasspoints:
    for pmasspnt in pmasspoints:
        cntr=cntr+1
        if cntr==jobid:
            ws.main(wmasspnt, pmasspnt)
            makecard(wmasspnt, pmasspnt)
            # combine -M AsymptoticLimits newcard.txt
