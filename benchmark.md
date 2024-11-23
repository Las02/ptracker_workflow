
Normal vamb, Avamb, 

Taxvamb med taxonomy som kan bruges med gtbd_truth (nok for godt, ikke brug kun til bench, bare output vamb taxometer) eller brug vamb taxometer 

vamb taxometer, uncomplete taxonomy -> more complete 
- input mmseqs_pred.tsv
- also benchmark

Dens output til Taxvamb efter det er vertificeret.

---

vamb recluster
kmeans -> til Cami data (SR)
test:
  clusters_merged_unsplit.tsv


---
and 
later: LR with DB Scan algo
Filter eg. 10KB 


----
Gamle version: 
Ny version: Nyeste

et par runs for each method. eg. 3
Kun run en specifik vamb eller 2 

Give den tidl. composition, abundance objects

Should only run first part of vamb once

---
Assemblies + Organisms .




## TODO

# Goal This weekend: 

- Add benchmarking part to vamb - Or use a make a simple seperate CLI tool for this? - What's the best solution?
- Add way to run for several refhashed? 

<!-- 1) Run Avamb just like the normal version of Vamb  -->

2) Run Vamb taxometer and TaxVamb

  Run Vamb taxometer to make uncomplete taxonomy -> more complete 
  - Input mmseqs_pred.tsv
  - Benchmark the taxonomy against gtbd_truth 

  Use the output of taxometer as input in Taxvamb


----

--- This needs reclarification. 
3) Run Recluster
Run vamb recluster
Den har to methods Kmeans for SR and DB scan for LR
AKA kmeans skal bruges til Cami data since it's SR

test:
  clusters_merged_unsplit.tsv

# What ? 
later: LR with DB Scan algo
Filter eg. 10KB 

---





