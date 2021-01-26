#!/bin/env python
import pandas as pd
import os
import sys
import glob
from itertools import islice
outfilename=''
sample_name=''
transcript_readfile=sys.argv[1].strip()
umi_readfile=sys.argv[2].strip()
outfilename=sys.argv[3].strip()
if os.path.exists(transcript_readfile) and os.path.exists(umi_readfile) and outfilename != '':
	pass
else:
	print "Error: umi and transcript read files dont exist"
	exit(1)

umi_fh=open(umi_readfile,"rb")
out_fh=open(outfilename,"w")
n=4
with open(transcript_readfile,"rb") as transcripts_fh:
	 while True:
	 	next_tr_lines = list(islice(transcripts_fh, n))
	 	next_umi_lines = list(islice(umi_fh, n))
        	if not next_tr_lines:
            		break
         	readnames=next_tr_lines[0].strip().split()
	 	out_fh.write(readnames[0] + ":" + next_umi_lines[1].strip() + " " + readnames[-1] + "\n")	
	 	out_fh.write(next_tr_lines[1])	
	 	out_fh.write(next_tr_lines[2])	
	 	out_fh.write(next_tr_lines[3])	
out_fh.close()
