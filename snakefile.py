import pandas as pd
import collections
import os
from pathlib import Path

## Paths
# Loading the correct configfile
THIS_FILE_DIR = config.get("dir_of_current_file")
THIS_FILE_DIR = Path("") if THIS_FILE_DIR is None else Path(THIS_FILE_DIR)
configfile: THIS_FILE_DIR / "config/config.yaml"

# Output directory defined by user
output_directory = config.get("output_directory")
# Set as empty path if not defined meaning will not have effect
OUTDIR = Path("") if output_directory is None else Path(output_directory)

# Define default threads/walltime/mem_gb
default_walltime = config.get("default_walltime")
default_threads = config.get("default_threads")
default_mem_gb = config.get("default_mem_gb")

# Functions to get the config-defined threads/walltime/mem_gb for a rule and if not defined the default
threads_fn = lambda rulename: config.get(rulename, {"threads": default_threads}).get(
    "threads", default_threads
)
walltime_fn = lambda rulename: config.get(rulename, {"walltime": default_walltime}).get(
    "walltime", default_walltime
)
mem_gb_fn = lambda rulename: config.get(rulename, {"mem_gb": default_mem_gb}).get(
    "mem_gb", default_mem_gb
)

# is GPU used ? #
CUDA = config.get("cuda", False)

contig = ""
bamfiles = ""


## Read in the sample data if contig and bamfiles are defined
if config.get("contig_bamfiles") != None:
    df = pd.read_csv(config["contig_bamfiles"], sep="\s+", comment="#")
    sample_paths = collections.defaultdict(dict)
    for sample, contig, directory_of_bamfiles in zip(
        df["sample"], df.contig, df.directory_of_bamfiles
    ):
        sample = str(sample)
        sample_paths[sample]["contig"] = contig
        sample_paths[sample]["directory_of_bamfiles"] = directory_of_bamfiles

    contig = lambda wildcards: sample_paths[wildcards.sample]["contig"]
    bamfiles = lambda wildcards: sample_paths[wildcards.sample]["directory_of_bamfiles"]

## Read in the sample data if composition and rpkm are defined
if config.get("composition_and_rpkm") != None:
    df = pd.read_csv(config["composition_and_rpkm"], sep="\s+", comment="#")
    sample_paths = collections.defaultdict(dict)
    for sample, composition, rpkm in zip(df["sample"], df.composition, df.rpkm):
        sample = str(sample)
        sample_paths[sample]["composition"] = composition
        sample_paths[sample]["rpkm"] = rpkm

    composition = lambda wildcards: sample_paths[wildcards.sample]["composition"]
    rpkm = lambda wildcards: sample_paths[wildcards.sample]["rpkm"]

    print(sample_paths)

rulename = "vamb_default"
rule vamb_default:
    input:
        contig = contig,
        bamfiles = bamfiles
    output:
        composition = OUTDIR / "sample_{sample}_vamb_default_run_{run_number}_from_bam_contig/composition.npz",
        rpkm = OUTDIR / "sample_{sample}_vamb_default_run_{run_number}_from_bam_contig/abundance.npz",
        dir = OUTDIR / "sample_{sample}_vamb_default_run_{run_number}_from_bam_contig",
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb bin default --outdir {output.dir} --fasta {input.contig} \
        -p {threads} --bamfiles {input.bamfiles} -m 2000
        """

rulename = "vamb_default_rpkm_comp"
rule vamb_default_rpkm_compt:
    input:
        # TODO add propper output
        composition = composition if config.get("composition_and_rpkm") is not None else  OUTDIR / "sample_{sample}_vamb_default_run_{run_number}_from_bam_contig/composition.npz",
        rpkm = rpkm if config.get("composition_and_rpkm") is not None else OUTDIR / "sample_{sample}_vamb_default_run_{run_number}_from_bam_contig/abundance.npz",
    output:
        dir = OUTDIR / "sample_{sample}_vamb_default_run_{run_number}_from_rpkm_comp"
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb bin default --outdir {output.dir} --composition {input.composition} \
        -p {threads} --rpkm {input.rpkm} -m 2000
        """
