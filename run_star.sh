readfile=$1
umifile=$2
ref_env_file=$3
outprefix=$4
UMIQUANT_HOME=$5
CLIP5P=$6
CLIP3P=$7
source $ref_env_file

#edit transcript readname to contain umi information
combined_fastq=$outprefix"_combined.fastq"
echo "Edit transcript readname to contain umi information"
echo "python $UMIQUANT_HOME/readname_change.py $readfile $umifile $combined_fastq"
time python $UMIQUANT_HOME/readname_change.py $readfile $umifile $combined_fastq
EXITCODE=$?

if [ "$EXITCODE" == 0 ]
then
	echo "Merging the UMI information in readname Done!"
else
        echo "Error: Merging the UMI information in readname Failed!"
	exit
fi
echo "----------------------------------"

echo "$STAR_EXEC  --runThreadN 12 --genomeLoad NoSharedMemory --outSAMunmapped Within --clip5pNbases  $CLIP5P  --clip3pNbases $CLIP3P  --genomeDir $REF_STAR  --outFilterMismatchNmax 3 --outFileNamePrefix $outprefix  --outSAMtype BAM Unsorted --readFilesIn  $combined_fastq"
time $STAR_EXEC  --runThreadN 12 --genomeLoad NoSharedMemory --outSAMunmapped Within --clip5pNbases  $CLIP5P  --clip3pNbases $CLIP3P  --genomeDir $REF_STAR  --outFilterMismatchNmax 3 --outFileNamePrefix $outprefix --outSAMtype BAM Unsorted --readFilesIn  $combined_fastq
EXITCODE=$?
if [ "$EXITCODE" == 0 ]
then
	echo "Alignment Done!"
else
	echo "Error: alignment Failed!"
	exit 1
fi
echo "----------------------------------"


#commenting out the section as STAR aligner can produce BAM files directly.
#echo "SAM to BAM conversion"
#echo $outprefix"Aligned.out.sam" 
#if [ -e $outprefix"Aligned.out.sam" ]
#then
#echo 'samtools view -bSh $outprefix"Aligned.out.sam" >$outprefix"Aligned.out.bam'
#time samtools view -bSh $outprefix"Aligned.out.sam" >$outprefix"Aligned.out.bam"
#EXITCODE=$?
#if [ "$EXITCODE" == 0 ]
#then
#	echo "SAM to BAM Done!" 	
#	if [ -e $outprefix"Aligned.out.bam" ]; then echo "Removing SAM file, keeping only BAM file"; rm $outprefix"Aligned.out.sam" ; fi
#else
#	echo "Error: SAM to BAM conversion Failed!"
#fi
#fi
#echo "----------------------------------"

echo "Split BAM file based on reference"
if [ -e $outprefix"Aligned.out.bam" ]
then
echo "bamtools split -in $outprefix"Aligned.out.bam"  -reference"
time bamtools split -in $outprefix"Aligned.out.bam"  -reference
ls $outprefix*REF*.bam >$outprefix"_bamsplit.list"
fi
EXITCODE=$?
if [ "$EXITCODE" == 0 ]; then echo "BAM split Done!" ; else echo "Error:  BAM split Failed!" ; exit 1 ; fi
echo "----------------------------------"

echo "Create bam list file for umi count taskarray"
numbams=`grep -c $ $outprefix"_bamsplit.list"`
echo "sed -i s'|%%{numbamchunks}%%|'$numbams'|' samchunkprocess_task.sh"
time sed -i s'|%%{numbamchunks}%%|'$numbams'|' samchunkprocess_task.sh
EXITCODE=$?
if [ "$EXITCODE" == 0 ]; then echo "Creating BAM list file Done!" ; else echo "Error:  Creating BAM list file Failed!" ; exit 1 ; fi
echo "----------------------------------"
