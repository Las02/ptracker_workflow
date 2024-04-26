# TODO path to files should not be thorugh symlinks -- access for other people
# TODO add genomad til mixed
# TODO megahit istedet for spades?
# TODO Downloading downloas 3 files, _1 and _2 and a second - what is it.. and should it be used (likey non-paired reads something)
configfile: "config/config.yaml"

from utils import expand_dir
import pandas as pd

# Constants
LOG_CMD = " > {log.o} 2> {log.e};"

# Read in the sample data
df = pd.read_csv("./config/accessions.txt", sep="\s+", comment="#")
sample_id = {}
for sample,id in zip(df.SAMPLE, df.ID):
    if sample not in sample_id:
        sample_id[sample] = [id]
    else:
        sample_id[sample].append(id)

# print( expand_dir("data/sample_{key}/mapped/{value}.bam.sort", sample_id))

#rulename = "download"
#rule download:
#    output:
#        "data/sample_{key}/fastq/{id}_1.fastq", # Quick fix for now.. improve it later
#        "data/sample_{key}/fastq/{id}_2.fastq",
#    params:
#        id_download = "data/sample_{key}/fastq",
#    group: "spades"
#    benchmark: config["benchmark"]+rulename
#    log: e =  config["log.e"]+rulename, o =  config["log.o"]+rulename,
#    shell:
#        "/home/people/lasdan/ptracker/sratoolkit.3.0.10-ubuntu64/bin/prefetch {wildcards.id} " 
#        +LOG_CMD+ 
#        "/home/people/lasdan/ptracker/sratoolkit.3.0.10-ubuntu64/bin/fastq-dump {wildcards.id} -O {params.id_download} --split-3 " 
#        +LOG_CMD+
#        "rm -rf {wildcards.id}" # Remove the pre-fetched information after collecting the fastq files


##  START PAU SETUP
def get_config(name, default, regex):
    #res = config.get(name, default).strip()
    CONFIGFILE = "PauPipeline/config_Gastrointestinal_with_renaming_geNomad.json" # TODO delete and add info to the other configfile
    res = CONFIGFILE
    m = re.match(regex, res)
    if m is None:
        raise ValueError(
            f'Config option \'{name}\' is \'{res}\', but must conform to regex \'{regex}\'')
    return res


# set configurations
## Contig parameters
CONTIGS_FILE=config["contigs_filtered_file"] #get_config('contigs_filtered_file','', r'.*')
ABUNDANCE_FILE=config["abundance_file"] #get_config('abundance_file','', r'.*')
CONTIGNAMES_FILE = config["contignames_file"] #get_config('contignames_file', '', r'.*') # file containing the sorted contignames
CONTIGS = config["contigs"] #get_config('contigs', 'contigs.txt', r'.*') # each line is a contigs path from a given sample
MIN_CONTIG_LEN = int(config["min_contig_len"]) #get_config('min_contig_len', '2000', r'[1-9]\d*$'))
#MIN_IDENTITY = float(get_config('min_identity', '0.95', r'.*'))
#SAMPLE_DATA 

## Assembly graph parameters
ASSEMBLY_GRAPHS_DIR=get_config('assembly_graph_dir','', r'.*')

## N2V parameters
N2V_NZconfig = "weight" # config["n2v_nz"] #get_config('n2v_nz','weight', r'.*') # TODO fix in a different way.
N2V_EDconfig = config["n2v_ed"] #get_config('n2v_ed','128', r'.*')
N2V_WLconfig = config["n2v_wl"] #get_config('n2v_wl','10', r'.*')
N2V_NWconfig = 50 #config["n2v_nw"] #get_config('n2v_nw','50', r'.*')
N2V_WSconfig = config["n2v_ws"] #get_config('n2v_ws','10', r'.*')
N2V_Pconfig = config["n2v_p"] #get_config('n2v_p','0.1', r'.*')
N2V_Qconfig = config["n2v_q"] #get_config('n2v_q','2.0', r'.*')

NEIGHS_R='0.05'
## Binning parameters
PLAMB_MEM = config["plamb_mem"] #get_config('plamb_mem', '20gb', r'[1-9]\d*GB$')
PLAMB_PPN = config["plamb_ppn"] #get_config('plamb_ppn', '10', r'[1-9]\d*(:gpus=[1-9]\d*)?$')
PLAMB_PARAMS = config["plamb_params"] #get_config('plamb_params',' -o C --minfasta 200000  ', r'.*')
PLAMB_PRELOAD = config["plamb_preload"] #get_config('plamb_preload', '', r'.*')

RENAMING_FILE = config["renaming_file"] #get_config('renaming_file', '', r'.*')
OUTDIR= "outdir_plamb" #config["outdir"] #get_config('outdir', 'outdir_plamb', r'.*') # TODO fix

try:
    os.makedirs(os.path.join(OUTDIR,'log'), exist_ok=True)
except FileExistsError:
    pass
# END PAU SET UP


rule all:
    input:
        expand(os.path.join(OUTDIR, "{key}", 'log/rename_clusters_and_hoods.finished'), key=sample_id.keys()),
        #expand_dir("data/sample_{key}/mapped/{value}.bam.sort", sample_id),
        #expand("data/sample_{key}/genomad/contigs.flt_aggregated_classification", key=sample_id.keys()),
        # expand("data/sample_{key}/mapped/{value}.sort.bam", key=sample_id.keys())

rulename = "spades"
rule spades:
    input:
        #fw = "data/sample_{key}/fastq/{id}_1.fastq",    |
        #rv = "data/sample_{key}/fastq/{id}_2.fastq",    | -- For when rule download is uncommented
        fw = "data/reads/{id}_1.fastq", # Quick fix for now.. improve it later .. actually not worth it.. i guess
        rv = "data/reads/{id}_2.fastq",
    output:
        outdir = directory("data/sample_{key}/spades_{id}"),
        outfile = "data/sample_{key}/spades_{id}/contigs.fasta",
        graph = "data/sample_{key}/spades_{id}/assembly_graph_after_simplification.gfa", # The graph Changed
        graphinfo  = "data/sample_{key}/spades_{id}/contigs.paths", # The graph Changed
    group: "spades"
    threads: config["spades"]["threads"]
    resources: walltime = config["spades"]["walltime"], mem_gb = config["spades"]["mem_gb"]
    benchmark: config["benchmark"]+rulename
    log: e =  config["log.e"]+rulename, o =  config["log.o"]+rulename,
    shell:
        #"rm -rf {output.outdir};"
        "bin/SPAdes-3.15.4-Linux/bin/metaplasmidspades.py "
        "-o {output.outdir} -1 {input.fw} -2 {input.rv} " 
        "-t {threads} " # No reason to set mem, as spades just quits if it uses above the threshold
        +LOG_CMD

rulename="cat_contigs"
rule cat_contigs:
    input:
        expand_dir("data/sample_{key}/spades_{value}/contigs.fasta", sample_id)
    output:
        "data/sample_{key}/contigs.flt.fna.gz"
    #conda: 
    #    "vambworks"
    group: "spades"
    benchmark: config["benchmark.key"]+rulename
    log: e =  config["log.e.key"]+rulename, o =  config["log.o.key"]+rulename,
    shell: 
        "python bin/vamb/src/concatenate.py {output} {input} -m 2000" 
        +LOG_CMD

# Index resulting contig-file with minimap2
rulename="index"
rule index:
    input:
        contigs = "data/sample_{key}/contigs.flt.fna.gz"
    output:
        mmi = "data/sample_{key}/contigs.flt.mmi"
    group: "spades"
    #envmodules:
    #    'tools',
    #    'minimap2/2.6'
    benchmark: config["benchmark.key"]+rulename
    log: e =  config["log.e.key"]+rulename, o =  config["log.o.key"]+rulename,
    shell:
        "minimap2 -d {output} {input} "
        +LOG_CMD


# This rule creates a SAM header from a FASTA file.
# We need it because minimap2 for truly unknowable reasons will write
# SAM headers INTERSPERSED in the output SAM file, making it unparseable.
# To work around this mind-boggling bug, we remove all header lines from
# minimap2's SAM output by grepping, then re-add the header created in this
# rule.
rulename="dict"
rule dict:
    input:
        contigs = "data/sample_{key}/contigs.flt.fna.gz",
    output:
        "data/sample_{key}/contigs.flt.dict"
    group: "spades"
    #envmodules:
    #    'tools',
    #    'samtools/1.17',
    benchmark: config["benchmark.key"]+rulename
    # log: e =  config["log.e.key"]+rulename, o =  config["log.o.key"]+rulename,
    shell:
        "samtools dict {input.contigs} | cut -f1-3 > {output}"

# Generate bam files 
LONG_READS = False
rulename="minimap"
rule minimap:
    input:
        #fw = "data/sample_{key}/fastq/{id}_1.fastq", |
        #rv = "data/sample_{key}/fastq/{id}_2.fastq", | - For when downloading fastq files
        fw = "data/reads/{id}_1.fastq", # Quick fix for now.. improve it later .. actually not worth it.. i guess
        rv = "data/reads/{id}_2.fastq",

        mmi ="data/sample_{key}/contigs.flt.mmi",
        dict = "data/sample_{key}/contigs.flt.dict"
    output:
        bam = temp("data/sample_{key}/mapped/{id}.bam")
    group: "minimap"
    params:
        long_or_short_read = 'map-pb -L' if LONG_READS else 'sr',
    #envmodules:
    #    'tools',
    #    'samtools/1.17',
    #    'minimap2/2.6'
    threads: config["minimap"]["threads"]
    resources: walltime = config["minimap"]["walltime"], mem_gb = config["minimap"]["mem_gb"]
    benchmark: config["benchmark"]+rulename
    # log: e =  config["log.e"]+rulename, o =  config["log.o"]+rulename,
    shell:
        # See comment over rule "dict" to understand what happens here
        "minimap2 -ax {params.long_or_short_read} {input.mmi} {input.fw} {input.rv} "
        " | grep -v '^@'"
        " | cat {input.dict} - "
        " | samtools view -F 3584 -b - " # supplementary, duplicate read, fail QC check
        " > {output.bam}"

 # Sort bam files
rulename="sort"
rule sort:
    input:
        "data/sample_{key}/mapped/{id}.bam",
    output:
        "data/sample_{key}/mapped/{id}.bam.sort",
    group: "minimap"
    #envmodules:
    #    'tools',
    #    'samtools/1.17',
    benchmark: config["benchmark"]+rulename
    # log: e =  config["log.e"]+rulename, o =  config["log.o"]+rulename,
    shell:
        "samtools sort {input} -o {output} "

rulename="genomad"
rule genomad:
    input: 
        fasta = "data/sample_{key}/contigs.flt.fna.gz", 
    output:
        direc = "data/sample_{key}/genomad",
        file = "data/sample_{key}/genomad/contigs.flt_aggregated_classification",
    params:
        db = "genomad_db", 
    threads: config["genomad"]["threads"]
    resources: walltime = config["genomad"]["walltime"], mem_gb = config["genomad"]["mem_gb"]
    #conda:
    #    "genomad"
    benchmark: config["benchmark.key"]+rulename
    log: e =  config["log.e.key"]+rulename, o =  config["log.o.key"]+rulename,
    shell:
        "genomad end-to-end {input.fasta} {output.direc} {params.db} "
        "-t {threads}"
        + LOG_CMD






## Pau Pipeline start



import re
import os
import sys
import numpy as np
SNAKEDIR = os.path.dirname(workflow.snakefile) # TODO should be bin
sys.path.append(os.path.join(SNAKEDIR, 'bin'))


## This snakemake workflow executes the second part of the  p-tracker pipeline.
# Inputs:
# - Contig fasta file with all contigs from all samples
# - Assembly graphs in GFA format
# - geNomad contig scores
# Outputs (final):
# - Plasmid bins
# - Organism bins
# - Virus bins

## The pipeline is composed of the following steps:
# 1. Align contigs all against all 
# 2. Generate per sample assembly graphs from gfa assembly graphs
# 3. Run n2v on the per sample assembly graphs 
# 4. Extract hoods from assembly graphs n2v embeddings per sample 
# 5. Connect hoods with alignment graphs
# 6. Run vamb to merge the hoods
# 7. Classify bins/clusters into plasmid/organism/virus bins/clusters

# Despite the steps are numerated, some of the order might change 




# parse if GPUs is needed #
plamb_threads, sep, plamb_gpus = PLAMB_PPN.partition(':gpus=')
PLAMB_PPN = plamb_threads
CUDA = len(plamb_gpus) > 0

## read in sample information ##
SAMPLES=get_config('samples',"",r'.*')

# target rule
#rule all:
#    input:
        #os.path.join(OUTDIR,'log/run_vamb_asymmetric.finished')
#        os.path.join(OUTDIR,'log/rename_clusters_and_hoods.finished')
        #os.path.join(OUTDIR,'log','classify_bins_with_geNomad.finished')

#gunzip -c {input} |blastn -query - -db {output[0]} -out {output[1]} -outfmt 6 -perc_identity 95 -num_threads {threads} -max_hsps 1000000
# 1. Align contigs all against all 
rule align_contigs:
    input:
        "data/sample_{key}/contigs.flt.fna.gz",
        #CONTIGS_FILE # Just a contig file
    output:
        os.path.join(OUTDIR,"{key}",'tmp','blastn','blastn_all_against_all.txt'),
        os.path.join(OUTDIR,"{key}",'log/blastn/align_contigs.finished')
    params:
        db_name=os.path.join(OUTDIR,'tmp','blastn','contigs.db'), # TODO should be made?
        walltime='86400',
        nodes='1',
        ppn='8'
    resources:
        mem='15GB'
    threads:
        8
    log:
        o = os.path.join(OUTDIR,"{key}",'qsub/blastn/align_contigs.o'),
        e = os.path.join(OUTDIR,"{key}",'qsub/blastn/align_contigs.e')
    conda:
        #'envs/blast.yaml'
        'vamb_n2v_master'
    shell:
        """
        module load ncbi-blast/2.15.0+
        gunzip -c {input} |makeblastdb -in - -dbtype nucl -out {params.db_name} -title contigs.db
        gunzip -c {input} |blastn -query - -db {params.db_name} -out {output[0]} -outfmt 6 -perc_identity 95 -num_threads {threads} -max_hsps 1000000
        touch {output[1]}
        """
print("SNAKEDIR", SNAKEDIR)
        
        
## 2. Generate nx graph per sample for graphs from gfa assembly graphs
# for each "sample"
rule weighted_assembly_graphs:
    input:
        graph = "data/sample_{key}/spades_{id}/assembly_graph_after_simplification.gfa", # The graph Changedhis created?
        graphinfo  = "data/sample_{key}/spades_{id}/contigs.paths", # TODO The graph Changed Where is this
        #os.path.join(ASSEMBLY_GRAPHS_DIR,'{sample}','assembly_graph_after_simplification.gfa'), # The graph
        #os.path.join(ASSEMBLY_GRAPHS_DIR,'{sample}','contigs.paths'), # information from the graph
    output:
        os.path.join(OUTDIR,"{key}",'tmp','assembly_graphs','{id}.pkl'),
        os.path.join(OUTDIR,"{key}", 'log','assembly_graph_processing','weighted_assembly_graphs_{id}.finished')
    params:
        path = os.path.join(SNAKEDIR, 'bin', 'process_gfa.py'),
        walltime='86400',
        nodes='1',
        ppn='4'
    resources:
        mem = '4GB'
    threads:
        4
    log:
        o=os.path.join(OUTDIR,"{key}",'qsub','assembly_graph_processing','weighted_assembly_graphs_{id}.out'),
        e=os.path.join(OUTDIR,"{key}",'qsub','assembly_graph_processing','weighted_assembly_graphs_{id}.err'),
    conda:
        'vamb_n2v_master'
        #'envs/vamb.yaml'
    shell:
        """
        python {params.path} --gfa {input[0]} --paths {input[1]} -s {wildcards.sample} -m {MIN_CONTIG_LEN}  --out {output[0]}
        touch {output[1]}
        """

# ## TODO  >> should have key/sample name with itself
def weighted_assembly_graphs_all_samples_f(wildcards):
    samples = [sample for sample in SAMPLES.split()]
    weighted_assembly_graphs_all_samples_paths=expand(
        os.path.join(OUTDIR,'tmp','assembly_graphs','{sample}.pkl'),
        sample=samples)
    return weighted_assembly_graphs_all_samples_paths

a = expand_dir(os.path.join(OUTDIR,"{key}",'tmp','assembly_graphs','{value}.pkl'), sample_id), # TODO might be funky 
print(a)
# Why does this exist?
rule weighted_assembly_graphs_all_samples:
    input:
        #weighted_assembly_graphs_all_samples_f
        expand_dir(os.path.join(OUTDIR,"{key}",'tmp','assembly_graphs','{value}.pkl'), sample_id), # TODO value because method changes key:value pair
    output:
        os.path.join(OUTDIR,"{key}",'log','assembly_graph_processing','weighted_assembly_graphs_all_samples.finished')
    params:
        walltime='86400',
        nodes='1',
        ppn='1'
    resources:
        mem = '1GB'
    threads:
        1
    log:
        o=os.path.join(OUTDIR,"{key}",'qsub','assembly_graph_processing','weighted_assembly_graphs_all_samples.out'),
        e=os.path.join(OUTDIR,"{key}",'qsub','assembly_graph_processing','weighted_assembly_graphs_all_samples.err')
    conda:
        'vamb_n2v_master'
        #'envs/vamb.yaml'
    shell:
        """
        touch {output}
        """
# ## TODO END



## 3. Genereate nx graph from the alignment graph
rule weighted_alignment_graph:
    input:
        os.path.join(OUTDIR,"{key}",'tmp','blastn','blastn_all_against_all.txt'),
        os.path.join(OUTDIR,"{key}",'log/blastn/align_contigs.finished')
    output:
        os.path.join(OUTDIR,"{key}",'tmp','alignment_graph','alignment_graph.pkl'),
        os.path.join(OUTDIR,"{key}",'log','alignment_graph_processing','weighted_alignment_graph.finished')
    params:
        path = os.path.join(SNAKEDIR, 'bin', 'process_blastout.py'),
        walltime='86400',
        nodes='1',
        ppn='4'
    resources:
        mem = '4GB'
    threads:
        4
    log:
        o=os.path.join(OUTDIR,"{key}",'qsub','alignment_graph_processing','weighted_alignment_graph.out'),
        e=os.path.join(OUTDIR,"{key}",'qsub','alignment_graph_processing','weighted_alignment_graph.err'),
    conda:
        'vamb_n2v_master'
        #'envs/vamb.yaml'
    shell:
        """
        python {params.path} --blastout {input[0]} --out {output[0]}
        touch {output[1]}
        """


## 4. Merge assembly graphs an alignment graph into a unified graph
rule create_assembly_alignment_graph:
    input:
        alignment_graph_file = os.path.join(OUTDIR,"{key}",'tmp','alignment_graph','alignment_graph.pkl'),
        assembly_graph_files = expand_dir(os.path.join(OUTDIR,"{key}",'tmp','assembly_graphs','{value}.pkl'), sample_id), # TODO might be funky 
        weighted_alignment_graph_finished_log = os.path.join(OUTDIR,"{key}",'log','alignment_graph_processing','weighted_alignment_graph.finished'),
        weighted_assembly_graphs_all_samples_finished_log = os.path.join(OUTDIR,"{key}", 'log','assembly_graph_processing','weighted_assembly_graphs_all_samples.finished')
        #assembly_graph_files =expand(os.path.join(OUTDIR,'tmp','assembly_graphs','{sample}.pkl'),sample=[sample for sample in SAMPLES.split()]),
    output:
        os.path.join(OUTDIR,"{key}",'tmp','assembly_alignment_graph.pkl'),
        os.path.join(OUTDIR,"{key}", 'log','create_assembly_alignment_graph.finished')
    params:
        path = os.path.join(SNAKEDIR, 'src', 'merge_assembly_alignment_graphs.py'),
        walltime='86400',
        nodes='1',
        ppn='4'
    resources:
        mem = '4GB'
    threads:
        4
    log:
        o=os.path.join(OUTDIR,"{key}",'qsub','create_assembly_alignment_graph.out'),
        e=os.path.join(OUTDIR,"{key}", 'qsub','create_assembly_alignment_graph.err')
    conda:
        'vamb_n2v_master'
        #'envs/vamb.yaml'
    shell:
        """
        python {params.path} --graph_alignment {input.alignment_graph_file}  --graphs_assembly {input.assembly_graph_files} --out {output[0]} 
        touch {output[1]}
        """
        



## 3. Run n2v on the per sample assembly graphs
rule n2v_assembly_alignment_graph:
    input:
        os.path.join(OUTDIR,"{key}",'tmp','assembly_alignment_graph.pkl'),
        os.path.join(OUTDIR,"{key}",'log','create_assembly_alignment_graph.finished')
    output:
        directory(os.path.join(OUTDIR,"{key}",'tmp','n2v','assembly_alignment_graph_embeddings')),
        os.path.join(OUTDIR,"{key}",'tmp','n2v','assembly_alignment_graph_embeddings','embeddings.npz'),
        os.path.join(OUTDIR,"{key}",'tmp','n2v','assembly_alignment_graph_embeddings','contigs_embedded.txt'),
        os.path.join(OUTDIR,"{key}",'log','n2v','n2v_assembly_alignment_graph.finished')
    params:
        path = os.path.join(SNAKEDIR, 'src', 'fastnode2vec_args.py'),
        walltime='86400',
        nodes='1',
        ppn='8'
    resources:
        mem = '20GB'
    threads:
        8
    log:
        o=os.path.join(OUTDIR,"{key}",'qsub','n2v','n2v_assembly_alignment_graph.out'),
        e=os.path.join(OUTDIR,"{key}",'qsub','n2v','n2v_assembly_alignment_graph.err')
    conda:
        'vamb_n2v_master'
        #'envs/vamb.yaml'
    shell:
        """
        python {params.path} -G {input[0]} --ed {N2V_ED} --nw {N2V_NW} --ws {N2V_WS} --wl {N2V_WL}\
         -p {N2V_P} -q {N2V_Q} --outdirembs {output[0]} --normE {N2V_NZ} --contignames {CONTIGNAMES_FILE}
        touch {output[3]}
        """



## 4. Extract hoods from assembly graphs n2v embeddings per sample 
rule extract_neighs_from_n2v_embeddings:
    input:
        os.path.join(OUTDIR,"{key}",'tmp','n2v','assembly_alignment_graph_embeddings','embeddings.npz'),
        os.path.join(OUTDIR,"{key}",'tmp','n2v','assembly_alignment_graph_embeddings','contigs_embedded.txt'),
        os.path.join(OUTDIR,"{key}",'log','n2v','n2v_assembly_alignment_graph.finished'),
        os.path.join(OUTDIR,"{key}",'tmp','assembly_alignment_graph.pkl')

    output:
        directory(os.path.join(OUTDIR,"{key}",'tmp','neighs')),
        os.path.join(OUTDIR,"{key}",'tmp','neighs','neighs_object_r_%s.npz'%NEIGHS_R),
        os.path.join(OUTDIR,"{key}",'log','neighs','extract_neighs_from_n2v_embeddings.finished')
    params:
        path = os.path.join(SNAKEDIR, 'src', 'embeddings_to_neighs.py'),
        walltime='86400',
        nodes='1',
        ppn='8'
    resources:
        mem = '50GB'
    threads:
        8
    log:
        o=os.path.join(OUTDIR,"{key}",'qsub','neighs','extract_neighs_from_n2v_embeddings.out'),
        e=os.path.join(OUTDIR,"{key}",'qsub','neighs','extract_neighs_from_n2v_embeddings.err')
    conda:
        'vamb_n2v_master'
    shell:
        """
        python {params.path} --embs {input[0]} --contigs_embs {input[1]}\
         --contignames {CONTIGNAMES_FILE} -g {input[3]} -r {NEIGHS_R} --neighs_outdir {output[0]}
        touch {output[2]}
        """

## 5. Run vamb to merge the hoods
rule run_vamb_asymmetric:
    input:
        os.path.join(OUTDIR,"{key}",'log','neighs','extract_neighs_from_n2v_embeddings.finished'),
        #CONTIGS_FILE,
        "data/sample_{key}/contigs.flt.fna.gz",
        ABUNDANCE_FILE,
        os.path.join(OUTDIR,"{key}",'tmp','neighs','neighs_object_r_%s.npz'%NEIGHS_R)#,
        #os.path.join(OUTDIR,'tmp','neighs','neighs_mask_r_%s.npz'%NEIGHS_R)

    output:
        #directory(os.path.join(OUTDIR,'vamb_asymmetric')),
        #os.path.join(OUTDIR,'vamb_asymmetric','vae_clusters_within_radius_complete_unsplit.tsv'),
        #os.path.join(OUTDIR,'vamb_asymmetric','vae_clusters_unsplit.tsv'),
        os.path.join(OUTDIR,"{key}",'log/run_vamb_asymmetric.finished')
    params:
        walltime='86400',
        nodes='1',
        ppn=PLAMB_PPN,
        cuda='--cuda' if CUDA else ''
    resources:
        mem=PLAMB_MEM
    threads:
        int(plamb_threads)
    conda:
        'vamb_n2v_master' 
    log:
        o=os.path.join(OUTDIR,"{key}",'qsub','run_vamb_asymmetric.out'),
        e=os.path.join(OUTDIR,"{key}",'qsub','run_vamb_asymmetric.err')
    shell:
        """
        module unload gcc/13.2.0
        module unload gcc/12.2.0
        module load gcc/13.2.0
        {PLAMB_PRELOAD}
        vamb bin vae_asy --outdir {OUTDIR}/vamb_asymmetric --fasta {input[1]} -p {threads} --rpkm {input[2]}\
        --seed 1 --neighs {input[3]}  -m {MIN_CONTIG_LEN} {PLAMB_PARAMS}\
         {params.cuda}  
        touch {output}
        """


rule run_geNomad:
    input:
        #CONTIGS_FILE
        "data/sample_{key}/contigs.flt.fna.gz",
    output:
        directory(os.path.join(OUTDIR,"{key}",'tmp','geNomad')),
        os.path.join(OUTDIR,"{key}",'log/run_geNomad.finished'),
        os.path.join(OUTDIR,"{key}",'tmp','geNomad','contigs.flt_aggregated_classification','contigs.flt_aggregated_classification.tsv')
    params:
        db_geNomad="/home/projects/ku_00197/data/ptracker/dbs/genomad_db",
        walltime='86400',
        nodes='1',
        ppn='16'
    resources:
        mem='50GB'
    threads:
        16
    log:
        o = os.path.join(OUTDIR,"{key}",'qsub/run_geNomad.o'),
        e = os.path.join(OUTDIR,"{key}",'qsub/run_geNomad.e')
    conda:
        #'envs/blast.yaml'
        'vamb_n2v_master'
    shell:
        """
        module load mmseqs2/release_15-6f452
        module load aragorn/1.2.36
        genomad end-to-end --cleanup {input} {output[0]}   {params.db_geNomad} --threads {threads}
        touch {output[1]}
        """


## 7. Classify bins/clusters into plasmid/organism/virus bins/clusters
rule classify_bins_with_geNomad:
    input:
        os.path.join(OUTDIR,"{key}",'tmp','geNomad','contigs.flt_aggregated_classification','contigs.flt_aggregated_classification.tsv'),
        os.path.join(OUTDIR,"{key}",'log/run_vamb_asymmetric.finished'),
        os.path.join(OUTDIR,"{key}",'log/run_geNomad.finished')
    output:
        os.path.join(OUTDIR,"{key}",'vamb_asymmetric','vae_clusters_within_radius_with_looners_complete_unsplit_candidate_plasmids.tsv'),
        os.path.join(OUTDIR,"{key}",'log','classify_bins_with_geNomad.finished')
    params:
        path = os.path.join(SNAKEDIR, 'bin', 'classify_bins_with_geNomad.py'),
        walltime='86400',
        nodes='1',
        ppn=1,
    resources:
        mem="1GB"
    threads:
        1
    conda:
        'vamb_n2v_master' 
    log:
        o=os.path.join(OUTDIR, "{key}", 'qsub','classify_bins_with_geNomad.out'),
        e=os.path.join(OUTDIR, "{key}", 'qsub','classify_bins_with_geNomad.err')
    shell:
        """
        python {params.path} --clusters {OUTDIR}/vamb_asymmetric/vae_clusters_within_radius_with_looners_complete_unsplit.tsv\
         --dflt_cls {OUTDIR}/vamb_asymmetric/vae_clusters_unsplit.tsv --scores {input[0]} --outp {output[0]} --lengths {OUTDIR}/vamb_asymmetric/lengths.npz --contignames {OUTDIR}/vamb_asymmetric/contignames
        touch {output[1]}
        """
    
print("SNAKEDIR2", SNAKEDIR)

rule rename_clusters_and_hoods:
    input:
        os.path.join(OUTDIR, "{key}", 'log','classify_bins_with_geNomad.finished')
    output:
        os.path.join(OUTDIR, "{key}", 'log/rename_clusters_and_hoods.finished')
    params:
        path_sample = os.path.join(SNAKEDIR, 'bin', 'replace_samples.py'),
        path_cluster = os.path.join(SNAKEDIR, 'bin', 'rename_clusters.py'),
        walltime='86400',
        nodes='1',
        ppn='1'

    resources:
        mem="1GB"
    threads:
        1
    conda:
        'vamb_n2v_master' 
    log:
        o=os.path.join(OUTDIR, "{key}", 'qsub','rename_clusters_and_hoods.out'),
        e=os.path.join(OUTDIR, "{key}", 'qsub','rename_clusters_and_hoods.err')
    shell:
        """
        python {params.path_cluster} --clusters {OUTDIR}/vamb_asymmetric/vae_clusters_within_radius_with_looners_complete_unsplit.tsv --renaming_file {RENAMING_FILE} --out {OUTDIR}/vamb_asymmetric/vae_clusters_within_radius_with_looners_complete_unsplit_renamed.tsv --header
        python {params.path_cluster} --clusters {OUTDIR}/vamb_asymmetric/vae_clusters_within_radius_with_looners_unsplit.tsv --renaming_file {RENAMING_FILE} --out {OUTDIR}/vamb_asymmetric/vae_clusters_within_radius_with_looners_unsplit_renamed.tsv --header
        python {params.path_cluster} --clusters {OUTDIR}/vamb_asymmetric/vae_clusters_unsplit.tsv --renaming_file {RENAMING_FILE} --out {OUTDIR}/vamb_asymmetric/vae_clusters_unsplit_renamed.tsv  --header 
        
        python {params.path_cluster} --clusters {OUTDIR}/vamb_asymmetric/vae_clusters_within_radius_with_looners_complete_unsplit_candidate_plasmids.tsv --renaming_file {RENAMING_FILE} --out {OUTDIR}/vamb_asymmetric/vae_clusters_within_radius_with_looners_complete_unsplit_candidate_plasmids_renamed.tsv --header
        python {params.path_cluster} --clusters {OUTDIR}/vamb_asymmetric/vae_clusters_unsplit_geNomadplasclustercontigs_extracted.tsv --renaming_file {RENAMING_FILE} --out {OUTDIR}/vamb_asymmetric/vae_clusters_unsplit_geNomadplasclustercontigs_extracted_renamed.tsv  --header 
        
        python {params.path_cluster} --clusters {OUTDIR}/tmp/neighs/hoods_clusters_r_0.05.tsv --renaming_file {RENAMING_FILE} --out {OUTDIR}/tmp/neighs/hoods_clusters_r_0.05_renamed.tsv --header
        touch {output}
        """















