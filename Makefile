all: 
	pytest --ignore=bin -vv
contig_bamfiles_:
	# python3 cli.py
	# ./cli.py --output tmpdir --contig_bamfiles contig_bamfiles --taxvamb -n --vamb_default --avamb --runtimes 2
	./cli.py --output tmpdir --contig_bamfiles contig_bamfiles  -n --vamb_default  --runtimes 4 --snakemake_arguments 'hello fam'
comp_rpkm_:
	./cli.py --output tmpdir --composition_and_rpkm  comp_rpkm -n --vamb_default --avamb --runtimes 2
binbench:
	./cli.py --output tmpdir --composition_and_rpkm  comp_rpkm_ref -n --vamb_default --taxvamb --avamb --runtimes 2 --run_binbencher --refhash latest d35788c910
taxvamb:
	./cli.py --output tmpdir --composition_and_rpkm  comp_rpkm_ref_taxvamb -n  --taxvamb --runtimes 2 --run_binbencher --refhash latest d35788c910
taxometer_taxvamb:
	./cli.py --output tmpdir --composition_and_rpkm  comp_rpkm_ref_taxvamb -n --run_bi  --taxvamb_and_taxometer --runtimes 1  --refhash latest 
setup_env:
	python3 cli.py --setup_env
test_contig_bamfiles_:
	# python3 cli.py
	# ./cli.py --output tmpdir --contig_bamfiles contig_bamfiles --taxvamb -n --vamb_default --avamb --runtimes 2
	# ./cli.py --output tmpdir --contig_bamfiles test_stuff/contig_bamfiles.tsv -t 8 --vamb_default  --runtimes 2
	# ./cli.py --output tmpdir --contig_bamfiles test_stuff/contig_bamfiles.tsv -t 8 --avamb  --runtimes 2
	# ./cli.py --output tmpdir --contig_bamfiles test_stuff/contig_bamfiles_tax.tsv -t 8 --taxometer  --runtimes 1
	./cli.py --output tmpdir --contig_bamfiles test_stuff/contig_bamfiles_tax.tsv -t 8 --taxvamb  --runtimes 1
test_taxometer_only:
	./cli.py --output Airways --contig_bamfiles test_stuff/contig_bamfiles_tax.tsv -t 8  --taxometer --runtimes 3 --refhash latest d35788c910 
test_contig_bamfiles_taxometer:
	./cli.py --output Airways --contig_bamfiles test_stuff/contig_bamfiles_tax.tsv -n -t 8 --taxvamb --vamb_default --avamb  --runtimes 2  --refhash latest d35788c910 
test_recluster:
	./cli.py --output tmpdir --contig_bamfiles test_stuff/recluster.tsv -t 8   --recluster --runtimes 3 --refhash latest 
test_taxometer_bench:
	./cli.py --output Airways --benchmark_taxometer --contig_bamfiles test_stuff/contig_bamfiles_tax.tsv -t 8  --taxometer --runtimes 2 -n --refhash latest 

run_all_no_benchmark_lastest:
	./cli.py --output run_all --contig_bamfiles test_stuff/run_all_latest.tsv -n -t 8 \
		--taxvamb --vamb_default --avamb --taxometer --runtimes 3  --refhash latest 
run_all_no_benchmark_refhash:
	./cli.py --output run_all --contig_bamfiles test_stuff/run_all_mmseq_needed.tsv -n -t 8 \
		--taxvamb --vamb_default --avamb --taxometer --runtimes 3  --refhash d35788c910  
