# Pipeline for running PLAMB 
Pipeline for running Plamb: https://github.com/RasmussenLab/vamb/tree/vamb_n2v_asy


## Quick Start
```
# Create environment and install dependencies 
conda create -n ptracker_pipeline -c conda-forge -c bioconda snakemake-minimal pandas     
conda activate ptracker_pipeline
pip install rich-click

# clone the repository
git clone https://github.com/Las02/ptracker_workflow -b try_cli

# Run the application to set up everything
./ptracker_workflow/cli.py --setup_env
```
 To run the entire pipeline including assembly pass in a whitespace seperated file containing the reads:
```
./ptracker_workflow/cli.py --reads <read_file> 
```
This file could look like:
``` 
sample                        read1                          read2
im_the_sample1_identifier     im/a/path/to/sample_1/read1    im/a/path/to/sample_1/read2
im_the_sample2_identifier     im/a/path/to/sample_2/read1    im/a/path/to/sample_2/read2
```
To dry run the pipeline before pass in the --dryrun flag


To run the pipeline from allready assembled reads pass in a whitespace seperated file containing the reads and additionally
3 files which Spades produces: 
| Description                         | File Name from Spades                               |
|:------------------------------------|:----------------------------------------|
| The assembled contigs               | `contigs.fasta`                         |
| The simplified assembly graphs      | `assembly_graph_after_simplification.gfa` |
| A metadata file                     | `contigs.paths`                         |

This file could look like:
``` 
sample                        read1                          read2                         assembly_graph                                           contig                                      contig_paths
im_the_sample1_identifier     im/a/path/to/sample_1/read1    im/a/path/to/sample_1/read2   sample1/sample1/assembly_graph_after_simplification.gfa  sample1/contigs.fasta sample1/contigs.paths sample1/contigs.paths
im_the_sample2_identifier     im/a/path/to/sample_2/read1    im/a/path/to/sample_2/read2   sample2/assembly_graph_after_simplification.gfa          sample2/contigs.fasta sample2/contigs.paths sample1/contigs.paths
```




## Advanced


The pipeline can be configurated in: ``` config/config.yaml ```
Here the resources for each rule can be configurated as follows
```
mpSpades:
  walltime: "15-00:00:00"
  threads: 60
  mem_gb: 950
```
if no resourcess are configurated for a rule the defaults will be used which are also defined in: ``` config/config.yaml ```

The input files for the pipeline can be configurated in ``` config/accesions.txt ``` 
As an example this could look like:
```
SAMPLE ID READ1 READ2
Airways 4 reads/errorfree/Airways/reads/4/fw.fq.gz reads/errorfree/Airways/reads/4/rv.fq.gz
Airways 5 reads/errorfree/Airways/reads/5/fw.fq.gz reads/errorfree/Airways/reads/5/rv.fq.gz
```

with an installation of snakemake run the following to dry-run the pipeline
```
	snakemake -np --snakefile snakefile.smk
```
and running the pipeline with 4 threads
```
	snakemake -p -c4 --snakefile snakefile.smk --use-conda
```

```
## Important Files
- snakefile.smk: The snakemake pipeline
- utils.py: utils used by the pipeline
- config: directory with the configuration files
  - accesions.txt: Sample information
  - config.yaml: configuration for the pipeline eg. resourcess
- envs: directory with the conda environment descriptions

## Misc files
Makefile - various small scripts for running the pipeline
clustersubmit.sh - script for submitting the snakefile to SLURM
parse_snakemake_output.py - small script for viewing snakefile logs
