# Pipeline for running PLAMB 
Pipeline for running Benchmarking Vamb: https://github.com/RasmussenLab/vamb


## Quick Start
```
# Create environment and install dependencies 
conda create -n vamb_benchmarker -c conda-forge -c bioconda snakemake-minimal pandas mamba pyyaml julia
conda activate vamb_benchmarker
pip install rich-click

# clone the repository
git clone https://github.com/Las02/ptracker_workflow -b Benchmark_vamb_cli
```


## Running on cluster
You can extend the arguments passed to snakemake by the '--snakemake_arguments' flag
This can then be used to have snakemake submit jobs to a cluster.
On SLURM this could look like

```
./cli.py <arguments> --snakemake_arguments \
    '--jobs 16 --max-jobs-per-second 5 --max-status-checks-per-second 5 --latency-wait 60 \
    --cluster "sbatch  --output={rule}.%j.o --error={rule}.%j.e \
    --time={resources.walltime} --job-name {rule}  --cpus-per-task {threads} --mem {resources.mem_gb}G "'
```
<!-- # TODO test above -->

## Setting resources
The resources are set in 'config/config.yaml'
If the tool is not submitting jobs to a cluster, the number of threads will be used to calculate how many rules can be run on the same time. If a rules defined threads is large than the number of threads defined in the --threads command line argument the threads used in the rule will be scaled down.  
A resource for a rule can be set as:
```
vamb_default:
  walltime: "05-00:00:00"
  threads: 16
  mem_gb: 245
```

If no resources is set for a rule the tool will default to the default resources set in the script:
```
default_walltime: "48:00:00"
default_threads: 8
default_mem_gb: 50
```











```
From Below needs to be updated to reflect benchmarking tool
----


 To run the entire pipeline including assembly pass in a whitespace separated file containing the reads:
```
./ptracker_workflow/cli.py --reads <read_file> 
```
This file could look like:
<Notice the header names are required to be: read1 and read2> 

``` 
read1                          read2
im/a/path/to/sample_1/read1    im/a/path/to/sample_1/read2
im/a/path/to/sample_2/read1    im/a/path/to/sample_2/read2
```
To dry run the pipeline before pass in the --dryrun flag

To run the pipeline from allready assembled reads pass in a whitespace separated file containing the reads and the path to the spades assembly directories for each read pair.
This directory must contain the following 3 files which Spades produces: 
| Description                         | File Name from Spades                               |
|:------------------------------------|:----------------------------------------|
| The assembled contigs               | `contigs.fasta`                         |
| The simplified assembly graphs      | `assembly_graph_after_simplification.gfa` |
| A metadata file                     | `contigs.paths`                         |

This file could look like:
 <Notice the header names are required to be: read1, read2 and assembly_dir> 

``` 
read1                          read2                         assembly_dir                                           
im/a/path/to/sample_1/read1    im/a/path/to/sample_1/read2   path/sample_1/Spades_output  
im/a/path/to/sample_2/read1    im/a/path/to/sample_2/read2   path/sample_2/Spades_output          
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
