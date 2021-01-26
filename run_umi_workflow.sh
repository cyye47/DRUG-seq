#!/bin/sh
PROG_NAME="run_umi_workflow.sh"
runDir=`pwd`/umicount_workdir
UMIQUANT_HOME="/usr/prog/ns/ngs_workflow_templates/countumi"
emailid=''
CLIP5P=5
CLIP3P=1
usage() { echo "Usage: $PROG_NAME
        -i  <comma separated file containing  [file_path,transcript_read_file,umi_read_file,reference_env_file], required. Provide one such line for eachsample>        
	-e <use your novartis emailid, required>
        -o <output directory, default: current directory>
        -s <scripts directory path, default: /usr/prog/ns/ngs_workflow_templates/countumi>
        -f <number of bases to clip from five prime end (for star aligner), default: 5>
        -t <number of bases to clip from three prime end (for star aligner), default: 1>"
	 1>&2; exit 1; }

while getopts "i:e:o:s:f:t:" opt; do

    case ${opt} in

        i)
            inputFile=$(readlink -f ${OPTARG})
            ;;
        e)
            emailid=${OPTARG}
            ;;

        o)
           runDir=$(readlink -f ${OPTARG})
            ;;

        s)
            UMIQUANT_HOME=$(readlink -f ${OPTARG})
            ;;
        b)
            CLIP5P=${OPTARG}
            ;;
        e)
            CLIP3P=${OPTARG}
            ;;

        *)
            usage
            ;;

    esac

done

shift $((OPTIND-1))


if [ -e $inputFile ]
        then
                numTiffs=$( wc -l $inputFile  | tr ' ' '\n' | head -n 1)
        else
                echo "Error: Inputfile not found : $inputFile "
                exit
fi

if [ -z "$emailid" ]
	then 
		echo " Error: No novartis email id provided for job notifications"
		exit
fi
	
outputpath=`dirname $runDir`
if [ -e $outputpath ]
        then
                if [ -e $runDir ]
                        then
                        echo "Error: Outputdirectory: $runDir exists "
			exit
                else
                	mkdir -p $runDir
			if [ -e $runDir ]
			then
                        	echo "Outputdirectory: $runDir created successfully"
			else
			
                        	echo "Error: Could not create output directory $runDir"
				exit
			fi
                fi
			
        else
                 echo "Error: Invalid output path $outputpath"
		 exit
fi



if [ -e $UMIQUANT_HOME ]
        then
                echo "script base: $UMIQUANT_HOME"
		if [ -e $UMIQUANT_HOME/run_star.sh -a -e $UMIQUANT_HOME/umicount.sh -a -e $UMIQUANT_HOME/samchunkprocess_task.sh -a -e $UMIQUANT_HOME/aligner_task.sh -a -e $UMIQUANT_HOME/sc_funcs_STAR_combined.py -a -e $UMIQUANT_HOME/readname_change.py ]
		then
			echo "Found all scripts!"
		else
			echo "Error: did not find all scripts"
			exit
		fi
        else
                echo "Error: script directory not found : $UMIQUANT_HOME"
                exit
fi

which samtools  
EXITCODESAM=$?
which bamtools
EXITCODE=$?

if [ "$EXITCODE" == 0 ] ; then echo "bamtools found!"; else echo "Error: bamtools not found!" ; exit 1 ; fi
if [ "$EXITCODESAM" == 0 ] ; then echo "samtools found!"; else echo "Error: samtools not found!" ; exit 1 ; fi
IFS=$'\n'  ;  for i in `cat $inputFile `; 
do
	IFS=',' read -r -a inparr <<< "$i"
	#inparr=( $( echo $i ) )
	inppath=`echo ${inparr[0]} | sed -e s'| ||g'`
	readtranscript=`echo $inppath/${inparr[1]} | sed -e s'| ||g'`
	readumi=`echo $inppath/${inparr[2]} | sed -e s'| ||g'`
	refenv=`echo ${inparr[3]} | sed -e s'| ||g'`

	if [ -e "$inppath" -a -e "$readtranscript" -a -e "$readumi" -a -e "$refenv" ]
       	then
                echo
	else
		echo "Error: cannot access one or more input files"
		echo "Error: No input path | No readtranscript file | No readumi file | No refenv file"	
                exit
	fi
	filename=$(basename "$readtranscript")
	outbase="${filename%.*}"
	sampleoutdir=$runDir/$outbase
	mkdir $sampleoutdir
        sgelogdir=$sampleoutdir/sgelogs
        mkdir $sgelogdir
	outprefix=$sampleoutdir/$outbase
	IFS=$'\n'
	cp $UMIQUANT_HOME/samchunkprocess_task.sh $sampleoutdir/
	cp $UMIQUANT_HOME/aligner_task.sh $sampleoutdir/
	source $refenv
	AlignerCommand="$UMIQUANT_HOME/run_star.sh $readtranscript $readumi $refenv $outprefix $UMIQUANT_HOME $CLIP5P $CLIP3P" 
	sed -i s'|AlignerCommandLine|'$AlignerCommand'|' $sampleoutdir/aligner_task.sh
	sed -i s'|%%{email}%%|'$emailid'|' $sampleoutdir/aligner_task.sh
	sed -i s'|SampleName|'$outbase'|' $sampleoutdir/aligner_task.sh
	sed -i s'|SgeLogDir|'$sgelogdir'|' $sampleoutdir/aligner_task.sh
	umicountcmd="$UMIQUANT_HOME/umicount.sh BamChunkFile $readumi $REF_GENE_POS $sampleoutdir $outbase $UMIQUANT_HOME"
	bamsplitlist="$sampleoutdir/$outbase"_bamsplit.list
	sed -i s'|ChunkCommandLine|'$umicountcmd'|' $sampleoutdir/samchunkprocess_task.sh
	sed -i s'| BamChunkFile| $BamChunkFile|' $sampleoutdir/samchunkprocess_task.sh
	sed -i s'|BamSplitFiles|'$bamsplitlist'|' $sampleoutdir/samchunkprocess_task.sh
	sed -i s'|SampleName|'$outbase'|' $sampleoutdir/samchunkprocess_task.sh
	sed -i s'|SgeLogDir|'$sgelogdir'|' $sampleoutdir/samchunkprocess_task.sh

	cd $sampleoutdir; myjob=$(qsub aligner_task.sh |grep job | awk '{print $3}' | cut -d '.' -f1 )
	qsub  -hold_jid $myjob samchunkprocess_task.sh
	cd -
done
