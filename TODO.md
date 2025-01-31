
<!-- - Add error checking for whether a correct spades dir is passed in -->
<!-- - Deafult to conda if mamba is not installed -->

- Clean up the snakemake pipeline
- Fix env setup - such that it works within vamb.. how should it be setup 

- Make sure log files and benchmark files are create correctly, prefearbly with class/fn -> also format them and outputfiles nicely

- What about the module loads at the top of snakefile.py:10 - running pipeline without it does different versions of packages work better?


- running not default shells gives wierd conda --json thingy with snakemake

- Freeze version of packages? 


- Genomad download option to give path

- Snakemake running it from CMD. - clustersubmission like Avamb workflow

- should  mamba install zstd be part of the module.. 

- lock versions


## Last checks
- Update README with preprint and cli.py paths to README
- when all is done test that everything works
  * Running from Assembly with CLI
  * Running with Assembly with CLI
  * Running without Assembly 
- grep for TODO not yet finished
