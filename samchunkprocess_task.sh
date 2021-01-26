#!/bin/sh
########################################
#                                      #
# SGE MPI job script for NIBR Cluster  #
#                                      #
########################################

# Grid Engine options
#$ -N SampleName
#$ -cwd
#$ -S /bin/bash
#$ -pe smp 1       # These are the number of smp cores required to run
#$ -l m_mem_free=10g # memory requested for each core
#$ -l h_rt=172800  # memory requested for each core
#$ -binding linear:1
#$ -j y
#$ -V
#$ -q default.q         # specify queuename here
#$ -m beas              # send email when job starts,ends,aborted or suspended  
#$ -M tripti.kulkarni@novartis.com       # use your email address
##$ -t 1-%%{numbamchunks}%%
#$ -o SgeLogDir
#$ -e SgeLogDir
#$ -t 1-477
inpfile=BamSplitFiles
workdir=`pwd`
IFS=$'\n'
inparr=( $( cat $inpfile ) )
BamChunkFile=${inparr[$SGE_TASK_ID-1]}

if [ -e BamChunkFile ]
        then
	time ChunkCommandLine
	EXITCODE=$?

	if [ "$EXITCODE" == 0 ]
	then
        	echo "Umi counts BamChunkFile" >>$workdir/successful_umicount_runs.txt
	else
		echo "Umi counts BamChunkFile" >>$workdir/failed_umicount_runs.txt
	fi
else
	        echo "No bam file BamChunkFile"
fi
