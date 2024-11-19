# Loading the correct configfile
THIS_FILE_DIR = config.get("dir_of_current_file")
THIS_FILE_DIR = Path("") if THIS_FILE_DIR is None else Path(THIS_FILE_DIR)
configfile: THIS_FILE_DIR / "config/config.yaml"

import os
from pathlib import Path

## Paths
# Dir defined by user
output_directory = config.get("output_directory")
# Set as empty path if not defined meaning will not have effect
output_directory = Path("") if output_directory is None else Path(output_directory)
OUTDIR = (
    output_directory / "outdir_plamb"
)  # config["outdir"] #get_config('outdir', 'outdir_plamb', r'.*') # TODO fix
PAU_SRC_DIR = THIS_FILE_DIR / "bin/ptracker/src/workflow"

# Define deault threads/walltime/mem_gb
default_walltime = config.get("default_walltime")
default_threads = config.get("default_threads")
default_mem_gb = config.get("default_mem_gb")

# Functions to get the config-defined threads/walltime/mem_gb for a rule and if not defined the default
threads_fn = lambda rulename: config.get(rulename, {"threads": default_threads}).get(
    "threads", default_threads
)
walltime_fn = lambda rulename: config.get(rulename, {"walltime": default_walltime}).get(
    "walltime", default_walltime
)
mem_gb_fn = lambda rulename: config.get(rulename, {"mem_gb": default_mem_gb}).get(
    "mem_gb", default_mem_gb
)

# # Read in the sample data
# df = pd.read_csv(config["files"], sep="\s+", comment="#")
# sample_id = collections.defaultdict(list)
# sample_id_path = collections.defaultdict(dict)
# for sample, id, read1, read2 in zip(df.SAMPLE, df.ID, df.READ1, df.READ2):
#     id = str(id)
#     sample = str(sample)
#     sample_id[sample].append(id)
#     sample_id_path[sample][id] = [read1, read2]
# Read in the sample data

# Default values for these params
contigs = OUTDIR / "data/sample_{key}/spades_{id}/contigs.fasta"
contigs_paths = OUTDIR / "data/sample_{key}/spades_{id}/contigs.paths"
assembly_graph = (
    OUTDIR / "data/sample_{key}/spades_{id}/assembly_graph_after_simplification.gfa"
)

# sample_id = {}
# sample_id_path = {}

# if config.get("read_file") != None:
#     df = pd.read_csv(config["read_file"], sep="\s+", comment="#")
#     sample_id = collections.defaultdict(list)
#     sample_id_path = collections.defaultdict(dict)
#     for id, (read1, read2) in enumerate(zip(df.read1, df.read2)):
#         id = f"sample{str(id)}"
#         sample = "Plamb_Ptracker"
#         sample_id[sample].append(id)
#         sample_id_path[sample][id] = [read1, read2]

# if config.get("read_assembly_file") != None:
#     df = pd.read_csv(config["read_assembly_file"], sep="\s+", comment="#")
#     print(df)
#     sample_id = collections.defaultdict(list)
#     sample_id_path = collections.defaultdict(dict)
#     sample_id_path_assembly = collections.defaultdict(dict)
#     sample_id_path_contig = collections.defaultdict(dict)
#     sample_id_path_contigpaths = collections.defaultdict(dict)
#     for id, read1, read2, assembly, contig, contig_path in zip(df["sample"], df.read1, df.read2, df.assembly_graph, df.contig, df.contig_paths):
#         id = str(id)
#         sample = "Plamb_Ptracker"
#         sample_id[sample].append(id)
#         sample_id_path[sample][id] = [read1, read2]
#         sample_id_path_assembly[sample][id] = [assembly]
#         sample_id_path_contig[sample][id] = [contig]
#         sample_id_path_contigpaths [sample][id] = [contig_path]
#
#     # Redefin definede paths to files
#     contigs =  lambda wildcards: sample_id_path_contig[wildcards.key][wildcards.id][0]
#     contigs_paths =  lambda wildcards: sample_id_path_contigpaths[wildcards.key][wildcards.id][0]
#     assembly_graph =  lambda wildcards: sample_id_path_assembly[wildcards.key][wildcards.id][0]


# if config.get("read_assembly_dir") != None:
#     df = pd.read_csv(config["read_assembly_dir"], sep="\s+", comment="#")
#     sample_id = collections.defaultdict(list)
#     sample_id_path = collections.defaultdict(dict)
#     sample_id_path_assembly = collections.defaultdict(dict)
#     for id, (read1, read2, assembly) in enumerate(zip( df.read1, df.read2, df.assembly_dir)):
#         id = f"sample{str(id)}"
#         sample = "Plamb_Ptracker"
#         sample_id[sample].append(id)
#         sample_id_path[sample][id] = [read1, read2]
#         sample_id_path_assembly[sample][id] = [assembly]
#     # Redefin definede paths to files
#     contigs =  lambda wildcards: Path(sample_id_path_assembly[wildcards.key][wildcards.id][0]) / "contigs.fasta"
#     contigs_paths =  lambda wildcards: Path(sample_id_path_assembly[wildcards.key][wildcards.id][0]) / "assembly_graph_after_simplification.gfa"
#     assembly_graph =  lambda wildcards: Path(sample_id_path_assembly[wildcards.key][wildcards.id][0]) / "contigs.paths"


# rule all:
#     input:
#         expand(os.path.join(OUTDIR, "{key}", 'log/run_vamb_asymmetric.finished'), key=sample_id.keys()),
#         expand(os.path.join(OUTDIR,"{key}",'vamb_asymmetric','vae_clusters_graph_thr_0.75_candidate_plasmids.tsv'),key=sample_id.keys()),
#         # expand(os.path.join(OUTDIR,"{key}",'vamb_asymmetric','vae_clusters_graph_thr_0.75_candidate_plasmids.tsv'),key=sample_id.keys()),
#         expand(os.path.join(OUTDIR,"{key}",'log/run_geNomad.finished'), key=sample_id.keys()),
#         # "tst"
#         # expand("data/sample_{key}/vamb_default", key=sample_id.keys()),
#         # expand("data/sample_{key}/vamb_default", key=sample_id.keys()),
#         # expand_dir("data/sample_[key]/scapp_[value]/delete_me", sample_id)
#         #expand_dir("data/sample_[key]/mp_spades_[value]/contigs.fasta", sample_id),


# is GPU used ? #
CUDA = config.get("cuda", False)

# ## 5. Run vamb to merge the hoods
# rulename = "run_vamb_asymmetric"
# rule run_vamb_asymmetric:
#     input:
#         notused = os.path.join(OUTDIR,"{key}",'log','neighs','extract_neighs_from_n2v_embeddings.finished'), # TODO why is this not used?
#         contigs = OUTDIR /  "data/sample_{key}/contigs.flt.fna.gz",
#         # bamfiles = expand_dir("data/sample_[key]/mapped/[value].bam.sort", sample_id),
#         bamfiles = lambda wildcards: expand(OUTDIR / "data/sample_{key}/mapped_sorted/{id}.bam.sort", key=wildcards.key, id=sample_id[wildcards.key]),
#         nb_file = os.path.join(OUTDIR,'{key}','tmp','neighs','neighs_intraonly_rm_object_r_%s.npz'%NEIGHS_R)
#         # nb_file = os.path.join(OUTDIR,"{key}",'tmp','neighs','neighs_object_r_%s.npz'%NEIGHS_R)#,
#     output:
#         directory = directory(os.path.join(OUTDIR,"{key}", 'vamb_asymmetric')),
#         bins = os.path.join(OUTDIR,"{key}",'vamb_asymmetric','vae_clusters_unsplit.tsv'),
#         finished = os.path.join(OUTDIR,"{key}",'log/run_vamb_asymmetric.finished'),
#         lengths = os.path.join(OUTDIR,"{key}",'vamb_asymmetric','lengths.npz'),
#         vae_clusters = os.path.join(OUTDIR, '{key}','vamb_asymmetric/vae_clusters_community_based_complete_unsplit.tsv'),
#         compo = os.path.join(OUTDIR, '{key}','vamb_asymmetric/composition.npz'),
#     params:
#         walltime='86400',
#         cuda='--cuda' if CUDA else ''
#     threads: threads_fn(rulename)
#     resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
#     benchmark: config.get("benchmark", "benchmark/") + "{key}_" + rulename
#     log: config.get("log", "log/") + "{key}_" + rulename
#     conda: THIS_FILE_DIR / "envs/pipeline_conda.yaml"
#     shell:
#         """
#         rmdir {output.directory}
#         {PLAMB_PRELOAD}
#         vamb bin vae_asy --outdir {output.directory} --fasta {input.contigs} -p {threads} --bamfiles {input.bamfiles}\
#         --seed 1 --neighs {input.nb_file}  -m {MIN_CONTIG_LEN} {PLAMB_PARAMS}\
#          {params.cuda}
#         touch {output}
#         """


# rulename = "VAMB_DEFAULT"
# rule VAMB_DEFAULT:
#     input:
#         contig = "data/sample_{key}/contigs.flt.fna.gz",
#         bamfiles = lambda wildcards: expand("data/sample_{key}/mapped_sorted/{id}.bam.sort", key=wildcards.key, id=sample_id[wildcards.key]),
#     output:
#         dir = directory("data/sample_{key}/vamb_default"),
#     threads: threads_fn(rulename)
#     resources: walltime = walltime_fn(rulename), mem_gb = mem_gb_fn(rulename)
#     benchmark: config.get("benchmark", "benchmark/") + "{key}_" + rulename
#     log: config.get("log", "log/") + "{key}_" + rulename
#     shell:
#         """
#         rm -rf {output.dir}
#         vamb bin default --outdir {output.dir} --fasta {input.contig} \
#         -p {threads} --bamfiles {input.bamfiles} -m 2000
#         """
