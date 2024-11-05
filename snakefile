
print(config)
rule all:
  input: "test/a"

rule create_a:
  input: "b" if config.get("b") == None else config.get("b")
  output: "test/a"
  conda: "coolenv.yaml"
  shell:
    """
    touch {output}
    """
