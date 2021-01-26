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
#$ -pe smp 12       # These are the number of smp cores required to run
#$ -l m_mem_free=6g # memory requested for each core
#$ -l h_rt=172800  # memory requested for each core
#$ -binding linear:12
#$ -j y
#$ -V
#$ -q default.q         # specify queuename here
#$ -m beas              # send email when job starts,ends,aborted or suspended  
#$ -o SgeLogDir
#$ -e SgeLogDir
#$ -M %%{email}%%       # use your email address
workdir=`pwd`

time AlignerCommandLine 

EXITCODE=$?

if [ "$EXITCODE" == 0 ]
then
        echo "Aligner command AlignerCommandLine" >>$workdir/successful_aligner_runs.txt
else
        echo "Aligner command AlignerCommandLine" >>$workdir/failed_aligner_runs.txt
fi





