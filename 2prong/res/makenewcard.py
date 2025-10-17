#!/bin/env python3

import files
import sys
import tempfile
import subprocess
import pathlib
import os
import argparse

###### main function ######
if __name__ == "__main__":
    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--sigtype",help="signal type that we're using",choices=files.sigtypes, default=files.sigtypes[0])
    parser.add_argument("--region",help="region that we're working in",choices=files.regions, default=files.regions[0])
    parser.add_argument("--binning",help="binning strategy selection", default=1)
    args=parser.parse_args()

    cardname = "combine.txt"
    newfilenames = []

    # skip the first two bins if we're doing the control region
    for bin in range(files.get_num_m2pbins(args.region, args.sigtype, args.binning)):
        for eta in files.etabins:
            oldfile = open(cardname, "r")
            newfile = tempfile.NamedTemporaryFile(delete=False, mode='wt', dir='.')
            path = pathlib.Path(newfile.name)
            newfilenames.append(path.name)
            for line in oldfile:
                newline=line.replace("BIN","bin"+str(bin)+eta)
                newline=newline.replace("SIGWS",files.sigworkspacefn)
                newline=newline.replace("BKGWS",files.bkgworkspacefn)
                newline=newline.replace("LUMI",str(files.luminosity))
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
