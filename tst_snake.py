
rule all:
    output: 'hello'
    conda: "envs/pipeline_conda.yaml"
    shell: "echo a > {output}"
