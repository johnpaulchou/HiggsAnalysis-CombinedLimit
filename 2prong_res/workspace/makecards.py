import subprocess
import shutil

cardname = "combine.txt"
newfilenames = []

for bin in range(3,26):
#for bin in range(3,4):
    binstr=str(bin)
    for eta in ["B","E"]:
        oldfile = open(cardname, "r")
        newfilename = "../output/combine_"+binstr+eta+".txt"
        newfilenames.append(newfilename)
        newfile = open(newfilename,"w")
        for line in oldfile:
            newline = line.strip()
            newline=newline.replace("BIN","bin"+binstr+eta)
            newfile.write(newline+"\n")
        newfile.close()
        oldfile.close()

runexec= ["combineCards.py"]
runexec.extend(newfilenames)
with open("newcard.txt","w") as outfile:
    subprocess.run(runexec,stdout=outfile)
