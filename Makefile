all: 
	pytest --ignore=bin -vv
contig_bamfiles_:
	# python3 cli.py
	./cli.py --output tmpdir --contig_bamfiles contig_bamfiles -n --vamb_default --avamb --runtimes 2
comp_rpkm_:
	./cli.py --output tmpdir --composition_and_rpkm  comp_rpkm -n --vamb_default --avamb --runtimes 2
binbench:
	./cli.py --output tmpdir --composition_and_rpkm  comp_rpkm_ref -n --vamb_default --avamb --runtimes 2 --run_binbencher
setup_env:
	python3 cli.py --setup_env
