#!/bin/env python3

import sys
import tempfile
import subprocess
import pathlib
import os
import argparse
import makeworkspace as ws


###### main function ######
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--imass",help="signal mass index (0-"+str(len(ws.sigmasses)-1)+")", choices=range(len(ws.sigmasses)), type=int)
    args=parser.parse_args()
    
    cardname = "combine.txt"
    newfilenames = []

    for ptbin in ws.ptbins:
        for btagbin in ws.btagbins:

            oldfile = open(cardname, "r")
            newfile = tempfile.NamedTemporaryFile(delete=False, mode='wt', dir='.')
            path = pathlib.Path(newfile.name)
            newfilenames.append(path.name)
            for line in oldfile:
                newline=line.replace("BIN",btagbin+"_"+ptbin)
                newline=newline.replace("LUMI","1.0")
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



