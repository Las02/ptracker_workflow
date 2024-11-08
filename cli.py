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

# click.rich_click.USE_RICH_MARKUP = True


class Logger:
    def print(self, arg):
        click.echo(arg)


# Snakemake should handle genomad download
# Only downloading conda envs
# snakemake --use-conda --conda-create-envs-only -c4 --conda-frontend conda
# genomad database download?


# def validate_paths(self):
#
class cli_runner:
    argument_holder = []


class Snakemake_runner:
    argument_holder = []

    def __init__(self, logger: Logger):
        dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
        self.snakemake_path = shutil.which("snakemake")
        self.snakefile_path = Path(Path(dir_of_current_file) / "snakefile")
        self.add_argument("--snakefile", self.snakefile_path)
        self.add_argument("-c", "4")

    def add_argument(self, argument, command=""):
        self.argument_holder += [argument, command]

    def run_snakemake(self):
        cmd = [self.snakemake_path] + self.argument_holder
        print(cmd)
        subprocess.run(cmd)

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
        self.dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
        self.git_path = shutil.which("git")
        self.logger = logger
        self.logger.print(f"using git installation: {self.git_path}")

    def setup(self):
        self.logger.print(f"Cloning plamb to directory {self.dir_of_current_file}")


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

    runner.validate_paths()
    logger.print("running snakemake")
    runner.run_snakemake()


if __name__ == "__main__":
    main()

    #    status = snakemake.snakemake(snakefile, configfile=paramsfile,
    #                              targets=[target], printshellcmds=True,
    #                              dryrun=args.dry_run, config=config)
    #
    # if status: # translate "success" into shell exit code of 0
    #    return 0
    # return 1
