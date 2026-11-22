"""Module 8 project: predict a protein's function class from its sequence.

Run from the top folder of your copy:   python scripts/protein_function.py
You can also work in a Colab notebook first (the lesson does), but keep this
script as the final, rerunnable version. Every result goes into results/.

Install once:   pip install pandas numpy scikit-learn torch transformers
The ESM-2 model (about 30 MB) downloads on first use. The whole script runs in
a few minutes on an ordinary CPU; no GPU is needed.
Fix every seed: random_state=0 throughout.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

# The three UniProt downloads (snapshot of release 2026_04; data/get-data.sh shows
# the exact URLs and downloads them again). One file per function class:
FILES = {"kinase": ("KW-0418", "uniprot_kinase_KW-0418.tsv"),
         "protease": ("KW-0645", "uniprot_protease_KW-0645.tsv"),
         "ion_channel": ("KW-0407", "uniprot_ion_channel_KW-0407.tsv")}

# Research question (write it in your own words):
# TODO

# ---------------------------------------------------------------------------
# Task 1 · Build the dataset and explore lengths (Module 7, lesson 1; lesson 3)
# ---------------------------------------------------------------------------
# TODO: read the three files with pd.read_csv(..., sep="\t") and add a label column.
# TODO: drop any protein carrying more than one of the three keywords
#       (the "Keyword ID" column), then sample 120 per class:
#       df.groupby("label").sample(120, random_state=0)
# TODO: family groups from the "Protein families" column ("superfamily, family,
#       subfamily"): family = the first two parts, top_group = the first part.
#       Use "none" for a protein with no family.
# TODO: save results/dataset.tsv with the columns
#       accession, gene, label, length, family, top_group
# TODO: save results/dataset_summary.tsv, one row per label, with the columns
#       label, proteins, mean_length, families

# ---------------------------------------------------------------------------
# Task 2 · Composition and k-mer features (lesson 2; lesson 3)
# ---------------------------------------------------------------------------
# TODO: amino-acid composition (20 numbers) and composition + dipeptides (420 numbers).
# TODO: score length alone, composition, and composition + dipeptides with
#       make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000))
#       and StratifiedKFold(5, shuffle=True, random_state=0).

# ---------------------------------------------------------------------------
# Task 3 · ESM-2 embeddings (lesson 7)
# ---------------------------------------------------------------------------
# TODO: embed every sequence with facebook/esm2_t6_8M_UR50D (load once, .eval(),
#       torch.no_grad()); drop the first and last token, average over residues.
# TODO: score the 360 x 320 matrix with the same model and the same folds.

# ---------------------------------------------------------------------------
# Task 4 · Compare, with a leakage check (lesson 10)
# ---------------------------------------------------------------------------
# TODO: in the random split, the share of test proteins whose family is also in
#       the training part (np.isin), averaged over the 5 folds.
# TODO: rescore composition + dipeptides and ESM-2 with GroupKFold(5), grouped by
#       family, and again grouped by top_group.

# ---------------------------------------------------------------------------
# Save the numbers from tasks 2 to 4 in results/metrics.tsv
# ---------------------------------------------------------------------------
# Two columns, metric and value (accuracies as fractions, 3 decimals), one row each:
#   length_random, composition_random, kmer_random, esm2_rows, esm2_dims, esm2_random,
#   random_split_family_overlap, kmer_family, kmer_toplevel, esm2_family, esm2_toplevel
# ("kmer" means composition + dipeptides; "random" the stratified random split;
#  "family" and "toplevel" the two GroupKFold splits.)

# ---------------------------------------------------------------------------
# Task 5 · Look at the errors (lesson 3; lesson 10)
# ---------------------------------------------------------------------------
# TODO: out-of-fold predictions for ESM-2 under the family split (cross_val_predict
#       with the same GroupKFold and groups); confusion matrix with pd.crosstab.
# TODO: save results/errors.tsv, one row per misclassified protein, with the columns
#       accession, gene, family, true, predicted

# ---------------------------------------------------------------------------
# Task 6 · Write a short honest report (lesson 10)
# ---------------------------------------------------------------------------
# Write results/report.md by hand, with the headings Question, Answer, Methods,
# Results, Errors and Limits, in that order. Give the UniProt URLs and the date.
