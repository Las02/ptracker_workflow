#!/usr/bin/env python3
try:
    import rich_click as click

    # Only set rich_click options if rich_click is installed else default to basic click package
    click.rich_click.OPTION_GROUPS = {
        "cli.py": [
            {
                "name": "Defining input files: One of these are required",
                "options": ["--reads", "--reads_and_assembly_dir"],
            },
            {
                "name": "Basic Usage",
                "options": ["--output", "--threads"],
            },
            {
                "name": "Other Options",
                "options": ["--dryrun", "--setup_env", "--help"],
            },
        ],
    }
except ModuleNotFoundError as e:
    try:
        import click
    except ModuleNotFoundError as e:
        print("""\nCould not find module click or module rich_click, please make sure to create an environment containing 
either of modueles eg. using conda or pip. See the user guide on the github README.\n""")
        raise e


from os.path import exists

from pandas.core.generic import config
from return_all import *
import os
import sys
import subprocess
from pathlib import Path
import shutil
from typing import List

# click.rich_click.USE_RICH_MARKUP = True


class Logger:
    def print(self, arg):
        # click.echo(arg)
        click.echo(click.style(arg, fg="yellow"))


# Snakemake should handle genomad download
# Only downloading conda envs
# snakemake --use-conda --conda-create-envs-only -c4 --conda-frontend conda
# genomad database download?


# def validate_paths(self):
#


class Cli_runner:
    argument_holder = []

    def add_command_to_run(self, command_to_run):
        self.argument_holder = [command_to_run] + self.argument_holder

    # def add_argument(self, argument, command=""):
    #     self.argument_holder += [argument, command]

    def add_arguments(self, arguments: List):
        self.argument_holder += arguments

    def prettyprint_args(self):
        [print(x, end=" ") for x in self.argument_holder]
        print()

    def run(self, dry_run_command=False):
        if dry_run_command:
            print("running:", self.argument_holder)
        else:
            print("Running:")
            self.prettyprint_args()
            subprocess.run(self.argument_holder)
            print("Ran:")
            self.prettyprint_args()


class Snakemake_runner(Cli_runner):
    argument_holder = []
    to_print_while_running_snakemake = None
    config_options = []
    snakemake_path = shutil.which("snakemake")
    dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
    output_directory = os.getcwd()

    def __init__(self, logger: Logger, snakefile: str = "snakefile.py"):
        self.add_command_to_run(self.snakemake_path)
        self.snakefile_path = Path(Path(self.dir_of_current_file) / snakefile)
        self.add_arguments(["--snakefile", self.snakefile_path])
        self.validate_paths()
        # default to run snakemake in current directory
        self.logger = logger
        # Config needs to be added in a special way

    def validate_paths(self):
        if not self.snakefile_path.exists():
            raise click.UsageError(
                f"Could not find snakefile, tried: {self.snakefile_path}"
            )

        if self.snakemake_path is None:
            raise click.UsageError(
                """Could not find snakemake, is it installed?
See following installation guide: https://snakemake.readthedocs.io/en/stable/getting_started/installation.html"""
            )

    def add_to_config(self, to_add):
        self.config_options += [to_add]

    def run(self):
        self.add_to_config(f"output_directory={self.output_directory}")
        # Add config options
        self.add_arguments((["--config"] + self.config_options))
        # Log
        self.logger.print(self.to_print_while_running_snakemake)
        # use conda: always
        snakemake_runner.add_arguments(["--use-conda"])
        # Run
        super().run()


class environment_setupper:
    def __init__(self, logger: Logger):
        self.dir_of_current_file = Path(os.path.dirname(os.path.realpath(__file__)))
        self.git_path = shutil.which("git")
        self.logger = logger

        self.plamb_dir = self.dir_of_current_file / "bin" / "plamb"
        self.genomad_dir = self.dir_of_current_file / "genomad_db"

        self.plamb_ptracker_dir = (
            self.dir_of_current_file / "bin" / "plamb_ptracker_dir"
        )

        self.ptracker_exist = self.plamb_ptracker_dir.exists()
        self.plamb_exist = self.plamb_dir.exists()
        self.genomad_db_exist = (self.genomad_dir).exists()

    def clone_directory(self, cli):
        git_cli_runner = Cli_runner()
        git_cli_runner.add_command_to_run(self.git_path)
        git_cli_runner.add_arguments(cli)
        git_cli_runner.run()

    def install_genomad_db(self):
        self.logger.print(
            f"Installing Genomad database (~3.1 GB) to {self.genomad_dir}"
        )
        snakemake_runner = Snakemake_runner(self.logger)
        # Set target rule to genomad_db to create the database
        snakemake_runner.add_arguments(["download_genomad_db"])
        # Download the directory in the location of the current file
        snakemake_runner.add_arguments(["--directory", self.dir_of_current_file])
        # Use conda as the genomad and therefore the genomad environment needs to be used
        snakemake_runner.add_arguments(["--use-conda"])
        snakemake_runner.run()

    def install_conda_environments(self):
        self.logger.print(f"Installing conda environments")
        snakemake_runner = Snakemake_runner(self.logger)
        snakemake_runner.add_arguments(["--use-conda", "--conda-create-envs-only"])
        snakemake_runner.run()

    def setup(self):
        if False not in [self.ptracker_exist, self.plamb_exist, self.genomad_db_exist]:
            raise click.UsageError(
                "It seems that the environment has allready been setup. If something still not works, please add an issue to the repository"
            )
        self.logger.print("Setting up environment")

        if not self.ptracker_exist:
            self.logger.print(f"Using git installation: {self.git_path}")
            self.logger.print(
                f"Cloning ptracker to directory {self.plamb_ptracker_dir}"
            )
            clone_plamb_ptracekr = [
                "clone",
                "https://github.com/Paupiera/ptracker",
                self.plamb_ptracker_dir,
            ]
            self.clone_directory(clone_plamb_ptracekr)

        if not self.plamb_exist:
            self.logger.print(f"Using git installation: {self.git_path}")
            self.logger.print(f"Cloning plamb to directory {self.plamb_dir}")
            clone_plamb = [
                "clone",
                "https://github.com/RasmussenLab/vamb",
                "-b",
                "vamb_n2v_asy",
                self.plamb_dir,
            ]
            self.clone_directory(clone_plamb)

        if not self.genomad_db_exist:
            self.install_genomad_db()

    def check_if_everything_is_setup(self):
        if True not in [self.ptracker_exist, self.plamb_exist, self.genomad_db_exist]:
            self.logger.print("It seems the environment has not been setup")
            return False
        if not self.ptracker_exist:
            raise click.UsageError(
                f"Could not find the plamb ptracker directory, try running the tool with --setup-env"
            )
        if not self.plamb_exist:
            raise click.UsageError(
                f"Could not find the plamb directory, try running the tool with --setup-env"
            )

        if not self.genomad_db_exist:
            raise click.UsageError(
                f"Could not find the genomad database, try running the tool with --setup-env"
            )
        return True


class List_of_files(click.ParamType):
    name = "List of paths"

    def convert(self, value, param, ctx):
        for file in value:
            if not Path(file).exists():
                self.fail(f"{file!r} is not a valid path", param, ctx)
        return list(value)


@click.command()
# @click.option("--genomad_db", help="genomad database", type=click.Path(exists=True))
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
    type=wss_file(
        Logger(),
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
    type=wss_file(
        Logger(),
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
    help="Output directory, defaults to the directory which the command is run in",
    type=click.Path(exists=False),
)
@click.option(
    "-e",
    "--setup_env",
    help="Setup environment, this will be done automatically the first time the application is ran",
    is_flag=True,
)
@click.option(
    "-n",
    "--dryrun",
    help="Run a dryrun for the specified files. Showing the parts of the pipeline which will be run ",
    is_flag=True,
)
# @click.option("--r1", cls=OptionEatAll, type=List_of_files())
# @click.option("--r2", cls=OptionEatAll, type=List_of_files())
def main(setup_env, reads, threads, dryrun, reads_and_assembly_dir, output):
    """
    \bThis is a program to run the Ptracker Snakemake pipeline to bin plasmids from metagenomic reads.
    The first time running the program it will try to install the genomad database (~3.1 G) and required scripts.
    For running the pipeline either the --reads or the --reads_and_assembly_dir arguments are required.
    For Quick Start please see the README: https://github.com/Las02/ptracker_workflow/tree/try_cli
    """
    logger = Logger()

    # Set up the environment
    if setup_env:
        environment_setupper(logger).setup()
        sys.exit()

    # Check if the environment is setup correctly, if not set it up
    if not environment_setupper(logger).check_if_everything_is_setup():
        environment_setupper(logger).setup()

    if reads_and_assembly_dir is not None and reads is not None:
        raise click.BadParameter(
            "Both --reads_and_assembly and --reads are used, only use one of them",
        )
    if reads_and_assembly_dir is None and reads is None:
        raise click.BadParameter(
            "Neither --reads_and_assembly and --reads are used, please define one of them",
        )

    snakemake_runner = Snakemake_runner(logger)
    snakemake_runner.add_arguments(["-c", str(threads)])

    # Set output dir if argument is set else default to CWD
    if output is not None:
        snakemake_runner.output_directory = output

    # Run the pipeline from the reads, meaning the pipeline will assemble the reads beforehand
    if reads is not None:
        snakemake_runner.add_to_config(f"read_file={reads}")
        snakemake_runner.to_print_while_running_snakemake = (
            f"running snakemake with {threads} thread(s), from paired reads"
        )

    # Run the pipeline from the reads and the assembly graphs
    if reads_and_assembly_dir is not None:
        snakemake_runner.add_to_config(f"read_assembly_dir={reads_and_assembly_dir}")
        snakemake_runner.to_print_while_running_snakemake = f"running snakemake with {threads} thread(s), from paired reads and assembly graph"

    if dryrun:
        snakemake_runner.add_arguments(["-n"])

    snakemake_runner.run()


if __name__ == "__main__":
    # Print --help if no arguments are passed in
    if len(sys.argv) == 1:
        main(["--help"])
    else:
        main()

    #    status = snakemake.snakemake(snakefile, configfile=paramsfile,
    #                              targets=[target], printshellcmds=True,
    #                              dryrun=args.dry_run, config=config)
    #
    # if status: # translate "success" into shell exit code of 0
    #    return 0
    # return 1
