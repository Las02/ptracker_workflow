all: 
	pytest --ignore=bin -vv
all2:
	# python3 cli.py
	./cli.py --output tmpdir --contig_bamfiles contig_bamfiles -n --vamb_default --runtimes 2
comp:
	./cli.py --output tmpdir --composition_and_rpkm  comp_rpkm -n --vamb_default --runtimes 2
setup_env:
	python3 cli.py --setup_env
