import os
import shutil
from pathlib import Path

from loguru import logger

from workflow_plamb.command_line_runners import CliRunner, SnakemakeRunner


class EnvironmentManager:
    def __init__(self):
        self.dir_of_current_file = Path(os.path.dirname(os.path.realpath(__file__)))
        self.git_path = shutil.which("git")

        self.plamb_dir = self.dir_of_current_file / "bin" / "plamb"
        self.genomad_dir = self.dir_of_current_file / "genomad_db"

        self.plamb_ptracker_dir = (
            self.dir_of_current_file / "bin" / "plamb_ptracker_dir"
        )

        self.ptracker_exist = self.plamb_ptracker_dir.exists()
        self.plamb_exist = self.plamb_dir.exists()
        self.genomad_db_exist = (self.genomad_dir).exists()

    def clone_directory(self, cli):
        git_cli_runner = CliRunner()
        git_cli_runner.add_command_to_run(self.git_path)
        git_cli_runner.add_arguments(cli)
        git_cli_runner.run()

    def install_genomad_db(self):
        logger.info(f"Installing Genomad database (~3.1 GB) to {self.genomad_dir}")
        snakemake_runner = SnakemakeRunner()
        # Download the directory in the location of the current file
        snakemake_runner.add_arguments(["--directory", self.dir_of_current_file])
        # Use conda as the genomad and therefore the genomad environment needs to be used
        snakemake_runner.add_arguments(["--use-conda"])
        snakemake_runner.add_arguments(["-c", "1"])
        # Set target rule to genomad_db to create the database
        snakemake_runner.add_arguments(["download_genomad_db"])
        snakemake_runner.run()

    def install_conda_environments(self):
        logger.info(f"Installing conda environments")
        snakemake_runner = SnakemakeRunner()
        snakemake_runner.add_arguments(["--use-conda", "--conda-create-envs-only"])
        snakemake_runner.run()

    def setup(self):
        if False not in [self.ptracker_exist, self.plamb_exist, self.genomad_db_exist]:
            raise click.UsageError(
                "It seems that the environment has allready been setup. If something still not works, please add an issue to the repository"
            )
        logger.info("Setting up environment")

        if not self.ptracker_exist:
            logger.info(f"Using git installation: {self.git_path}")
            logger.info(f"Cloning ptracker to directory {self.plamb_ptracker_dir}")
            clone_plamb_ptracekr = [
                "clone",
                "git@github.com:Paupiera/ptracker",
                self.plamb_ptracker_dir,
            ]
            self.clone_directory(clone_plamb_ptracekr)

        if not self.plamb_exist:
            logger.info(f"Using git installation: {self.git_path}")
            logger.info(f"Cloning plamb to directory {self.plamb_dir}")
            clone_plamb = [
                "clone",
                "git@github.com:RasmussenLab/vamb",
                "-b",
                "vamb_n2v_asy",
                self.plamb_dir,
            ]
            self.clone_directory(clone_plamb)

        if not self.genomad_db_exist:
            self.install_genomad_db()

    def check_if_everything_is_setup(self):
        if True not in [self.ptracker_exist, self.plamb_exist, self.genomad_db_exist]:
            logger.info("It seems the environment has not been setup")
            return False
        if not self.ptracker_exist:
            raise click.UsageError(
                f"Could not find the plamb ptracker directory, try running the tool with --setup_env"
            )
        if not self.plamb_exist:
            raise click.UsageError(
                f"Could not find the plamb directory, try running the tool with --setup_env"
            )

        if not self.genomad_db_exist:
            raise click.UsageError(
                f"Could not find the genomad database, try running the tool with --setup_env"
            )
        return True
