from return_all import *
import yaml
import os
import sys
import subprocess
from pathlib import Path
import shutil
from typing import List
from collections import defaultdict

try:
    import rich_click as click
except ModuleNotFoundError:
    import click


class Smk_target_creater:
    """
    smk_target_creator = Smk_target_creater(samples=["sample1", "sample2"])
    targets = target_creator.create_targets(VambTypes=["Default"], runtimes=3)
    """

    dir_of_current_file = os.path.dirname(os.path.realpath(__file__))

    def __init__(
        self,
        samples: List[str],
        vambTypes: List[str],
        runtimes: int,
        from_bamfiles: bool = True,
    ):
        self.samples = samples
        self.vambTypes = vambTypes
        self.runtimes = runtimes
        self.from_bamfiles = from_bamfiles
        # for vambtype in vambTypes:
        #     assert vambtype in ["vamb_default"]

    def create_targets(self, output_dir: Path = None, as_dict=False) -> List[str]:
        dict_out = defaultdict(list)
        targets = []
        for sample in self.samples:
            to_add = []
            for vamb_type in self.vambTypes:
                if self.from_bamfiles:
                    to_add += self.add_vamb_runs(
                        f"sample_{sample}_{vamb_type}", default=True
                    )
                else:
                    to_add += self.add_vamb_runs(
                        f"sample_{sample}_{vamb_type}", default=False
                    )
            if output_dir is not None:
                to_add = [output_dir / x for x in to_add]
            targets += to_add
            dict_out[sample] += to_add

        if as_dict:
            return dict_out
        return targets

    def add_vamb_runs(self, sample_vamb_type: str, default: bool) -> List[str]:
        # If it should only be run one time, it is run from bamfiles and contigfiles.
        if self.runtimes == 1 and default:
            return [sample_vamb_type + f"_run_1_from_bam_contig"]
        elif default:
            start_int = 2
        else:
            start_int = 1

        # All should be made from rpkm and composition
        out_targets = []
        for run_number in range(start_int, self.runtimes + 1, 1):
            out_targets.append(sample_vamb_type + f"_run_{run_number}_from_rpkm_comp")
        return out_targets

        # def add_vamb_runs_vamb_default(self, sample_vamb_type: str) -> List[str]:
        #     out_targets = []
        #     # Dont create all from rpkm and composition of the first
        #     for run_number in range(2, self.runtimes + 1, 1):
        #         out_targets.append(sample_vamb_type + f"_run_{run_number}_from_rpkm_comp")

        return out_targets


class Logger:
    def print(self, arg):
        click.echo(click.style(arg, fg="yellow"))

    def warn(self, arg):
        click.echo(click.style("WARNING:   " + arg, fg="red", underline=True))


class Cli_runner:
    argument_holder = []
    _command_has_been_added = False
    _cwd = None

    def add_command_to_run(self, command_to_run):
        if self._command_has_been_added:
            raise Exception(
                f"A command has allready been added: {self.argument_holder[0]}"
            )
        self.argument_holder = [command_to_run] + self.argument_holder
        self._command_has_been_added = True

    def add_arguments(self, arguments: List):
        arguments = [arg for arg in arguments if arg != None]
        self.argument_holder += arguments

    def clear_arguments(self):
        if self._command_has_been_added:
            self.argument_holder = [self.argument_holder[0]]
        else:
            self.argument_holder = []

    def cwd(self, cwd):
        self._cwd = cwd

    def prettyprint_args(self):
        [print(x, end=" ") for x in self.argument_holder]
        print()

    def run(self, dry_run_command=False):
        if dry_run_command:
            print("running:", self.argument_holder)
        else:
            print("Running:")
            self.prettyprint_args()
            if self._cwd == None:
                subprocess.run(self.argument_holder, check=True)
            else:
                print(f"cwd: {self._cwd}")
                subprocess.run(self.argument_holder, cwd=self._cwd, check=True)
            print("Ran:")
            self.prettyprint_args()


class Snakemake_runner(Cli_runner):
    argument_holder = []
    to_print_while_running_snakemake = None
    config_options = None
    target_rule = None
    snakemake_path = shutil.which("snakemake")
    dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
    output_directory = os.getcwd()
    vamb_run_nam = None
    vamb_conda_env_yamlfile = None

    def __init__(self, logger: Logger, snakefile: str = "snakefile.py"):
        self.add_command_to_run(self.snakemake_path)
        self.snakefile_path = Path(Path(self.dir_of_current_file) / snakefile)
        self.add_arguments(["--snakefile", self.snakefile_path])
        self.add_arguments(["--rerun-triggers", "mtime"])
        self.add_arguments(["--nolock"])
        self.logger = logger
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
            self.logger.warn(
                "Could not find mamba installation, is the correct environment activated?"
            )
            self.logger.warn(
                "Defaulting to use conda to build environments for snakemake, this will be slower"
            )
            self.add_arguments(["--conda-frontend", "conda"])

    def add_to_config(self, to_add):
        if self.config_options is None:
            self.config_options = []
        self.config_options += [to_add]

    def set_vamb_run_name(self, refhash, branch):
        self.vamb_run_nam = f"vamb_run_name=r_{refhash}_b_{branch}"

    def set_vamb_conda_env_yamlfile(self, vamb_conda_env_yamlfile):
        self.vamb_conda_env_yamlfile = (
            f"vamb_conda_env_yamlfile={vamb_conda_env_yamlfile}"
        )

    def set_target_rule(self, to_add):
        self.target_rule = to_add

    def run(self):
        # Store old settings
        old_config = self.config_options.copy()
        old_argument_holder = self.argument_holder.copy()

        self.add_to_config(f"output_directory={self.output_directory}")
        self.add_to_config(f"dir_of_current_file={self.dir_of_current_file}")

        if self.vamb_run_nam is not None:
            self.add_to_config(self.vamb_run_nam)
        if self.vamb_conda_env_yamlfile is not None:
            self.add_to_config(self.vamb_conda_env_yamlfile)

        # Add config options
        if self.config_options is not None:
            self.add_arguments((["--config"] + self.config_options))
        # Log
        if self.to_print_while_running_snakemake is not None:
            self.logger.print(self.to_print_while_running_snakemake)

        # use conda: always
        self.add_arguments(["--use-conda"])
        self.add_arguments(["--rerun-incomplete"])

        # Needs to be added last
        if self.target_rule is not None:
            self.add_arguments((self.target_rule))

        # Run
        super().run()

        # Restore old settings for running the tool several times changing only some options
        self.config_options = old_config
        self.argument_holder = old_argument_holder


class Environment_setupper:
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

    def create_conda_env_yaml(self, refhash: str, branch: str) -> Path:
        vamb_location = (
            self.dir_of_current_file / "bin" / f"vamb_branch_{branch}_commit_{refhash}"
        )
        with open(self.dir_of_current_file / "envs" / "vamb_env.yaml", "r") as in_file:
            # Set up yaml to build env with correct vamb version
            yaml_vamb_env = yaml.safe_load(in_file)
            # TODO add way to safely rename pip dependencies without it having to be the last element
            yaml_vamb_env["dependencies"][-1]["pip"] = ["-e " + str(vamb_location)]
            yaml_vamb_env["name"] = str(yaml_vamb_env["name"] + f"_{refhash}")
            # Write the yaml file
            out_file_path = f"{self.dir_of_current_file}/envs/vamb_branch_{branch}_commit_{refhash}.yaml"
            with open(out_file_path, "w") as out_file:
                yaml.dump(yaml_vamb_env, out_file)
        return Path(out_file_path)

    def run_git(self, cli, cwd=None):
        git_cli_runner = Cli_runner()
        git_cli_runner.add_command_to_run(self.git_path)
        git_cli_runner.add_arguments(cli)
        git_cli_runner.cwd(cwd)
        git_cli_runner.run()

    def install_conda_environments(self):
        self.logger.print(f"Installing conda environments")
        snakemake_runner = Snakemake_runner(self.logger)
        snakemake_runner.add_arguments(["--use-conda", "--conda-create-envs-only"])
        snakemake_runner.run()

    def clone_vamb_github(self, refhash: str, branch: str):
        vamb_location = (
            self.dir_of_current_file / "bin" / f"vamb_branch_{branch}_commit_{refhash}"
        )
        if not vamb_location.exists():
            self.logger.print(f"Using git installation: {self.git_path}")
            self.logger.print(
                f"Cloning vamb branch: {branch}, commit: {refhash}, to directory {vamb_location}"
            )
            self.run_git(
                [
                    "clone",
                    "git@github.com:RasmussenLab/vamb",
                    "-b",
                    branch,
                    vamb_location,
                ]
            )
            # Checkout the commit given, if not latest
            if refhash != "latest":
                self.run_git(["checkout", refhash, "-q"], cwd=vamb_location)

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
                "git@github.com:Paupiera/ptracker",
                self.plamb_ptracker_dir,
            ]
            self.clone_directory(clone_plamb_ptracekr)

        if not self.plamb_exist:
            self.logger.print(f"Using git installation: {self.git_path}")
            self.logger.print(f"Cloning plamb to directory {self.plamb_dir}")
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
            self.logger.print("It seems the environment has not been setup")
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


class BinBencher(Cli_runner):
    output = None
    target_result = None

    def __init__(self, reference: str, targets: List[str]) -> None:
        super().__init__()
        self.julia_path = shutil.which("julia")
        self.validate_paths()
        self.add_command_to_run(self.julia_path)
        self.targets = targets
        self.reference = reference
        self.tool_to_run = "./BinBencher"
        self.cwd(Path(os.path.dirname(os.path.realpath(__file__))))
        self.has_been_run = []

    def run_all_targets(self, dry_run_command=False):
        self.target_result = defaultdict()
        for target in self.targets:
            self.clear_arguments()
            self.add_arguments([self.tool_to_run])
            self.add_arguments([self.reference])
            # Only organisms
            self.add_arguments(["true"])
            self.add_arguments([target])
            # Assembly
            self.add_arguments(["true"])
            self.run(dry_run_command=dry_run_command)
            if not dry_run_command:
                self.target_result[target] = self.get_output()

    def get_benchmarks(self):
        if self.target_result is None:
            raise Exception("run cmd has not been run")
        return dict(self.target_result)

    def run(self, dry_run_command=False):
        if dry_run_command:
            print("running:", self.argument_holder)
        else:
            print("Running:")
            self.prettyprint_args()
            print(f"cwd: {self._cwd}")
            self.output = subprocess.run(
                self.argument_holder, cwd=self._cwd, stdout=subprocess.PIPE
            )
            print("Ran:")
            self.prettyprint_args()

        self.has_been_run.append(self.argument_holder)

    def get_output(self):
        if self.output is None:
            raise Exception("run cmd has not been run or did not create any std.out")
        return int(self.output.stdout.decode("utf-8").strip())

    def validate_paths(self):
        if self.julia_path is None:
            raise click.UsageError("""Could not find julia, is it installed?""")


def output_binbencher_results(targets_dict, df, output_file, logger, refhash):
    targets2benchmark = defaultdict()
    logger.print("Starting running BinBencher")
    sample2ref = {sample: ref for sample, ref in zip(df["sample"], df["reference"])}
    for sample in targets_dict.keys():
        binbencher = BinBencher(
            reference=sample2ref[sample], targets=[x / "vae_clusters_split.tsv" for x in targets_dict[sample]]
        )
        # binbencher.tool_to_run = "./test_stuff/test_binbench.jl"  # WARNING remove this
        binbencher.tool_to_run = os.path.dirname(os.path.realpath(__file__)) + "/Binbench.jl"
        binbencher.run_all_targets(dry_run_command=False)
        targets2benchmark.update(binbencher.get_benchmarks())

    # TODO print in a nice format including vamb_type, run_number etc. formatted in different columns
    # if not output_file.exists():
    #     output_file.mkdir()
    with open(output_file, "a") as f:
        # print("refhash\ttarget\tbenchmark", file=f)
        for target, benchmark in targets2benchmark.items():
            print(f"{refhash}\t{target}\t{benchmark}", file=f)
    logger.print(f"Finished running BinBencher, output files in {output_file}")
