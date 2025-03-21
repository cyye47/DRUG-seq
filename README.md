Package Requirements:
These should be in your path:
python, samtools, bamtools,bash environment

Read and executable access to files in /usr/prog/ns/ngs_workflow_templates/countumi/ directory

How to run:
bash-4.1$ /usr/prog/ns/ngs_workflow_templates/countumi/run_umi_workflow.sh  -h

Usage: run_umi_workflow.sh
        -i  <comma separated file containing  [file_path,transcript_read_file,umi_read_file,reference_env_file], required. Provide one such line for eachsample>        
	-e <use your novartis email_id, required>
        -o <output directory, default: current directory>
        -s <scripts directory path, default: /usr/prog/ns/ngs_workflow_templates/countumi>
        -f <number of bases to clip from five prime end (for star aligner), default: 5>
        -t <number of bases to clip from three prime end (for star aligner), default: 1>


More information:

Input file content. [ -i option]  

Here, each line in the file represents one sample, requires four comma separated fields.
1)input file path where fastq files are. Example: /usr/prog/ns/ngs_workflow_templates/countumi
2)fastq name of the trascript read file. Example : drug_seq_384_200000_R2.fastq
3)fastq name of the umi-bacode read file. Example: drug_seq_384_200000_R1.fastq
4)Reference environemnt file containing star index, gene_pos.dat file information etc. Example: /usr/prog/ns/ngs_workflow_templates/countumi/star_ref_env.sh

Inside "input_text.txt" will look like
/usr/prog/ns/ngs_workflow_templates/countumi,drug_seq_384_200000_R2.fastq,drug_seq_384_200000_R1.fastq,/usr/prog/ns/ngs_workflow_templates/countumi/star_ref_env.sh
/usr/prog/ns/ngs_workflow_templates/countumi,drug_seq_400_R2.fastq,drug_seq_400_R1.fastq,/usr/prog/ns/ngs_workflow_templates/countumi/star_ref_env.sh

email id [ -e option]
example: abc@gmail.com
-------------------------------------------------------------

output directory [-o option]
example: /XXX/umidemo 

Script will generate "/clscratch/kulkatr1/umidemo" directory and output goes under it. If this directory already exists then it will give error and come out. Either delete directory or provide different name. 
for example: /XXX/umidemo1
-------------------------------------------------------------

Script base [-s option]
This is a directory path where all the accessory scripts and sge/cluster automation templates required by the workflow are situated. 
Default script base: /usr/prog/ns/ngs_workflow_templates/countumi/ 

If you decide to modify script for different use case, then those scripts can sit in a different directory and upon run pass the information to -s option

for example:
-s ~/testing_myown_scriptbase


Command line looks like:

/usr/prog/ns/ngs_workflow_templates/countumi/run_umi_workflow.sh  -i /usr/prog/ns/ngs_workflow_templates/countumi/input_test.txt  -e abc@gmail.com -o /XXX/demo -f 5 -t 1



#to merge the result .dat file

cat *results*.dat |  grep -v Gene  | sort --key 1 >final_compile_results.dat

#append header line in final results manually. 

 
<<<<<<< HEAD
=======

>>>>>>> 9a1178050bb0286d5e6801b5b0f62d35003e9c73
