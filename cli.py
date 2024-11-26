#!/usr/bin/env python3
# Import rich_click if installed else default to click.
# If none are installed write errormessage
try:
    import rich_click as click

    # Only set rich_click options if rich_click is installed else default to basic click package
    click.rich_click.OPTION_GROUPS = {
        "cli.py": [
            {
                "name": "Defining input files: One of these options are required",
                "options": ["--reads", "--reads_and_assembly_dir"],
            },
            {
                "name": "Additional Required Arguments",
                "options": [
                    "--output",
                ],
                "table_styles": {
                    "row_styles": ["yellow", "default", "default", "default"],
                },
            },
            {
                "name": "Other Options",
                "options": [
                    "--threads",
                    "--dryrun",
                    "--setup_env",
                    "--help",
                    "--branch",
                ],
                "table_styles": {
                    "row_styles": ["yellow", "default", "default", "default"],
                },
            },
        ],
    }
    click.rich_click.USE_RICH_MARKUP = True
except ModuleNotFoundError as e:
    try:
        import click
    except ModuleNotFoundError as e:
        print("""\nCould not find module click or module rich_click, please make sure to create an environment containing 
either of modueles eg. using conda or pip. See the user guide on the github README.\n""")
        raise e


import yaml
from pandas.core.generic import config
from return_all import *
import os
import sys
import subprocess
from pathlib import Path
import shutil
from typing import List
from collections import defaultdict


# Make both -h and --help available instead of just --help
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


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
        if default:
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
        self.vamb_conda_env_yamlfile = f"vamb_conda_env_yamlfile={vamb_conda_env_yamlfile}"



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
        self.argument_holder  = old_argument_holder 



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
            yaml_vamb_env["dependencies"][-1]["pip"] = ["-e", str(vamb_location)]
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
            self.add_arguments([target])
            self.add_arguments([self.reference])
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
            # print("Running:")
            # self.prettyprint_args()
            # print(f"cwd: {self._cwd}")
            self.output = subprocess.run(
                self.argument_holder, cwd=self._cwd, stdout=subprocess.PIPE
            )
            # print("Ran:")
            # self.prettyprint_args()

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
            reference=sample2ref[sample], targets=targets_dict[sample]
        )
        binbencher.tool_to_run = "./test_stuff/test_binbench.jl" # WARNING remove this
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


# class List_of_files(click.ParamType):
#     name = "List of paths"
#
#     def convert(self, value, param, ctx):
#         for file in value:
#             if not Path(file).exists():
#                 self.fail(f"{file!r} is not a valid path", param, ctx)
#         return list(value)


@click.command()
# @click.option("--genomad_db", help="genomad database", type=click.Path(exists=True))
# TODO add test of bamfiles directory
@click.option(
    "-b",
    "--contig_bamfiles",
    help="""\bWhite space separated file containing sample, contig and directory_of_bamfiles. 
<Notice the header names are required to be: sample, contig and directory_of_bamfiles>
This file could look like:
```
sample      contig                           directory_of_bamfiles
sample1     path/to/sample_1/contig.fasta    path/to/sample_1/bamfiles_dir
sample2     path/to/sample_2/contig.fasta    path/to/sample_2/bamfiles_dir
```
# Passing in this file means that the pipeline will be run from the start, meaning it will also assemble the reads.

""",
    type=click.Path(exists=True),
    # type=wss_file(
    #     Logger(),
    #     expected_headers=["sample", "contig", "directory_of_bamfiles"],
    #     none_file_columns=["sample"],
    # ),
)
@click.option(
    "-c",
    "--composition_and_rpkm",
    help=f"""\bWhite space separated file containing read pairs and paths to Spades output assembly directories.
<Notice the header names are required to be: sample, composition and rpkm>
This file could look like:  
```
sample      composition                       rpkm
sample1     path/to/sample_1/composition.npz  path/to/sample_1/rpkm.npz
sample2     path/to/sample_2/composition.npz  path/to/sample_2/rpkm.npz
```
Passing in this file means that the pipeline will not assemble the reads but run everything after the assembly step. 
        """,
    type=click.Path(exists=True),
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
# @click.option("--r1", cls=OptionEatAll, type=List_of_files())
@click.option("-b", "--branch", default="master", show_default=True)
@click.option("-r", "--runtimes", type=int, default=1, show_default=True)
@click.option("-d", "--vamb_default", is_flag=True)
@click.option("-d", "--avamb", is_flag=True)
@click.option("-b", "--run_binbencher", is_flag=True)
@click.option("-b", "--taxvamb", is_flag=True)
@click.option("-b", "--taxvamb_and_taxometer", is_flag=True)
@click.option("-b", "--taxometer", is_flag=True)
# @click.option( "-o", "--vamb_options", default="master", help="Pass in options to vamb", show_default=True,)
# @click.option( "-s", "--snakemake_options", default="master", help="Pass in options to snakemake", show_default=True,)
@click.option(
    "-r",
    "--refhash",
    help="Commits to run the pipeline for",
    cls=OptionEatAll,
    type=One_or_more_commit_hashes(),
)
def main(
    setup_env,
    threads,
    dryrun,
    branch,
    composition_and_rpkm,
    contig_bamfiles,
    output,
    refhash,
    runtimes,
    vamb_default,
    avamb,
    run_binbencher: bool,
    taxvamb: bool,
    taxometer: bool,
    taxvamb_and_taxometer: bool,
):
    """
    \bThis is a program to run the Ptracker Snakemake pipeline to bin plasmids from metagenomic reads.
    The first time running the program it will try to install the genomad database (~3.1 G) and required scripts.
    For running the pipeline either the --reads or the --reads_and_assembly_dir arguments are required.
    Additionally, the --output argument is required which defines the output directory.
    For Quick Start please see the README: https://github.com/Las02/ptracker_workflow/tree/try_cli
    """

    if output is None:
        raise click.BadParameter(
            "--output is required",
        )

    if contig_bamfiles is None and composition_and_rpkm is None:
        raise click.BadParameter(
            "Neither --contig_bamfiles and --composition_and_rpkm are used, please define one of them",
        )

    if contig_bamfiles is not None and composition_and_rpkm is not None:
        raise click.BadParameter(
            "Both --contig_bamfiles and --composition_and_rpkm are used, only use one of them",
        )

    vamb_types = []
    if vamb_default:
        vamb_types.append("vamb_default")
    if avamb:
        vamb_types.append("avamb")
    if taxvamb:
        vamb_types.append("taxvamb")
    if taxvamb_and_taxometer:
        vamb_types.append("taxvamb_and_taxometer")

    if len(vamb_types) == 0:
        raise click.BadParameter("No vamb types is defined")

    logger = Logger()

    if contig_bamfiles is not None:
        expected_headers = ["sample", "contig", "directory_of_bamfiles"]
        if run_binbencher:
            expected_headers += ["reference"]
        if taxvamb or taxometer or taxvamb_and_taxometer:
            expected_headers += ["taxonomy"]
        path_contig_bamfiles, df = wss_file_checker(
            Logger(),
            expected_headers=expected_headers,
            none_file_columns=["sample"],
        ).get_info(contig_bamfiles, param="contig_bamfiles")

    if composition_and_rpkm is not None:
        expected_headers = ["sample", "composition", "rpkm"]
        if run_binbencher:
            expected_headers += ["reference"]
        if taxvamb or taxometer or taxvamb_and_taxometer:
            expected_headers += ["taxonomy"]
        path_composition_and_rpkm, df = wss_file_checker(
            Logger(),
            expected_headers=expected_headers,
            none_file_columns=["sample"],
        ).get_info(composition_and_rpkm, param="contig_bamfiles")


    snakemake_runner = Snakemake_runner(logger)
    snakemake_runner.add_arguments(["-c", str(threads)])

    if taxvamb or taxometer or taxvamb_and_taxometer:
        snakemake_runner.add_to_config(f"taxonomy_information=yes")

    if contig_bamfiles is not None:
        smk_target_creator = Smk_target_creater(
            samples=list(df["sample"]),
            vambTypes=vamb_types,
            runtimes=runtimes,
            from_bamfiles=True,
        )
        snakemake_runner.add_to_config(f"contig_bamfiles=yes")
        snakemake_runner.add_to_config(f"input_data={path_contig_bamfiles}")
        snakemake_runner.to_print_while_running_snakemake = (
            f"Running snakemake with {threads} thread(s), from contigs and bamfiles"
        )

    if composition_and_rpkm is not None:
        smk_target_creator = Smk_target_creater(
            samples=list(df["sample"]),
            vambTypes=vamb_types,
            runtimes=runtimes,
            from_bamfiles=False,
        )
        snakemake_runner.add_to_config(f"composition_and_rpkm=yes")
        snakemake_runner.add_to_config(f"input_data={path_composition_and_rpkm}")
        snakemake_runner.to_print_while_running_snakemake = (
            f"Running snakemake with {threads} thread(s), from composition and rpkm"
        )

    if dryrun:
        snakemake_runner.add_arguments(["-np"])

    if refhash == None:
        logger.warn("Refhash not set, defaulting to lastest version of VAMB")
        refhash = ["latest"]


    for refhash in refhash:
        # Set output dir for snakemake 
        output_dir_refhash = Path(output) / refhash
        snakemake_runner.output_directory = output_dir_refhash

        # Set targets snakemake try to create
        targets = smk_target_creator.create_targets(output_dir=output_dir_refhash) 
        snakemake_runner.set_target_rule(targets)

        # Create vamb version w.r.t. to the refhash
        env_setupper = Environment_setupper(logger)
        env_setupper.clone_vamb_github(refhash=refhash, branch=branch)
        # .. and yaml file pointing to it
        vamb_conda_env_yamlfile = env_setupper.create_conda_env_yaml(
            refhash=refhash, branch=branch
        )
        # Let snakemake know where it is
        snakemake_runner.set_vamb_conda_env_yamlfile(vamb_conda_env_yamlfile)

        # Set the name of the snakemake run
        snakemake_runner.set_vamb_run_name(refhash, branch)

        # Run snakemake
        snakemake_runner.run()


        # TODO this section should be moved down such that it takes the arguments and then
        # writes to the file without appendig
        targets_dict = smk_target_creator.create_targets(
            output_dir=output_dir_refhash, as_dict=True
        )
        if run_binbencher:
            output_binbencher_results(
                targets_dict=targets_dict,
                df = df,
                output_file=Path(output) / "benchmark.tsv",
                logger=logger,
                refhash=refhash,
            )


if __name__ == "__main__":
    # Print --help if no arguments are passed in
    if len(sys.argv) == 1:
        main(["--help"])
    else:
        main()
