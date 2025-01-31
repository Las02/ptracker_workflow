#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

import rich_click as click
from click_file_types import WssFile
from command_line_runners import CliRunner, SnakemakeRunner
from environment import EnvironmentManager
from loguru import logger
from richclick_options import *

# Make both -h and --help available instead of just --help
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command()
@click.option(
    "-r",
    "--reads",
    help="""\bWhite space separated file containing read pairs. 
<Notice the header names are required to be: read1 and read2>
This file could look like:
```
read1                     read2
path/to/sample_1/read1    path/to/sample_1/read2
path/to/sample_2/read1    path/to/sample_2/read2
```
Passing in this file means that the pipeline will be run from the start, meaning it will also assemble the reads.

""",
    type=WssFile(
        expected_headers=["read1", "read2"],
        none_file_columns=[],
    ),
)
@click.option(
    "-a",
    "--reads_and_assembly_dir",
    help=f"""\bWhite space separated file containing read pairs and paths to Spades output assembly directories.
<Notice the header names are required to be: read1, read2 and assembly_dir>
This file could look like:  
```
read1                     read2                     assembly_dir
path/sample_1/read1    path/sample_1/read2    path/sample_1/Spades_dir
path/sample_2/read1    path/sample_2/read2    path/sample_2/Spades_dir
```
Passing in this file means that the pipeline will not assemble the reads but run everything after the assembly step. 
        """,
    type=WssFile(
        expected_headers=[
            "read1",
            "read2",
            "assembly_dir",
        ],
        spades_column="assembly_dir",
    ),
)
@click.option(
    "-t",
    "--threads",
    help="Number of threads to run the application with",
    show_default=True,
    type=int,
    default=1,
)
@click.option(
    "-o",
    "--output",
    help="Output directory for the files produced by the pipeline",
    type=click.Path(exists=False),
)
@click.option(
    "-e",
    "--setup_env",
    help="Setup environment, this will be done automatically the first time the application is run",
    is_flag=True,
)
@click.option(
    "-n",
    "--dryrun",
    help="Run a dryrun for the specified files. Showing the parts of the pipeline which will be run ",
    is_flag=True,
)
def main(setup_env, reads, threads, dryrun, reads_and_assembly_dir, output):
    """
    \bThis is a program to run the Ptracker Snakemake pipeline to bin plasmids from metagenomic reads.
    The first time running the program it will try to install the genomad database (~3.1 G) and required scripts.
    For running the pipeline either the --reads or the --reads_and_assembly_dir arguments are required.
    Additionally, the --output argument is required which defines the output directory.
    For Quick Start please see the README: https://github.com/Las02/ptracker_workflow/tree/try_cli
    """

    environment_manager = EnvironmentManager()
    # Set up the environment
    if setup_env:
        environment_manager.setup_environment()
        sys.exit()

    if output is None:
        raise click.BadParameter(
            "--output is required",
        )

    if reads_and_assembly_dir is not None and reads is not None:
        raise click.BadParameter(
            "Both --reads_and_assembly and --reads are used, only use one of them",
        )

    if reads_and_assembly_dir is None and reads is None:
        raise click.BadParameter(
            "Neither --reads_and_assembly and --reads are used, please define one of them",
        )

    # Check if the environment is setup correctly, if not set it up
    if not environment_manager.check_if_everything_is_setup():
        environment_manager.setup_environment()

    snakemake_runner = SnakemakeRunner(snakefile="snakefile.smk")
    snakemake_runner.add_arguments(["-c", str(threads)])

    # Set output directory
    snakemake_runner.output_directory = output

    # Run the pipeline from the reads, meaning the pipeline will assemble the reads beforehand
    if reads is not None:
        snakemake_runner.add_to_config(f"read_file={reads}")
        snakemake_runner.to_print_while_running_snakemake = (
            f"Running snakemake with {threads} thread(s), from paired reads"
        )

    # Run the pipeline from the reads and the assembly graphs
    if reads_and_assembly_dir is not None:
        snakemake_runner.add_to_config(f"read_assembly_dir={reads_and_assembly_dir}")
        snakemake_runner.to_print_while_running_snakemake = f"Running snakemake with {threads} thread(s), from paired reads and assembly graph"

    if dryrun:
        snakemake_runner.add_arguments(["-n"])

    snakemake_runner.run()


if __name__ == "__main__":
    # Print --help if no arguments are passed
    if len(sys.argv) == 1:
        main(["--help"])
    else:
        main()
