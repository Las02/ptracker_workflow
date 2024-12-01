VAMB_TYPE = "taxometer"


rulename = "taxometer_default"
rule taxometer_default:
    input:
        contig = contig,
        bamfiles = bamfiles,
        taxonomy = taxonomy
    output:
        # TODO set as correct
        # taxonomy_taxometer = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig") / ,
        dir = directory(OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig")),
        composition = composition if config.get("composition_and_rpkm") is not None else  OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig/composition.npz"),
        rpkm = rpkm if config.get("composition_and_rpkm") is not None else OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig/abundance.npz"),
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb taxometer --taxonomy {input.taxonomy} --outdir {output.dir} --fasta {input.contig} \
        -p {threads} --bamdir {input.bamfiles} -m 2000
        """


# # TODO implement this: 
rulename = "taxometer_rpkm_comp"
rule taxometer_rpkm_comp:
    input:
        # TODO add propper output
        composition = composition if config.get("composition_and_rpkm") is not None else  OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig/composition.npz"),
        rpkm = rpkm if config.get("composition_and_rpkm") is not None else OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig/abundance.npz"),
        taxonomy = taxonomy 
    output:
        dir = directory(OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_rpkm_comp"))
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb taxometer --taxonomy {input.taxonomy} --outdir {output.dir} --composition {input.composition} \
        -p {threads} --abundance {input.rpkm} -m 2000
        """

# # TODO implement this: 
# rulename = "taxometer_rpkm_comp"
# rule taxometer_rpkm_comp:
#     input:
#         # TODO add propper output
#         composition = composition if config.get("composition_and_rpkm") is not None else  OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig/composition.npz"),
#         rpkm = rpkm if config.get("composition_and_rpkm") is not None else OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_1_from_bam_contig/abundance.npz"),
#     output:
#         dir = OUTDIR / ("sample_{sample}_" + VAMB_TYPE + "_run_{run_number}_from_rpkm_comp")
#     threads: threads_fn(rulename)
#     resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
#     conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
#     shell:
#         """
#         rm -rf {output.dir}
#         vamb bin default --outdir {output.dir} --composition {input.composition} \
#         -p {threads} --rpkm {input.rpkm} -m 2000
#         """
