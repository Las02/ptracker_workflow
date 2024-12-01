from math import log
from pathlib import Path

from vamb.taxonomy import (
    ContigTaxonomy,
    PredictedContigTaxonomy,
    Taxonomy,
    PredictedTaxonomy,
)

# The score is computed as the log of the probability assigned to the right species.
# At any clade, we assume there are e^2+1 children, and all the children not predicted
# have been given the same score.

# Examples:
# 1) Correct guess at species level. The predictor predicts the species with score 0.8:
#    Result: log(0.8)

# 2) Correct guess at genus level; wrong at species level with score 0.8:
# The remaining score of 0.8 is divided by the remaining e^2 children:
#    Result: log(0.2 / e^2) = log(0.2) - 2

# 3) Correct guess at family level; wrong at genus level with score 0.8:
# The remaining score of 0.2 is divided among e^2 children, each whom have e^2+1 children.
#    Result: log(0.2 / (e^2 * (e^2 + 1))) - we round this off to log(0.2 / (e^2 * e^2)) = log(0.2) - 4

# So: Result is: If correct, log of last score. If N levels are incorrect, it's log(1 - score at first level) - 2N

from typing import Iterable

def score(true: ContigTaxonomy, pred: PredictedContigTaxonomy) -> float:
    for (rank_level, (true_rank, pred_rank, prob)) in enumerate(zip(true.ranks, pred.contig_taxonomy.ranks, pred.probs)):
        if true_rank != pred_rank:
            wrong_ranks = 7 - rank_level
            return log(1 - prob) - 2 * wrong_ranks
    
    missing_ranks = 7 - len(pred.contig_taxonomy.ranks)
    if missing_ranks == 0:
        return log(pred.probs[-1])
    else:
        return 2.0 * missing_ranks

def validate_gtdb_structure(it: Iterable[list[str]]):
    target_ranks = [i + '__' for i in "dpcofgs"]
    for i in it:
        for (rank, target) in zip(i, target_ranks):
            if not rank.startswith(target):
                raise ValueError(f"GDTB Clade name does not begin with {target} as expected.")

def load_scores(truth_path: Path, pred_path: Path) -> list[tuple[int, float]]:
    truth = dict(Taxonomy.parse_tax_file(truth_path, True))
    for tax in truth.values():
        if len(tax.ranks) != 7:
            raise ValueError("Not all GTDB ground truth has 7 taxonomic ranks")
    validate_gtdb_structure(i.rank for i in truth.values())
    pred = PredictedTaxonomy.parse_tax_file(pred_path, True)
    validate_gtdb_structure(p.contig_taxonomies.rank for (_, _, p) in pred)
    return [
        (length, score(truth[name], contig_pred))
        for (name, length, contig_pred) in pred
    ]

def weighted_score(lst: list[tuple[int, float]]) -> float:
    return sum(i[0] * i[1] for i in lst) / sum(i[0] for i in lst)
