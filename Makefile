all: 
	pytest --ignore=bin -vv
contig_bamfiles_:
	# python3 cli.py
	# ./cli.py --output tmpdir --contig_bamfiles contig_bamfiles --taxvamb -n --vamb_default --avamb --runtimes 2
	./cli.py --output tmpdir --contig_bamfiles contig_bamfiles  -n --vamb_default  --runtimes 4
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
