#!/usr/bin/env python
### cut a fasta query (arg1) in "nbPart" (arg3)
### subFasta files and launches a blast programm (arg4)
### vs the bank (arg2) for each subfasta and then
### concatenates the tab delimited blast results in
### one file. You can add any additional blastall option in the
### arg5 with quotes like this : "-e 0.001 -a 2 -W 5"
### example of execution :
### paraBlast.py query.fasta blastdb 10 tblastx "-e 0.001 -a 2 -W 5"


import string
import sys
import os
import subprocess
import tempfile
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from StringIO import StringIO

fastafile = sys.argv[1]
#fastafile = "/bank/fasta/Roth/E1.454.fasta"
bank = sys.argv[2]
#bank = "/bank/blastdb/E1"
nbPart=int(sys.argv[3])
#nbPart=int(5)
my_blast_prog = sys.argv[4]
#my_blast_prog = "tblastx"
blastOpt=sys.argv[5]
#blastOpt="-e 0.001 -a 2 -W 5"
my_blast_exe = "/usr/local/bin/blast/bin/blastall"


nbResidues=0
meanLen=0
nbSeqs=0
seqs=[]


#### reading the fasta file to cut
handle = open(fastafile)

for seq_record in SeqIO.parse(handle, "fasta"):
	seqs.append(seq_record)
	nbSeqs+=1
	nbResidues+=len(seq_record.seq)

handle.close()

#### prints some infos about the input fasta file
meanLen=nbResidues/nbSeqs

print "sequences -- residues -- mean sequence length"
print nbSeqs,"--",nbResidues,"--", meanLen

#### creates a temp directory and
#### writes the divided-input fasta files into it
wDir= "/scratch/USERS/prestat"
tmpDir=tempfile.mkdtemp(prefix="parablast",dir= wDir)

nbSeqsbyfile=nbSeqs/nbPart
modulo=nbSeqs%nbPart
iteSeqs=0
for i in range(0,nbPart-1):
	tmpFasta=tempfile.mkstemp(dir=tmpDir,suffix="."+str(i)+".fasta")
	SeqIO.write(seqs[iteSeqs:iteSeqs+nbSeqsbyfile], tmpFasta[1], "fasta")
	iteSeqs+=nbSeqsbyfile

tmpFasta=tempfile.mkstemp(dir=tmpDir,suffix="."+str(nbPart)+".fasta")
SeqIO.write(seqs[iteSeqs:nbSeqs], tmpFasta[1], "fasta")

#### runs the blast
my_blast_files = os.listdir(tmpDir)
myProcesses=[]
for blast_file in my_blast_files:
	cmd= "blastall -m 8"+" "+ " "+\
		"-p"+" "+ my_blast_prog + " "+\
		"-i"+" "+ tmpDir+"/"+blast_file + " "+\
		"-d"+" "+ bank + " "+\
		"-o"+" "+ tmpDir+"/"+blast_file.replace("fasta","blast") + " "+\
		blastOpt
	myProcesses.append(subprocess.Popen(cmd,shell=True))

#### waits for the end of all processes
for i in myProcesses:
	i.wait()

#### concatenates the blast files results
#### and removes the temp files used
os.system("cat " + tmpDir+"/"+"*.blast > "+ wDir + '/' + str.split(fastafile,'/')[-1]+".vs."+str.split(bank,'/')[-1]+".blast")
os.system("rm -rf "+ tmpDir)















