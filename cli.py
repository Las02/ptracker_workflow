import rich_click as click
import os
import snakemake
import subprocess
from pathlib import Path
import shutil

click.rich_click.USE_RICH_MARKUP = True


class Logger:
    def print(self, arg):
        click.echo(arg)

            

# Snakemake should handle genomad download
# Only downloading conda envs
#snakemake --use-conda --conda-create-envs-only -c4 --conda-frontend conda
# genomad database download?
        
#def validate_paths(self):

class Snakemake_runner():
    argument_holder = []
    def __init__(self):
        dir_of_current_file = os.path.dirname(os.path.realpath(__file__))
        self.snakemake_path = shutil.which("snakemake")  #Path("/home/las/ubuntu2/miniconda3/envs/ptracker_pipeline4/bin/snakemake")
        self.snakefile_path = Path(Path(dir_of_current_file) / "snakefile")
        self.add_argument("--snakefile", self.snakefile_path)
        self.add_argument("-c", "4")

    def add_argument(self, argument, command):
      self.argument_holder += [argument, command]

    def run_snakemake(self):
      print([self.snakemake_path] + self.argument_holder)
      #subprocess.run([self.snakemake_path, "--snakefile" ,self.snakefile, "-c", self.threads])
    
    def validate_paths(self):
      if not self.snakefile_path.exists():
        raise click.UsageError(f"Could not find snakefile, tried: {self.snakefile_path}")

      if self.snakemake_path is None:
        raise click.UsageError(f"Could not find snakemake, is it installed? \nsee https://snakemake.readthedocs.io/en/stable/getting_started/installation.html")

      

@click.command()
@click.option("--genomad_db", help="genomad database", type=click.Path(exists=True))
@click.option("--dryrun", help="run a dryrun", is_flag=True)
def main(dryrun,  download_genomad_db):
    
  # if genomad_db == None:
  # raise click.BadParameter("genomad_db", param_hint=["--genomad_db"])

    logger = Logger()
    logger.print("running snakemake")


    runner = Snakemake_runner()
    runner.validate_paths()
    runner.run_snakemake()


if __name__ == "__main__":

    main()

    #    status = snakemake.snakemake(snakefile, configfile=paramsfile,
    #                              targets=[target], printshellcmds=True,
    #                              dryrun=args.dry_run, config=config)
    #
    # if status: # translate "success" into shell exit code of 0
    #    return 0
    # return 1
