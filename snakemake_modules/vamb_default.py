
VAMB_TYPE = "vamb_default"

rulename = "vamb_default"
rule vamb_default:
    input:
        contig = contig,
        bamfiles = bamfiles
    output:
        composition = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/composition.npz"),
        rpkm = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/abundance.npz"),
        dir = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig"),
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb bin default --outdir {output.dir} --fasta {input.contig} \
        -p {threads} --bamfiles {input.bamfiles} -m 2000
        """

rulename = "vamb_default_rpkm_comp"
rule vamb_default_rpkm_comp:
    input:
        # TODO add propper output
        composition = composition if config.get("composition_and_rpkm") is not None else  OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/composition.npz"),
        rpkm = rpkm if config.get("composition_and_rpkm") is not None else OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/abundance.npz"),
    output:
        dir = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_rpkm_comp")
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb bin default --outdir {output.dir} --composition {input.composition} \
        -p {threads} --rpkm {input.rpkm} -m 2000
        """
