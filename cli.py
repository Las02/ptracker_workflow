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

    def add_argument(self, argument, command=""):
        self.argument_holder += [argument, command]

    def add_arguments(self, arguments: List):
        self.argument_holder += arguments

    def clear_arguments(self):
        # TODO add safety
        self.argument_holder = [self.argument_holder[0]]

    def run(self):
        print("running:", self.argument_holder)
        # subprocess.run(self.argument_holder)


class Snakemake_runner(Cli_runner):
    argument_holder = []

    def __init__(self, logger: Logger):
        dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
        self.snakemake_path = shutil.which("snakemake")
        self.add_command_to_run(self.snakemake_path)
        self.snakefile_path = Path(Path(dir_of_current_file) / "snakefile")
        self.add_arguments(["--snakefile", self.snakefile_path])
        self.add_arguments(["-c", "8"])
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


class create_env:
    def __init__(self, logger: Logger):
        self.dir_of_current_file = Path(os.path.dirname(os.path.realpath(__file__)))
        self.git_path = shutil.which("git")
        self.logger = logger
        self.logger.print(f"Using git installation: {self.git_path}")

        self.plamb_dir = self.dir_of_current_file / "bin" / "plamb"

        self.plamb_ptracker_dir = (
            self.dir_of_current_file / "bin" / "plamb_ptracker_dir"
        )

    def clone_directories(self):
        git_cli_runner = Cli_runner()
        git_cli_runner.add_command_to_run(self.git_path)

        clone_plamb = [
            "clone",
            "https://github.com/RasmussenLab/vamb",
            "-b",
            "vamb_n2v_asy",
            self.plamb_dir,
        ]
        clone_plamb_ptracekr = [
            "clone",
            "https://github.com/Paupiera/ptracker",
            self.plamb_dir,
        ]

        for cli in [clone_plamb, clone_plamb_ptracekr]:
            git_cli_runner.add_arguments(cli)
            git_cli_runner.run()
            git_cli_runner.clear_arguments()

    def install_genomad_db(self):
        snakemake_runner = Snakemake_runner(self.logger)
        # Set target rule to genomad_db to create the database
        snakemake_runner.add_arguments(["genomad_db"])
        snakemake_runner.run()

    def setup(self):
        self.logger.print(
            f"Cloning plamb and ptracker to directory {self.plamb_ptracker_dir} and {self.plamb_ptracker_dir}"
        )
        self.clone_directories()
        self.logger.print(f"Installing Genomad database (~3.1 GB)")
        self.install_genomad_db()


@click.command()
# @click.option("--genomad_db", help="genomad database", type=click.Path(exists=True))
@click.option("--dryrun", help="run a dryrun", is_flag=True)
@click.option("--setup_env", help="Setup enviornment", is_flag=True)
def main(dryrun, setup_env):
    # if genomad_db == None:
    # raise click.BadParameter("genomad_db", param_hint=["--genomad_db"])

    logger = Logger()

    runner = Snakemake_runner(logger)

    if dryrun:
        runner.add_argument("-n")

    if setup_env:
        create_env(logger).setup()
        sys.exit()

    logger.print("running snakemake")
    runner.run()


if __name__ == "__main__":
    main()

    #    status = snakemake.snakemake(snakefile, configfile=paramsfile,
    #                              targets=[target], printshellcmds=True,
    #                              dryrun=args.dry_run, config=config)
    #
    # if status: # translate "success" into shell exit code of 0
    #    return 0
    # return 1
