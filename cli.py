#!/usr/bin/env python3
try:
    import rich_click as click

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
except ModuleNotFoundError:
    try:
        import click
    except ModuleNotFoundError as e:
        print(
            """\nCould not find module click or module rich_click, please make sure to create an environment containing
either of modules eg. using conda or pip. See the user guide on the github README.\n"""
        )
        raise e

from logic import (
    Logger,

    Smk_target_creater,
    Snakemake_runner,
    Environment_setupper,
    output_binbencher_results,
)
from return_all import *
import sys
from pathlib import Path
from collections import defaultdict

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def validate_options(
    benchmark_taxometer,
    taxometer,
    output,
    contig_bamfiles,
    composition_and_rpkm,
    vamb_types,
    recluster,
):
    if benchmark_taxometer and not taxometer:
        raise click.BadParameter(
            "--benchmark_taxometer is defined but taxometer is not"
        )
    if output is None:
        raise click.BadParameter("--output is required")
    if contig_bamfiles is None and composition_and_rpkm is None:
        raise click.BadParameter(
            "Neither --contig_bamfiles nor --composition_and_rpkm are used, please define one of them"
        )
    if contig_bamfiles is not None and composition_and_rpkm is not None:
        raise click.BadParameter(
            "Both --contig_bamfiles and --composition_and_rpkm are used, only use one of them"
        )
    if not vamb_types and not recluster:
        raise click.BadParameter("No vamb types are defined")


def load_data(
    contig_bamfiles,
    composition_and_rpkm,
    run_binbencher,
    recluster,
    benchmark_taxometer,
    taxvamb,
    taxometer,
    taxvamb_and_taxometer,
):
    df = None
    if contig_bamfiles is not None:
        expected_headers = ["sample", "contig", "directory_of_bamfiles"]
        if run_binbencher:
            expected_headers.append("reference")
        if recluster:
            expected_headers.extend(["latent", "cluster", "markers"])
        if benchmark_taxometer:
            expected_headers.append("reference_taxometer")
        if taxvamb or taxometer or taxvamb_and_taxometer:
            expected_headers.append("taxonomy")
        _, df = wss_file_checker(
            Logger(),
            expected_headers=expected_headers,
            none_file_columns=["sample"],
        ).get_info(contig_bamfiles, param="contig_bamfiles")

    if composition_and_rpkm is not None:
        expected_headers = ["sample", "composition", "rpkm"]
        if run_binbencher:
            expected_headers.append("reference")
        if benchmark_taxometer:
            expected_headers.append("reference_taxometer")
        if taxvamb or taxometer or taxvamb_and_taxometer:
            expected_headers.append("taxonomy")
        if recluster:
            expected_headers.extend(["latent", "cluster", "markers"])
        _, df = wss_file_checker(
            Logger(),
            expected_headers=expected_headers,
            none_file_columns=["sample"],
        ).get_info(composition_and_rpkm, param="composition_and_rpkm")
    return df


def configure_snakemake(
    threads,
    snakemake_arguments,
    taxvamb,
    taxometer,
    taxvamb_and_taxometer,
    recluster,
    contig_bamfiles,
    composition_and_rpkm,
    df,
    vamb_types,
    runtimes,
    logger,
):
    snakemake_runner = Snakemake_runner(logger)
    snakemake_runner.add_arguments(["-c", str(threads)])

    if snakemake_arguments is not None:
        logger.print(f"Expanding snakemake arguments with: {snakemake_arguments}")
        snakemake_runner.add_arguments(snakemake_arguments)

    if taxvamb or taxometer or taxvamb_and_taxometer:
        snakemake_runner.add_to_config("taxonomy_information=yes")

    if recluster:
        snakemake_runner.add_to_config("latent_cluster_markers=yes")

    smk_target_creator = None
    if contig_bamfiles is not None:
        smk_target_creator = Smk_target_creater(
            samples=list(df["sample"]),
            vambTypes=vamb_types,
            runtimes=runtimes,
            from_bamfiles=True,
        )
        snakemake_runner.add_to_config("contig_bamfiles=yes")
        snakemake_runner.add_to_config(f"input_data={contig_bamfiles}")
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
        snakemake_runner.add_to_config("composition_and_rpkm=yes")
        snakemake_runner.add_to_config(f"input_data={composition_and_rpkm}")
        snakemake_runner.to_print_while_running_snakemake = (
            f"Running snakemake with {threads} thread(s), from composition and rpkm"
        )
    return snakemake_runner, smk_target_creator


def run_workflow(
    dryrun,
    refhash,
    output,
    recluster,
    runtimes,
    composition_and_rpkm,
    contig_bamfiles,
    df,
    branch,
    run_binbencher,
    benchmark_taxometer,
    logger,
    snakemake_runner,
    smk_target_creator,
):
    snakemake_runner.add_arguments(["--keep-incomplete"])
    snakemake_runner.add_arguments(["-p"])

    if dryrun:
        snakemake_runner.add_arguments(["-np"])

    if refhash is None:
        logger.warn("Refhash not set, defaulting to the latest version of VAMB")
        refhash = ["latest"]

    for refhash_item in refhash:
        output_dir_refhash = Path(output) / refhash_item
        snakemake_runner.output_directory = output_dir_refhash

        targets = smk_target_creator.create_targets(output_dir=output_dir_refhash)

        if recluster:
            add_to_targets = []
            for sample in list(df["sample"]):
                for number in range(1, runtimes + 1):
                    if composition_and_rpkm is not None:
                        add_to_targets.append(
                            output_dir_refhash
                            / f"sample_{sample}_run_{number}_from_comp_rpkm"
                        )
                    if contig_bamfiles is not None:
                        add_to_targets.append(
                            output_dir_refhash
                            / f"sample_{sample}_run_{number}_from_bam"
                        )
            targets.extend(add_to_targets)

        snakemake_runner.set_target_rule(targets)

        env_setupper = Environment_setupper(logger)
        env_setupper.clone_vamb_github(refhash=refhash_item, branch=branch)
        vamb_conda_env_yamlfile = env_setupper.create_conda_env_yaml(
            refhash=refhash_item, branch=branch
        )
        snakemake_runner.set_vamb_conda_env_yamlfile(vamb_conda_env_yamlfile)
        snakemake_runner.set_vamb_run_name(refhash_item, branch)
        snakemake_runner.run()

        targets_dict = smk_target_creator.create_targets(
            output_dir=output_dir_refhash, as_dict=True
        )
        if run_binbencher:
            output_binbencher_results(
                targets_dict=targets_dict,
                df=df,
                output_file=Path(output) / "benchmark.tsv",
                logger=logger,
                refhash=refhash_item,
            )

        if benchmark_taxometer:
            logger.print("Starting benchmarking of taxometer")
            taxometer_benchmark_creator = Smk_target_creater(
                samples=list(df["sample"]),
                vambTypes=["taxometer"],
                runtimes=runtimes,
                from_bamfiles=True,
            )
            targets_dict = taxometer_benchmark_creator.create_targets(
                output_dir=output_dir_refhash, as_dict=True
            )
            import taxbench

            logger.print("Benchmarking", targets_dict)
            sample_truth = {
                sample: truth
                for sample, truth in zip(df["samples"], df["reference_taxometer"])
            }
            output_dict = defaultdict()
            for sample in targets_dict.keys():
                scores = taxbench.load_scores(
                    sample_truth[sample], targets_dict[sample]
                )
                output_dict[sample] = taxbench.weighted_score(scores)
            print(output_dict)


@click.command(context_settings=CONTEXT_SETTINGS)
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
@click.option("-b", "--branch", default="master", show_default=True)
@click.option("-r", "--runtimes", type=int, default=1, show_default=True)
@click.option("-d", "--vamb_default", is_flag=True)
@click.option("-d", "--avamb", is_flag=True)
@click.option("-b", "--run_binbencher", is_flag=True)
@click.option("-b", "--taxvamb", is_flag=True)
@click.option("-r", "--recluster", is_flag=True)
@click.option("-o", "--taxvamb_and_taxometer", is_flag=True)
@click.option("-tx", "--taxometer", is_flag=True)
@click.option("-btx", "--benchmark_taxometer", is_flag=True)
@click.option("-s", "--snakemake_arguments", type=One_or_more_snakemake_arguments())
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
    recluster: bool,
    benchmark_taxometer: bool,
    taxvamb_and_taxometer: bool,
    snakemake_arguments: str,
):
    """
    \bThis is a program to run the Ptracker Snakemake pipeline to bin plasmids from metagenomic reads.
    The first time running the program it will try to install the genomad database (~3.1 G) and required scripts.
    For running the pipeline either the --reads or the --reads_and_assembly_dir arguments are required.
    Additionally, the --output argument is required which defines the output directory.
    For Quick Start please see the README: https://github.com/Las02/ptracker_workflow/tree/try_cli
    """
    vamb_types = []
    if vamb_default:
        vamb_types.append("vamb_default")
    if avamb:
        vamb_types.append("avamb")
    if taxvamb:
        vamb_types.append("taxvamb")
    if taxometer:
        vamb_types.append("taxometer")

    validate_options(
        benchmark_taxometer,
        taxometer,
        output,
        contig_bamfiles,
        composition_and_rpkm,
        vamb_types,
        recluster,
    )

    logger = Logger()

    df = load_data(
        contig_bamfiles,
        composition_and_rpkm,
        run_binbencher,
        recluster,
        benchmark_taxometer,
        taxvamb,
        taxometer,
        taxvamb_and_taxometer,
    )

    snakemake_runner, smk_target_creator = configure_snakemake(
        threads,
        snakemake_arguments,
        taxvamb,
        taxometer,
        taxvamb_and_taxometer,
        recluster,
        contig_bamfiles,
        composition_and_rpkm,
        df,
        vamb_types,
        runtimes,
        logger,
    )

    run_workflow(
        dryrun,
        refhash,
        output,
        recluster,
        runtimes,
        composition_and_rpkm,
        contig_bamfiles,
        df,
        branch,
        run_binbencher,
        benchmark_taxometer,
        logger,
        snakemake_runner,
        smk_target_creator,
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main.main(["--help"])
    else:
        main()
