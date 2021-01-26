bamfile=$1
readfile_umi=$2
gene_to_pos_file=$3
outdir=$4
outbasename=$5
UMIQUANT_HOME=$6

samfile=`basename $bamfile .bam`.sam
echo " converting bam to sam $bamfile"
echo "samtools view -h $bamfile > ${samfile}"
time samtools view -h $bamfile > ${samfile}
EXITCODE=$?
if [ "$EXITCODE" == 0 ]; then echo "BAM to SAM conversion Done!"; else echo "Error:  bam to sam conversion Failed!" ; exit 1 ; fi
echo "----------------------------------"
echo "Counting umi "
echo "python $UMIQUANT_HOME/sc_funcs_STAR_combined.py  $readfile_umi $gene_to_pos_file $outbasename $outdir $samfile"
time python $UMIQUANT_HOME/sc_funcs_STAR_combined.py  $readfile_umi $gene_to_pos_file $outbasename $outdir $samfile
if [ -e $samfile ]
then
	echo "removing temp $samfile"
	rm $samfile
fi
EXITCODE=$?
if [ "$EXITCODE" == 0 ]; then echo "UMI count Done!"; else echo "Error:  UMI count Failed!" ; exit 1 ; fi
echo "----------------------------------"

