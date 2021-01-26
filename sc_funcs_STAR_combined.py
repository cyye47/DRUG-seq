#!/usr/bin/python
import sys
import os
from os.path import basename
import pickle, cPickle


readfilename = sys.argv[1].strip()
geneinfofilename=sys.argv[2].strip()
out_basename = sys.argv[3].strip()
dirhead = os.path.abspath(sys.argv[4].strip())
samfilename=os.path.abspath(sys.argv[5].strip())
spikeinfilename=''

def get_gene_coordinates(geneinfofilename,dirhead,samfilename):
	print "In get_gene_coordinates"
	print geneinfofilename
	#fetch which chromosome the file belongs to based on samfilename
	refchr=(samfilename.split("REF_")[-1]).replace(".sam",'')
	if geneinfofilename=='':
		geneinfofilename='gene_start_stop.dat'
	gene_key=[]
	gene_to_count={}
	pos_to_gene={}
	count=0
	genefile=open(geneinfofilename,'r')
	line=genefile.readline()
	while line:
		splitvals=line.split()
		chrval=splitvals[0]	
		if chrval == refchr:
			gene=splitvals[5]
			orient='p'
			if splitvals[1]=='-':
				orient='n'
			chrval=splitvals[0]	
			startcoords=splitvals[3].split(',')
			stopcoords=splitvals[4].split(',')
			gene_val=(orient,chrval)
			if not(gene_val in pos_to_gene):
				pos_to_gene[gene_val]={}
			for exon in range(len(startcoords)):
				if startcoords[exon]!='':
					pos_to_gene[gene_val][(int(startcoords[exon]),int(stopcoords[exon]))]=count # changed into tuple key to save memory, need to be sorted
				#print(str(count) + ' ' + chrval + ' ' + gene)
			gene_key.append(gene+","+chrval)
			count=count+1
		line=genefile.readline()
	genefile.close()
	pos_to_gene['gene_key']=gene_key
	count=0
	for key in gene_key:
		count+=1
	print count, "total genes"
	return(pos_to_gene)
	
	
def get_umis_to_gene_seq(samfilename,spikeinfilename,readfilename,dirhead, pos_to_gene,barcodes):
	gene_key=pos_to_gene['gene_key']
	print " In function get_umis_to_gene_seq"
	print samfilename,spikeinfilename,readfilename,dirhead, len(pos_to_gene),len(barcodes)
	all_genes={}
	all_barcodes={}
	read_umis={}
	read_barcodes={}
	print "length gene_key", len(gene_key)
	print "length barcodes", len(barcodes)
	for key in range(len(gene_key)):
		all_genes[gene_key[key]]={}
		for bc in barcodes:
			all_genes[gene_key[key]][bc]={}
	for bc in barcodes:
		all_barcodes[bc]=1
	'''readfile=open(readfilename,'r')
	line=readfile.readline()
	while line:
		lin=line.split()
		name=lin[0].replace('@','')
		name=name.replace('/1','')
		line2=readfile.readline()
		line3=readfile.readline()
		line4=readfile.readline()
		bc=line2[0:10]
		if bc in all_barcodes:
			read_umis[name]=line2[10:20]
			read_barcodes[name]=bc
		line=readfile.readline()
	readfile.close()	
	'''
	totreads=len(read_umis)
	samfile=open(samfilename,'r')
        file_basename = os.path.basename(samfilename) 
	#output=open("compare_all_genes_initial.p",'wb')
       	#cPickle.dump(all_genes,output,protocol=cPickle.HIGHEST_PROTOCOL )
	#output.close()
	count=1
	for line in samfile:
		if line[0]!='@':
			count=count+1
			lin=line.split()
			namefield = lin[0].rsplit(":",1)
			name=namefield[0].replace('@','')
			name=name.replace('/1','')
			bc = namefield[-1][0:10]
			if bc in all_barcodes:
				read_umis[name]=namefield[-1][10:20]
				read_barcodes[name]=bc
			if (lin[1]=='0' or lin[1]=='16'):	#primary alignment
				if name in read_umis:
					chromval=lin[2]
					orient='p'
					if (lin[1]=='16'):
						orient='n'
					gene_val=(orient,chromval)
					if gene_val in pos_to_gene:
						lin[3]=int(lin[3])
						for cor_key in pos_to_gene[gene_val]:
							if (lin[3] >= cor_key[0]) & (lin[3] <= cor_key[1]):
								geneindex=pos_to_gene[gene_val][cor_key]
								gene=gene_key[geneindex]
								umi=read_umis[name]
								barcode=read_barcodes[name]
								if umi in all_genes[gene][barcode]:
									if lin[3] in all_genes[gene][barcode][umi]:
										all_genes[gene][barcode][umi][lin[3]] += 1
									else:
										all_genes[gene][barcode][umi][lin[3]]=1
								else:
									all_genes[gene][barcode][umi]={}
									all_genes[gene][barcode][umi][lin[3]]=1
								break
	samfile.close()
	
	
	for bckey in all_barcodes:
		outfilename=dirhead + '/' + file_basename+ bckey + '.fastq.processed'
		outfile=open(outfilename,'w')
		for gene in sorted(all_genes.iterkeys()):
			outfile.write('Gene : ' + gene + '\n')
			barcodes_for_gene=all_genes[gene]
			umis_for_gene=all_genes[gene][bckey]
			for key in sorted(umis_for_gene.iterkeys()):
				outfile.write(key + '\t')
				for key2 in sorted(umis_for_gene[key].iterkeys()):
					outfile.write(str(key2) + ' (' + str(umis_for_gene[key][key2]) + ')\t')
				outfile.write('\n')
		outfile.close()

def quantify_genes(dirhead,samfilename,out_basename):
	print "In quantify_genes"
        file_basename = os.path.basename(samfilename) 
	os.system('ls ' + dirhead + '/' +  file_basename + '*.fastq.processed > ' + dirhead + '/' + file_basename + 'filelist.dat')
	datafile=open(dirhead + '/' + file_basename + 'filelist.dat','r')

	filenames=[]
	readcount_all={}
	umicount_all={}
	umicount_filtered_all={}
	aa=0
	line=datafile.readline()
	while line:
		line=line.rstrip()
		filenames.append(line)
		infile=open(line,'r')
		readcount={}
		umicount={}
		umicount_filtered={}
		for line2 in infile:
			lin=line2.split()

			if lin[0]=='Gene':
				genename=lin[2]
				readcount[genename]=0
				umicount[genename]=0
				umicount_filtered[genename]=0
			else:
				numreads=0
				startpos=(len(lin)-1)/2
				for bb in range(0,startpos):
					countind=(bb+1)*2
					numreads=lin[countind]
					numreads=numreads.replace('(','')
					numreads=numreads.replace(')','')
					numreads=int(numreads)
					readcount[genename]=readcount[genename]+numreads
					umicount[genename]=umicount[genename]+1
					#if numreads>1:
				umicount_filtered[genename]=umicount_filtered[genename]+1
	
		infile.close()
		readcount_all[aa]=readcount
		umicount_all[aa]=umicount
		umicount_filtered_all[aa]=umicount_filtered
		aa=aa+1
		line=datafile.readline()

	numfiles=aa


	outfile=open(dirhead + '/'+ file_basename + '_compiled_results.dat','w')
	outfile.write('Gene')
	for aa in range(0,numfiles):
		barcode=filenames[aa]
		barcode=filenames[aa].split('/')[-1]
		barcode=barcode.split(".sam")[-1]
		#barcode=out_basename + barcode.replace('.fastq.processed','')
		barcode= barcode.replace('.fastq.processed','')
		#outfile.write('\tReads_'+barcode+'\tUMI_'+barcode+'\tUMI_filtered_'+barcode)
		outfile.write('\tReads_'+barcode+'\tUMI_'+barcode) # no longer need to monitor different UMI but with same transcript start site
	outfile.write('\n')
	for key in sorted(readcount_all[0].iterkeys()):
		outfile.write(key)
		for aa in range(0,numfiles):
			#outfile.write('\t' + str(readcount_all[aa][key]) + '\t' + str(umicount_all[aa][key]) + '\t' + str(umicount_filtered_all[aa][key]))
			outfile.write('\t' + str(readcount_all[aa][key]) + '\t' + str(umicount_all[aa][key])) # no longer need to monitor different UMI but with same transcript start site
		outfile.write('\n')
	runstring = 'rm ' + dirhead + '/' +file_basename + '*.fastq.processed'
        os.system(runstring)
        runstring = 'rm ' + dirhead + '/' +file_basename + 'filelist.dat'
        os.system(runstring)
	outfile.close()		
####END FUNCTION DEFINITIONS
barcodes = ['AACAAGGTAC','AACAATCAGG','AACATGGAGA','AACATTACCG','AACCGCGACT','AACCGGAAGG','AACCTCATAG','AACGTAAGCT','AAGACGGATT','AAGATCGGCG',\
'AAGCGATGTT','AAGCGTTCAG','AAGGTCTGGA','AAGTTAGCGC','AATAGCCACA','AATCACGCGA','AACACCTAGT','AACAGGCAAT','AACCAGCCAG','AACCAGTTGA','AACCGGCGTA',\
'AACCTAGTCC','AACTCTACAC','AACTGTGTCA','AAGATGTCCA','AAGCATATGG','AAGCTCACCT','AAGGCATGCG','AAGTTCCTTG','AATACCGGTA','AATCCATCTG','AATCCGCTCC',\
'AATCCTACCA','AATCGTCCGC','AATGAGAGCA','AATGTCAGTG','ACAACAGTCG','ACAACCATAC','ACACAATCTC','ACACAGTGAA','ACACGGTCCT','ACACTTGCTG','ACCAGGACCA',\
'ACCATAACAC','ACCGGTACAG','ACCGTACTTC','ACCTGTCCGA','ACCTTATGTG','AATGAACACG','AATGACCTTC','AATTAGGCCG','AATTGCGATG','ACAACGGAGC','ACAAGCGCGA',\
'ACACCGAATT','ACACGCAGTA','ACAGTGCCAA','ACATGTGTGC','ACCGAACCGT','ACCGAGAGTC','ACCTCCGACA','ACCTCTCTCC','ACGAATGACA','ACGCCTCAAC','ACGCCTTCGT',\
'ACGCTGGATA','ACGTGCTGAT','ACTCCAAGCC','ACTTAACTGC','ACTTCATCAC','ACTTGAGGAA','ACTTGTAAGG','AGACCGTTAT','AGACTAGCAT','AGAGTGTAAC','AGAGTTCTGC',\
'AGCATGTCAT','AGCCACTAGC','AGCGATAACG','AGCGTACAAT','ACGGTCCGTT','ACGTAGGCAC','ACTGGCGCAT','ACTGGCTTCC','ACTTCGTTGA','ACTTCTCCTG','AGAACCACGG',\
'AGAAGCAATC','AGAGATGCAG','AGAGCTTACA','AGATAGTGCT','AGCAATGCGC','AGCCAGAATA','AGCCAGCTCT','AGCTATTCCA','AGCTCCTCAG','AGGAGGCATA','AGGCGTCTGT',\
'AGTAACTCAC','AGTAAGCGTT','AGTCTGTACG','AGTGCAATGT','ATAAGGTGCA','ATACACGACA','ATAGGCCATT','ATATCCGCAT','ATCCAATACG','ATCCGCTGTG','ATCGCGATTA',\
'ATCGGTAGGC','ATGACTCAGT','ATGCACCGGA','AGGTATCCTC','AGGTCACCAA','AGTCCACGTA','AGTCTCGGCA','ATAACGCCTC','ATAAGAGGTC','ATACCTCCGG','ATAGCAGTGC',\
'ATCAGCACTT','ATCAGCGAGG','ATCCGTCCAT','ATCGACGGCT','ATCTAAGGAG','ATGACGGTAA','ATGCGGACTG','ATGCTTCCTA','ATGGACCAAC','ATGGTCTTAG','ATTATCGGAC',\
'ATTCGGAACA','CAAGATGAGG','CAAGCCAACG','CACGAGTCTG','CACGCTCCAA','CAGTGCTCTT','CAGTTAAGCA','CATGTACGCC','CATTACACTG','CCAAGGAGTT','CCAATTGTTC',\
'CCATAACTTG','CCATACTGAC','ATGGTGAGCG','ATGTGGAAGC','CAACAATCCA','CAAGAAGCAT','CAAGTGGATC','CACAGTTCAT','CACTGAGCAC','CAGATCAATG','CATAGCTATC',\
'CATCACCACC','CATTCGACGA','CCAACTATGG','CCACAAGTGC','CCAGCTTAGT','CCATAGATCA','CCATGTGCTT','CCATTCAGCG','CCGAACAAGC','CCGAATAGTG','CCGACTTCTC',\
'CCGCGTTATG','CCGCTAGCTT','CCGGTCTCTA','CCGTACGATG','CCTAGTTGAG','CCTATTCTGT','CCTGATGCCA','CCTGCAATAC','CGAGGAACAA','CGATAACCGC','CGCCAGTGTT',\
'CGCCTTGTAC','CCGAACCTAA','CCGAAGACCT','CCGATCCACT','CCGATGATAC','CCGGAGTATC','CCGGCCAATT','CCGTCAGAAC','CCTAGACACG','CCTCAACCGA','CCTCCATAAG',\
'CCTTGTATTC','CGAGATCTCT','CGATCCTGTG','CGCCAACCAT','CGCGGATTCA','CGCTTAAGGC','CGCTTACTAA','CGCTTCTTGG','CGGAGATTGG','CGGAGCTCAA','CGGCAACTTA',\
'CGGCTCATCA','CGTAACGGAT','CGTAAGATTC','CGTCCTAGGA','CGTCGGCAAT','CTAACTTCAG','CTAATAGCGT','CTATGAACGG','CTCAAGGACC','CTCGCAACGT','CTCGTGCCTA',\
'CGGAAGCTGT','CGGAATACAC','CGGATCGGTA','CGGATTCTAG','CGGTCGTATT','CGGTGACATC','CGTACTGTAA','CGTAGAAGAC','CGTGAGTTAT','CGTGTCAAGC','CTACACCAGG',\
'CTAGCACAAT','CTCACCTGTC','CTCCTATTGT','CTGGATTGAC','CTGTAGTCAG','CTGTCGCTTC','CTGTCTGTGT','CTTCATATCG','CTTGCTGACG','GAAGGATTAG','GAATCGAGCC',\
'GACCATCTAA','GACGACCACA','GAGACATCTT','GAGCGAGTCA','GATAGACTGT','GATAGAGGCG','GATCTCATTC','GATCTGGTCG','GATGTGACAG','GATTAAGTCC','CTGTGCAACA',\
'CTTATGTTGC','CTTGGATCTT','GAAGAGTTCT','GAATCTTCTC','GAATTACGGC','GAGAACGAAG','GAGACAAGGC','GAGTAGACCA','GATACGCTTA','GATAGGTCAA','GATATCAGGA',\
'GATGAGTGAC','GATGGATACA','GATTGCACGC','GCAAGCGAAT','GCAATGTAAG','GCACACTATA','GCACTTAATC','GCAGGAGATG','GCATCCGATC','GCCAAGTACA','GCCATATCGA',\
'GCCGTCAATA','GCTATTATCC','GCTCAGTAAT','GGACGATGCT','GGCATCGTGA','GGCGCTATAA','GGCGTTAAGT','GGTAATGTGT','GGTGGTTGGA','GCACTCGGAA','GCACTGCGTT',\
'GCAGTACTGG','GCATATGAGT','GCCACGATTC','GCCATAGGTT','GCCTGGACAT','GCGTAATTAC','GCTGCTTATA','GGAATAAGCA','GGCATTATTG','GGCCGAGATT','GGCTATTGAT',\
'GGCTGCTACT','GGTGTTCACC','GGTTAGATCT','GGTTATGGCG','GGTTCACTGG','GTAACCTTGG','GTAAGAACCT','GTATTGTGGA','GTCCGCATCA','GTCGGTGACA','GTCTCGAGTG',\
'GTGACTATAC','GTGGTTAATG','GTTCATTGCC','GTTCCGGTGA','GTTGATCCGC','GTTGTATGCT','TAAGGTACGG','TACGGACATA','GGTTGTGCAA','GTAACCAGTA','GTAAGGCTCC',\
'GTAATCCACG','GTCCTTCGGT','GTCGCTCTCT','GTCTCTTAAG','GTCTTCCGAG','GTGTGCCTGT','GTGTGTGTCC','GTTCGTCGAA','GTTGAATTGG','TAACCGTAGC','TAACGTCGAT',\
'TACTACCGCC','TACTGTCAAG','TAGCGAACGC','TAGCGCCAAC','TAGTAGTCTC','TAGTCCGCTG','TATCGTTACG','TCAAGTGCAG','TCACGCCACT','TCACGTTGGC','TCCACGGTCA',\
'TCCACTCGCT','TCCTAAGAGA','TCCTCTAGTA','TCGCACTTGA','TCGCCTACTG','TCTACATCCG','TCTCCACATT','TAGGACGCCT','TAGGTTGCAA','TAGTGGAACT','TATCATGCAG',\
'TCACAGATAC','TCACCGCCTA','TCATTGTCCA','TCCACACTAG','TCCGACTAAC','TCCGTTATCT','TCGAAGCATT','TCGAGAGAGC','TCGCGTAGCA','TCGGCGTTAA','TCTCTCCTAT',\
'TCTTGCTCGG','TGAACTAACC','TGAAGAAGGT','TGAGCGTTCC','TGAGTACGTA','TGGAATGGAG','TGTCATTCGC','TGTGCTTCAG','TGTTCAGGAT','TTACACACGT','TTACTGTGAC',\
'TTATGCCGCG','TTCACGGAAG','TTCGAGTGAT','TTCTGTACCT','TTGGTAACAG','TTGGTCAGTA','TGAAGATCCA','TGACCTGAGA','TGCGCTCATT','TGCGTGCTCA','TGTGACGTGC',\
'TGTGCACTAA','TGTTGTGACT','TTAACGCTGA','TTATAGGAGG','TTATCGCGTT','TTCAGGAGTA','TTCCATCGAG','TTGGCAATTC','TTGGCTCCAC','TTGTCGGCCA','TTGTGTTCGA']

pos_to_gene=get_gene_coordinates(geneinfofilename,dirhead,samfilename)
get_umis_to_gene_seq(samfilename,spikeinfilename,readfilename,dirhead,pos_to_gene,barcodes)
quantify_genes(dirhead,samfilename,out_basename)
