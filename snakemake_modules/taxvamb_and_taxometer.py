
VAMB_TYPE = "taxvamb_and_taxometer"


rulename = "taxometer_for_taxvamb"
rule taxometer_for_taxvamb:
    input:
        #contig = contig,
        #bamfiles = bamfiles,
        taxonomy = taxonomy
    output:
        # TODO set as correct
        taxonomy_taxometer = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/taxonomy.tax"), 
        dir = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig"),

    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb taxometer --taxonomy {input.taxonomy} --outdir {output.dir} --fasta {input.contig} \
        -p {threads} --bamfiles {input.bamfiles} -m 2000
        """

rulename = "taxvamb_and_taxometer"
rule taxvamb_and_taxometer:
    input:
        contig = contig,
        bamfiles = bamfiles,
        # TODO set as correct
        taxonomy_taxometer = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/taxonomy.tax"), 
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
        vamb bin taxvamb --taxonomy {input.taxonomy} --outdir {output.dir} --fasta {input.contig} \
        -p {threads} --bamfiles {input.bamfiles} -m 2000
        """

rulename = "taxvamb_rpkm_comp"
rule taxvamb_and_taxometer_rpkm_comp:
    input:
        # TODO add propper output
        composition = composition if config.get("composition_and_rpkm") is not None else  OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/composition.npz"),
        rpkm = rpkm if config.get("composition_and_rpkm") is not None else OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/abundance.npz"),
        # TODO set as correct
        taxonomy_taxometer = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_bam_contig/taxonomy.tax"), 
    output:
        dir = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_rpkm_comp")
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb bin taxvamb --taxonomy {input.taxonomy} --outdir {output.dir} --composition {input.composition} \
        -p {threads} --rpkm {input.rpkm} -m 2000
        """
