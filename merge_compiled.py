#!/bin/env python
import pandas as pd
import os
import sys
import glob
files_path=sys.argv[1]
sample_name=sys.argv[2]

files_arr=glob.glob(files_path + "*compiled_results.dat")
#print files_arr
dff_final=pd.DataFrame()
for i in range(0,len(files_arr)):
	#print i
	dff = pd.read_csv(files_arr[i], sep="\t")
	dff.reset_index(inplace=True)
	dff.set_index(['index','Gene'], inplace=True)
	if i==0:
		dff_final = dff
	else:
		dff_final = dff_final.add(dff, axis=1)
dff_final.to_csv(files_path + "/" + sample_name + "_final_compiled_results.dat",sep="\t")
