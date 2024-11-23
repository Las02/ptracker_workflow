
rulename = "vamb_default"
rule vamb_default:
    input:
        contig = contig,
        bamfiles = bamfiles
    output:
        dir = "sample_{sample}/vamb_default"
    threads: threads_fn(rulename)
    resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
    conda: THIS_FILE_DIR / "envs" / config["vamb_conda_env_yamlfile"]
    shell:
        """
        rm -rf {output.dir}
        vamb bin default --outdir {output.dir} --fasta {input.contig} \
        -p {threads} --bamfiles {input.bamfiles} -m 2000
        """
