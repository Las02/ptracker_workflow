#!/usr/bin/env python3
try:
    import rich_click as click
except ModuleNotFoundError as e:
    try:
        import click
    except ModuleNotFoundError as e:
        print("""\nCould not find module click or module rich_click, please make sure to create an environment containing 
either of modueles eg. using conda or pip. See the user guide on the github README.\n""")
        raise e


from os.path import exists
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

    def clear_arguments(self):
        # TODO add safety
        self.argument_holder = [self.argument_holder[0]]

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

    def __init__(self, logger: Logger, snakefile: str = "snakefile.py"):
        dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
        self.snakemake_path = shutil.which("snakemake")
        self.add_command_to_run(self.snakemake_path)
        self.snakefile_path = Path(Path(dir_of_current_file) / snakefile)
        self.add_arguments(["--snakefile", self.snakefile_path])
        self.validate_paths()

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
        snakemake_runner.add_arguments(["genomad_db"])
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

        if not self.ptracker_exist:
            self.logger.print(f"Using git installation: {self.git_path}")
            self.logger.print(
                f"Cloning ptracker to directory {self.plamb_ptracker_dir}"
            )
            clone_plamb_ptracekr = [
                "clone",
                "https://github.com/Paupiera/ptracker",
                self.plamb_dir,
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
            raise click.UsageError(
                "It seems the environment has not been setup run --setup_env to set up the environment"
            )
        if not self.ptracker_exist:
            raise click.UsageError(f"Could not find the plamb ptracker directory")
        if not self.plamb_exist:
            raise click.UsageError(f"Could not find the plamb directory")
        if not self.genomad_db_exist:
            raise click.UsageError(f"Could not find the genomad database")


class List_of_files(click.ParamType):
    name = "List of paths"

    def convert(self, value, param, ctx):
        for file in value:
            if not Path(file).exists():
                self.fail(f"{file!r} is not a valid path", param, ctx)
        return list(value)


@click.command()
# @click.option("--genomad_db", help="genomad database", type=click.Path(exists=True))
@click.option("--dryrun", help="run a dryrun", is_flag=True)
@click.option("--setup_env", help="Setup enviornment", is_flag=True)
@click.option(
    "--threads", help="threads to run the application with", type=int, default=1
)
@click.option(
    "--reads",
    help="white space seperated file containing read pairs",
    type=wss_file(
        Logger(),
        expected_headers=["sample", "read1", "read2"],
        none_file_columns=["sample"],
    ),
)
@click.option(
    "--reads_and_assembly",
    help="white space seperated file containing read pairs and assembly",
    type=wss_file(
        Logger(),
        expected_headers=[
            "sample",
            "read1",
            "read2",
            "assembly_graph",
            "contig",
            "contig_paths",
        ],
        none_file_columns=["sample"],
    ),
)
# @click.option("--r1", cls=OptionEatAll, type=List_of_files())
# @click.option("--r2", cls=OptionEatAll, type=List_of_files())
def main(dryrun, setup_env, reads, reads_and_assembly, threads):
    logger = Logger()

    # Set up the environment
    if setup_env:
        environment_setupper(logger).setup()
        sys.exit()

    # Check if the environment is setup correctly
    environment_setupper(logger).check_if_everything_is_setup()

    if reads_and_assembly != None and reads != None:
        raise click.BadParameter(
            "Both --reads_and_assembly and --reads are used, only use one of them",
        )

    snakemake_runner = Snakemake_runner(logger)
    snakemake_runner.add_arguments(["-c", str(threads)])

    # Run the pipeline from the reads, meaning the pipeline will assemble the reads beforehand
    if reads != None:
        snakemake_runner.add_arguments(["--config", f"read_file={reads}"])
        to_print_while_running_snakemake = (
            f"running snakemake with {threads} thread(s), from paired reads"
        )

    # Run the pipeline from the reads and the assembly graphs
    if reads_and_assembly != None:
        snakemake_runner.add_arguments(
            ["--config", f"read_assembly_file={reads_and_assembly}"]
        )
        to_print_while_running_snakemake = f"running snakemake with {threads} thread(s), from paired reads and assembly graph"

    if dryrun:
        snakemake_runner.add_arguments(["-n"])

    logger.print(to_print_while_running_snakemake)
    snakemake_runner.run()


if __name__ == "__main__":
    main()

    #    status = snakemake.snakemake(snakefile, configfile=paramsfile,
    #                              targets=[target], printshellcmds=True,
    #                              dryrun=args.dry_run, config=config)
    #
    # if status: # translate "success" into shell exit code of 0
    #    return 0
    # return 1
