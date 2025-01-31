import os
import shutil
from typing import List

from loguru import logger


class CliRunner:
    _argument_holder = []
    _command_has_been_added = False

    def add_command_to_run(self, command_to_run):
        if self._command_has_been_added:
            raise Exception(
                f"A command has allready been added: {self._argument_holder[0]}"
            )
        self._argument_holder = [command_to_run] + self._argument_holder
        self._command_has_been_added = True

    def add_arguments(self, arguments: List):
        self._argument_holder += arguments

    def prettyprint_args(self):
        [print(x, end=" ") for x in self._argument_holder]
        print()

    def run(self, dry_run_command=False):
        if dry_run_command:
            logger.info("running:", self._argument_holder)
        else:
            print("Running:")
            self.prettyprint_args()
            subprocess.run(self._argument_holder)
            print("Ran:")
            self.prettyprint_args()


class SnakemakeRunner(CliRunner):
    _argument_holder = []
    to_print_while_running_snakemake = None
    config_options = []
    snakemake_path = shutil.which("snakemake")
    dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
    output_directory = os.getcwd()

    def __init__(self, snakefile: str = "snakefile.smk"):
        self.add_command_to_run(self.snakemake_path)
        self.snakefile_path = Path(Path(self.dir_of_current_file) / snakefile)
        self.add_arguments(["--snakefile", self.snakefile_path])
        self.add_arguments(["--rerun-triggers", "mtime"])
        self.add_arguments(["--nolock"])
        self.validate_paths()
        # default to run snakemake in current directory
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

        if shutil.which("mamba") is None:
            logger.warning(
                "Could not find mamba installation, is the correct environment activated?"
            )
            logger.warning(
                "Defaulting to use conda to build environments for snakemake, this will be slower"
            )
            self.add_arguments(["--conda-frontend", "conda"])

    def add_to_config(self, to_add):
        self.config_options += [to_add]

    def run(self):
        # use conda: always
        self.add_arguments(["--use-conda"])
        self.add_arguments(["--rerun-incomplete"])

        self.add_to_config(f"output_directory={self.output_directory}")
        self.add_to_config(f"dir_of_current_file={self.dir_of_current_file}")
        # Add config options
        self.add_arguments((["--config"] + self.config_options))
        # Log
        if self.to_print_while_running_snakemake is not None:
            logger.info(self.to_print_while_running_snakemake)
        # Run
        super().run()
