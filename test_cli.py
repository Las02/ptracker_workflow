from cli import Smk_target_creater, BinBencher


def test_snakemake_target():
    smk_target_creator = Smk_target_creater(
        samples=["sample1", "sample2"], vambTypes=["vamb_default"], runtimes=3
    )
    targets = smk_target_creator.create_targets()
    assert targets == [
        "sample_sample1_vamb_default_run_2_from_rpkm_comp",
        "sample_sample1_vamb_default_run_3_from_rpkm_comp",
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


def test_as_dict():
    # Create targets
    smk_target_creator = Smk_target_creater(
        samples=["sample1"], vambTypes=["vamb_default"], runtimes=2, from_bamfiles=False
    )
    targets = smk_target_creator.create_targets(as_dict=True)
    assert targets == {
        "sample1": [
            "sample_sample1_vamb_default_run_1_from_rpkm_comp",
            "sample_sample1_vamb_default_run_2_from_rpkm_comp",
        ]
    }


def test_bin_bench():
    # Create targets
    smk_target_creator = Smk_target_creater(
        samples=["sample1"], vambTypes=["vamb_default"], runtimes=2, from_bamfiles=False
    )
    targets = smk_target_creator.create_targets(as_dict=True)
    assert targets == {
        "sample1": [
            "sample_sample1_vamb_default_run_1_from_rpkm_comp",
            "sample_sample1_vamb_default_run_2_from_rpkm_comp",
        ]
    }
    # Binbench targets for sample1 (here all of them)
    binbencher = BinBencher(reference="reference", targets=targets["sample1"])
    binbencher.run_all_targets(dry_run_command=True)
    assert binbencher.has_been_run == [
        [
            "/home/las/ubuntu2/miniconda3/envs/ptracker_pipeline4/bin/julia",
            "./BinBencher",
            "sample_sample1_vamb_default_run_1_from_rpkm_comp",
            "reference",
        ],
        [
            "/home/las/ubuntu2/miniconda3/envs/ptracker_pipeline4/bin/julia",
            "./BinBencher",
            "sample_sample1_vamb_default_run_2_from_rpkm_comp",
            "reference",
        ],
    ]


def test_binbencher_output_individual():
    binbencher = BinBencher(reference="reference", targets=["target1"])
    binbencher.tool_to_run = "./test_stuff/test_binbench.jl"
    # above file contains ```println("2")```
    binbencher.run_all_targets(dry_run_command=False)
    assert binbencher.get_output() == 2


def test_binbencher_output_several():
    binbencher = BinBencher(reference="reference", targets=["target1", "target2"])
    binbencher.tool_to_run = "./test_stuff/test_binbench.jl"
    # above file contains ```println("2")```
    binbencher.run_all_targets(dry_run_command=False)
    assert binbencher.get_benchmarks() == {"target1": 2, "target2": 2}
