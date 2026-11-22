<a href="https://lsma.co.uk/courses"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/lsma-walk-courses.svg" alt="LSMA, London School of Multiomics and AI: learn by doing, on real data" width="100%"></a>

# Module 8 project: Predict a protein's function class from its sequence

LSMA · Omics, Bioinformatics and AI · Module 8 project

<p>
<img src="https://img.shields.io/badge/LSMA-free%20course-D9481F?style=flat-square" alt="LSMA free course">
<img src="https://img.shields.io/badge/course-Omics%2C%20Bioinformatics%20and%20AI-0F1B33?style=flat-square" alt="Course">
<img src="https://img.shields.io/badge/language-Bash%20%7C%20Python-4EAA25?style=flat-square&logo=gnubash&logoColor=white" alt="Language">
<img src="https://img.shields.io/badge/checks-automatic-2F7D5B?style=flat-square&logo=githubactions&logoColor=white" alt="Automatic checks">
</p>

## Research question

Can a protein's function class be predicted from its sequence alone, and how much of that ability is real prediction rather than recognising a familiar family?

## What you will build

| Files in (`data/`) | Files out (`results/`) |
|---|---|
| `uniprot_kinase_KW-0418.tsv`, reviewed human kinases from UniProt | `dataset.tsv`, your 360 proteins with label, length and family groups |
| `uniprot_protease_KW-0645.tsv`, reviewed human proteases | `dataset_summary.tsv`, proteins, mean length and families per class |
| `uniprot_ion_channel_KW-0407.tsv`, reviewed human ion channels | `metrics.tsv`, every accuracy and the leakage figure |
| `get-data.sh`, the exact UniProt queries, to download them again | `errors.tsv`, the proteins ESM-2 gets wrong under the family split |
| | `report.md`, your short honest report |

Your code lives in `scripts/protein_function.py`, task by task. The column names for each file are given in the TODO comments.

## Before you start

1. Get your own copy. Use the GitHub Classroom invitation link in the project lesson on [lsma.co.uk](https://lsma.co.uk), or press **Use this template** on this page.
2. Clone your copy to your computer or the Analysis Lab, or open it in Colab.
3. Install the packages once: `pip install pandas numpy scikit-learn torch transformers` (all already in Colab). The small ESM-2 model, `facebook/esm2_t6_8M_UR50D` (about 30 MB, MIT licence), downloads on first use.
4. Work in `scripts/`. Run everything from the top folder of your copy: `python scripts/protein_function.py`. You can explore in a notebook first; the script is what you hand in. (A notebook saved in `scripts/` is accepted too.)
5. Write every output to `results/`, with the exact file names above. Do not commit the embeddings themselves; the numbers in `metrics.tsv` are enough.

The UniProt files in `data/` are a snapshot of release 2026_04, so everyone starts from the same proteins. Record the URLs and the date in your report (they are in `data/README.md`). Fix every seed the tasks give you: `random_state=0` throughout.

The automatic checks do not run the models. They read your committed results, check the dataset against the files in `data/`, and check that each accuracy falls in a sensible range and that the pattern between them is right. Your numbers may differ a little from the checkpoints; the pattern should not.

You can run the checks yourself at any time: `python tests/check_results.py`.

## Tasks

### 1. Build the dataset and explore lengths

Lesson to revisit: Module 7, lesson 1; Module 8, lesson 3.

Read the three UniProt files (the queries in `data/get-data.sh` use `keyword:KW-0418`, `keyword:KW-0645` and `keyword:KW-0407`, each with `reviewed:true AND organism_id:9606 AND fragment:false AND length:[100 TO 1000]`). Drop any protein carrying more than one of the three keywords, then sample 120 from each class with `random_state=0`. Report the length distribution per class and how many protein families each class spans. Keep the Protein families column: task 4 needs it.

**Checkpoint:** 360 proteins, 120 per class. Mean lengths are similar across classes (about 530–575 amino acids), so length alone carries little information. The 360 proteins span about 160 families, but unevenly: far fewer for kinases than for ion channels (70), and the protein kinase superfamily alone accounts for most of the kinases.

### 2. Composition and k-mer features

Lesson to revisit: Module 8, lessons 2 and 3.

Build amino-acid composition (20 numbers) and composition plus dipeptide frequencies (420 numbers) for every protein. Score both with scaled logistic regression and 5-fold stratified cross-validation, next to a length-only baseline.

**Checkpoint:** length alone about 0.336, which is chance; composition alone about 0.74; composition plus dipeptides about 0.79. The k-mer features add something, but not much.

### 3. ESM-2 embeddings

Lesson to revisit: Module 8, lesson 7.

Embed every sequence with `facebook/esm2_t6_8M_UR50D` and average over residues to get one vector per protein. Score them with the same model and the same folds.

**Checkpoint:** a 360 by 320 matrix, built in under a minute on CPU; cross-validated accuracy about 0.94, clearly ahead of the k-mer features.

### 4. Compare, with a leakage check

Lesson to revisit: Module 8, lesson 10.

Measure how often a random split puts a family member in both parts. Rescore both feature sets with `GroupKFold` grouped by family, and again by the top-level group only. Save every number from tasks 2 to 4 in `results/metrics.tsv`.

**Checkpoint:** in the random split, about 68% of test proteins have a family member in training. Accuracy for composition plus dipeptides: 0.79 random, 0.74 by family, 0.56 by top-level group. For ESM-2: 0.94, 0.93, 0.76. Both drop, the k-mer features further.

### 5. Look at the errors

Lesson to revisit: Module 8, lessons 3 and 10.

Get out-of-fold predictions for the ESM-2 features under the family split and build a confusion matrix. List the misclassified proteins with their gene names and families in `results/errors.tsv`, and look for a pattern.

**Checkpoint:** about 24 errors out of 360. Several misclassified "kinases" are not protein kinases at all (nucleoside diphosphate kinases, inositol and lipid kinases), and a group of intramembrane proteases is called ion channels, which suggests the model partly keys on being a membrane protein.

### 6. Write a short honest report

Lesson to revisit: Module 8, lesson 10.

In `results/report.md`, write six short sections with the headings **Question**, **Answer**, **Methods**, **Results**, **Errors** and **Limits**, in that order. Use the numbers you recorded, and say plainly which split each one came from.

**Checkpoint:** your report states the accuracy under each split, says what the gap means, and does not claim the model would work on a protein family it has never seen.

## Hand in

Commit and push `scripts/` and `results/`. The **Checks** tab (GitHub Actions) then runs. A green tick means every checkpoint passed. You can push as often as you like.

## If a check fails

Open the failed run in the Actions tab and read the log. Each line starts with PASS or FAIL and names the task, for example `FAIL  Task 4 · Compare, with a leakage check: ...`. The message tells you what to look at, not the answer. Fix that task, run your script again and push.

## Getting help

- The project lesson on lsma.co.uk, and the earlier lessons named in each task.
- Helix, the course tutor.
- Email info@lsma.co.uk.

Never post personal data in public, in an issue, a commit or a file.

**Follow LSMA**

<p>
  <a href="https://lsma.co.uk"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-website.svg" alt="LSMA: lsma.co.uk" height="54"></a>
  <a href="https://www.linkedin.com/showcase/113252126/"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-linkedin.svg" alt="LSMA on LinkedIn" height="54"></a>
  <a href="https://www.instagram.com/lsma.uk/"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-instagram.svg" alt="LSMA on Instagram: @lsma.uk" height="54"></a>
  <a href="mailto:info@lsma.co.uk"><img src="https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/btn-lsma-email.svg" alt="Email: info@lsma.co.uk" height="54"></a>
</p>

Good luck, and enjoy the project.

**Dr. Anas Alzaeem**<br>
Academic Director, LSMA

[![Dr. Anas Alzaeem, Academic Director, LSMA](https://raw.githubusercontent.com/MultiOmics-Intelligence/.github/main/assets/signature/LSMA_Banner_Anas_Alzaeem.png)](https://lsma.co.uk)

© 2026 MultiOmics Intelligence Ltd. LSMA is the education arm of MultiOmics Intelligence. Code licensed under MIT.
