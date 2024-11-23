from cli import Smk_target_creater


def test_snakemake_target():
    smk_target_creator = Smk_target_creater(
        samples=["sample1", "sample2"], vambTypes=["vamb_default"], runtimes=3
    )
    targets = smk_target_creator.create_targets()
    assert targets == [
        "sample_sample1_vamb_default_run_1_from_bam_contig",
        "sample_sample1_vamb_default_run_2_from_rpkm_comp",
        "sample_sample1_vamb_default_run_3_from_rpkm_comp",
        "sample_sample2_vamb_default_run_1_from_bam_contig",
        "sample_sample2_vamb_default_run_2_from_rpkm_comp",
        "sample_sample2_vamb_default_run_3_from_rpkm_comp",
    ]


def test_snakemake_target_from_rpkm():
    smk_target_creator = Smk_target_creater(
        samples=["sample1"], vambTypes=["vamb_default"], runtimes=2, from_bamfiles=False
    )
    targets = smk_target_creator.create_targets()
    assert targets == [
        "sample_sample1_vamb_default_run_1_from_rpkm_comp",
        "sample_sample1_vamb_default_run_2_from_rpkm_comp",
    ]


def test_snakemake_target_from_rpkm_dir():
    smk_target_creator = Smk_target_creater(
        samples=["sample1"], vambTypes=["vamb_default"], runtimes=2, from_bamfiles=False
    )
    from pathlib import Path

    targets = smk_target_creator.create_targets(output_dir=Path("output_dir"))
    assert targets == [
        Path("output_dir") / "sample_sample1_vamb_default_run_1_from_rpkm_comp",
        Path("output_dir") / "sample_sample1_vamb_default_run_2_from_rpkm_comp",
    ]
