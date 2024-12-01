Config file /maps/projects/rasmussen/scratch/ptracker/Benchmark_vamb_cli/config/config.yaml is extended by additional config specified via the command line.
The flag 'directory' used in rule vamb_default is only valid for outputs, not inputs.
Building DAG of jobs...
Your conda installation is not configured to use strict channel priorities. This is however crucial for having robust and correct environments (for details, see https://conda-forge.org/docs/user/tipsandtricks.html). Please consider to configure strict priorities by executing 'conda config --set channel_priority strict'.
Using shell: /usr/bin/bash
Provided cores: 8
Rules claiming more threads will be scaled down.
Provided resources: mem_mb=3255, mem_mib=3105, disk_mb=3255, disk_mib=3105, mem_gb=50
Select jobs to execute...

[Mon Dec  2 00:00:32 2024]
rule taxvamb:
    input: data/vambnew/Airways/contigs_2kbp.fna, data/vambnew/Airways/bam, data/vambnew/Airways/fmt_mmseqs_pred.tsv
    output: run_all/latest/sample_Airways_taxvamb_run_1_from_bam_contig/composition.npz, run_all/latest/sample_Airways_taxvamb_run_1_from_bam_contig/abundance.npz, run_all/latest/sample_Airways_taxvamb_run_1_from_bam_contig
    jobid: 0
    reason: Forced execution
    wildcards: sample=Airways
    threads: 8
    resources: mem_mb=3255, mem_mib=3105, disk_mb=3255, disk_mib=3105, tmpdir=/scratch, walltime=48:00:00, mem_gb=50


        rm -rf run_all/latest/sample_Airways_taxvamb_run_1_from_bam_contig
        vamb bin taxvamb --taxonomy data/vambnew/Airways/fmt_mmseqs_pred.tsv --outdir run_all/latest/sample_Airways_taxvamb_run_1_from_bam_contig --fasta data/vambnew/Airways/contigs_2kbp.fna         -p 8 --bamdir data/vambnew/Airways/bam  -m 2000
        
Activating conda environment: .snakemake/conda/de64111bbbaa1c5022a8f21f5b9e9c08_
2024-12-02 00:00:45.016 | INFO    | Starting Vamb version 4.1.4.dev141+g21bdcdd
2024-12-02 00:00:45.017 | INFO    | Random seed is 31587856555973163
2024-12-02 00:00:45.017 | INFO    | Invoked with CLI args: '/maps/projects/rasmussen/scratch/ptracker/Benchmark_vamb_cli/.snakemake/conda/de64111bbbaa1c5022a8f21f5b9e9c08_/bin/vamb bin taxvamb --taxonomy data/vambnew/Airways/fmt_mmseqs_pred.tsv --outdir run_all/latest/sample_Airways_taxvamb_run_1_from_bam_contig --fasta data/vambnew/Airways/contigs_2kbp.fna -p 8 --bamdir data/vambnew/Airways/bam -m 2000'
2024-12-02 00:00:45.017 | INFO    | Loading TNF
2024-12-02 00:00:45.017 | INFO    | 	Minimum sequence length: 2000
2024-12-02 00:00:45.017 | INFO    | 	Loading data from FASTA file data/vambnew/Airways/contigs_2kbp.fna
