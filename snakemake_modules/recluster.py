
VAMB_TYPE = "recluster"


rulename = "recluster"
rule recluster:
    input:
        contig = contig,
        bamfiles = bamfiles,
        cluster = cluster,
        latent = latent,
        markers = markers,
    output:
        dir = directory(OUTDIR / ("sample_{sample}_run_{run_number}_from_bam")),
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb recluster --outdir {output.dir} --fasta {input.contig} \
        --markers {input.markers} --algorithm kmeans \
        -p {threads} --bamdir {input.bamfiles} --latent_path {input.latent} --clusters_path {input.cluster} 
        """

rulename = "recluster_rpkm"
rule recluster_rpkm:
    input:
        composition = composition if config.get("composition_and_rpkm") is not None else "" ,
        rpkm = rpkm if config.get("composition_and_rpkm") is not None else "",
        cluster = cluster,
        latent = latent,
        markers = markers,
    output:
        dir = directory(OUTDIR / ("sample_{sample}_run_{run_number}_from_comp_rpkm")),
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb recluster --outdir {output.dir} --composition {input.composition} \
        -p {threads} --abundance {input.rpkm} --latent_path {input.latent} --clusters_path {input.cluster} \
        --markers {input.markers} --algorithm kmeans 
        """



