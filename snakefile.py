import pandas as pd
import collections
import os
from pathlib import Path

## Setup
# Loading the correct configfile
THIS_FILE_DIR = config.get("dir_of_current_file", "")
THIS_FILE_DIR = Path(THIS_FILE_DIR)
configfile: THIS_FILE_DIR / "config/config.yaml"

# Output directory defined by user
OUTDIR = config.get("output_directory", "")
OUTDIR = Path(OUTDIR)

# Functions to get the config-defined threads/walltime/mem_gb for a rule and if not defined the default
threads_fn = lambda rulename: config.get(
    rulename, {"threads": config.get("default_threads")}
).get("threads", config.get("default_threads"))
walltime_fn = lambda rulename: config.get(
    rulename, {"walltime": config.get("default_walltime")}
).get("walltime", config.get("default_walltime"))
mem_gb_fn = lambda rulename: config.get(
    rulename, {"mem_gb": config.get("default_mem_gb")}
).get("mem_gb", config.get("default_mem_gb"))

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


include: THIS_FILE_DIR / "snakemake_modules/vamb_default.py"
include: THIS_FILE_DIR / "snakemake_modules/avamb_default.py"
