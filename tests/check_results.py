"""Automatic checks for Module 8 project: Predict a protein's function class from its sequence.

Run from the top folder of your copy:   python tests/check_results.py
It reads only the files you commit in results/ and scripts/, uses the Python
standard library only, and prints PASS or FAIL for each task.
"""
import csv
import hashlib
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
_failed = []


class Fail(Exception):
    pass


def check(label):
    """Run one labelled check and print PASS or FAIL."""
    def wrap(fn):
        try:
            fn()
        except Fail as err:
            print(f"FAIL  {label}: {err}")
            _failed.append(label)
        except Exception as err:  # an unreadable file should guide, not crash
            print(f"FAIL  {label}: could not read your results ({type(err).__name__}: {err})")
            _failed.append(label)
        else:
            print(f"PASS  {label}")
        return fn
    return wrap


def finish():
    print()
    if _failed:
        print(f"{len(_failed)} check(s) failed. Read the messages above, fix that task and push again.")
        sys.exit(1)
    print("Every checkpoint passed. Well done.")


def need(path):
    path = Path(path)
    if not path.exists():
        raise Fail(f"{path.relative_to(ROOT)} not found; create it and commit it")
    return path


def read_rows(path):
    """Read a CSV (or tab-separated) file into a list of dicts with lower-case keys."""
    text = need(path).read_text(encoding="utf-8-sig")
    dialect = "excel-tab" if "\t" in text.splitlines()[0] else "excel"
    rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
    return [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items()} for r in rows]


def column(rows, *names, path=""):
    if not rows:
        raise Fail(f"{path} has no data rows")
    for n in names:
        if n in rows[0]:
            return n
    raise Fail(f"{path} needs a column called {names[0]}; found {', '.join(rows[0])}")


def num(value, what):
    try:
        return float(str(value).replace("%", "").strip())
    except ValueError:
        raise Fail(f"{what}: '{value}' is not a number")


def near(a, b, tol):
    return abs(a - b) <= tol


def _norm(text):
    return re.sub(r"\s+", " ", text.replace("\r", "")).strip()


def sha(path):
    return hashlib.sha256(_norm(Path(path).read_text(encoding="utf-8")).encode()).hexdigest()


def edited(path, starter_sha):
    path = need(path)
    if sha(path) == starter_sha:
        raise Fail(f"{path.relative_to(ROOT)} is still the untouched starter; write your code in it")
    return path


def png_info(path):
    """Width, height and dpi (None if not stored) of a PNG file."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", data[16:24])
    dpi = None
    i = 8
    while i + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[i:i + 8])
        if kind == b"pHYs":
            x, _, unit = struct.unpack(">IIB", data[i + 8:i + 17])
            if unit == 1:
                dpi = x * 0.0254
            break
        if kind == b"IDAT":
            break
        i += 12 + length
    return w, h, dpi


def image(path, min_px=300, min_bytes=5000):
    """Check that a PNG or SVG is a real image of sensible size; return PNG info."""
    path = need(path)
    rel = path.relative_to(ROOT)
    size = path.stat().st_size
    if size < min_bytes:
        raise Fail(f"{rel} is only {size} bytes; it looks empty")
    if path.suffix.lower() == ".svg":
        head = path.read_text(encoding="utf-8", errors="replace")[:5000]
        if "<svg" not in head:
            raise Fail(f"{rel} is not a valid SVG file")
        return None
    info = png_info(path)
    if info is None:
        raise Fail(f"{rel} is not a real PNG file (was it renamed from another format?)")
    w, h, _ = info
    if w < min_px or h < min_px // 3:
        raise Fail(f"{rel} is only {w} x {h} pixels; save it with a higher dpi")
    return info


def text_of(path, min_words=0):
    path = need(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    words = len(re.findall(r"\w+", text))
    if words < min_words:
        raise Fail(f"{path.relative_to(ROOT)} has {words} words; write at least {min_words}")
    return text

FILES = {"kinase": ("KW-0418", "uniprot_kinase_KW-0418.tsv"),
         "protease": ("KW-0645", "uniprot_protease_KW-0645.tsv"),
         "ion_channel": ("KW-0407", "uniprot_ion_channel_KW-0407.tsv")}
LABELS = set(FILES)


def uniprot():
    """accession -> (label, length, families field, keyword ids) from the data snapshot."""
    out = {}
    for label, (kw, fname) in FILES.items():
        for r in read_rows(DATA / fname):
            out.setdefault(r["entry"], []).append(
                (label, int(r["length"]), r["protein families"] or "none", r["keyword id"]))
    return out


def dataset():
    path = "results/dataset.tsv"
    rows = read_rows(RESULTS / "dataset.tsv")
    for c in ("accession", "label", "length", "family", "top_group"):
        column(rows, c, path=path)
    return rows


def metrics():
    path = "results/metrics.tsv"
    rows = read_rows(RESULTS / "metrics.tsv")
    column(rows, "metric", path=path)
    column(rows, "value", path=path)
    return {r["metric"].lower(): r["value"] for r in rows}


def metric(m, name, lo, hi, hint):
    if name not in m:
        raise Fail(f"results/metrics.tsv has no row for {name}")
    v = num(m[name], name)
    if v > 1.5:
        raise Fail(f"{name} should be a fraction between 0 and 1, not a percentage")
    if not lo <= v <= hi:
        raise Fail(f"{name} = {v:.3f} is outside the range expected for this dataset "
                   f"({lo:.2f} to {hi:.2f}); {hint}")
    return v


@check("Setup · Your script")
def _():
    if list(SCRIPTS.glob("*.ipynb")):
        return
    edited(SCRIPTS / "protein_function.py", "46531fe5e246a4b7905c3c000996cb6c73d01e3ef04a69bd7d710efbf23c3652")


@check("Task 1 · Build the dataset and explore lengths")
def _():
    rows = dataset()
    ref = uniprot()
    if len(rows) != 360:
        raise Fail(f"expected 360 rows in results/dataset.tsv (120 per class), found {len(rows)}")
    counts = {}
    for r in rows:
        counts[r["label"]] = counts.get(r["label"], 0) + 1
    if set(counts) != LABELS or any(v != 120 for v in counts.values()):
        raise Fail("results/dataset.tsv should hold 120 proteins of each class, labelled "
                   + ", ".join(sorted(LABELS)))
    accs = [r["accession"].upper() for r in rows]
    if len(set(accs)) != len(accs):
        raise Fail("some accessions appear twice in results/dataset.tsv")
    for r in rows:
        a = r["accession"].upper()
        if a not in ref:
            raise Fail(f"{a} is not in the UniProt files in data/; build the dataset from them")
        if len(ref[a]) > 1:
            raise Fail(f"{a} carries more than one of the three keywords; drop such proteins "
                       "before sampling")
        label, length, fams, _ = ref[a][0]
        if r["label"] != label:
            raise Fail(f"{a} has the wrong label; it comes from the {label} file")
        if r["family"] != ", ".join(fams.split(", ")[:2]) or r["top_group"] != fams.split(", ")[0]:
            raise Fail(f"the family groups for {a} are not right: family is the first two parts "
                       "of 'Protein families', top_group the first part ('none' if empty)")
    path = "results/dataset_summary.tsv"
    summ = read_rows(RESULTS / "dataset_summary.tsv")
    for c in ("label", "proteins", "mean_length", "families"):
        column(summ, c, path=path)
    got = {s["label"]: s for s in summ}
    for label in LABELS:
        if label not in got:
            raise Fail(f"{path} needs a row for {label}")
        mine = [r for r in rows if r["label"] == label]
        mean = sum(ref[r["accession"].upper()][0][1] for r in mine) / len(mine)
        fams = len({r["family"] for r in mine})
        if not near(num(got[label]["mean_length"], "mean_length"), mean, 0.6):
            raise Fail(f"mean_length for {label} does not match your dataset")
        if int(num(got[label]["families"], "families")) != fams:
            raise Fail(f"families for {label} does not match your dataset; count distinct "
                       "family groups")


@check("Task 2 · Composition and k-mer features")
def _():
    m = metrics()
    metric(m, "length_random", 0.20, 0.45, "length alone should be close to chance (0.333)")
    comp = metric(m, "composition_random", 0.60, 0.85,
                  "check the 20 composition shares and the scaled logistic regression")
    kmer = metric(m, "kmer_random", 0.65, 0.90,
                  "check the 400 dipeptide frequencies and C = 0.1")
    if kmer < comp - 0.03:
        raise Fail("composition plus dipeptides should do at least as well as composition alone")


@check("Task 3 · ESM-2 embeddings")
def _():
    m = metrics()
    for name, want in (("esm2_rows", 360), ("esm2_dims", 320)):
        if name not in m or int(num(m[name], name)) != want:
            raise Fail("the ESM-2 matrix should have one row per protein and 320 numbers per "
                       "protein (esm2_rows and esm2_dims in results/metrics.tsv)")
    esm = metric(m, "esm2_random", 0.85, 1.0,
                 "average over residues, without the first and last token")
    if esm <= num(m.get("kmer_random", "0"), "kmer_random"):
        raise Fail("ESM-2 should score clearly ahead of the k-mer features")


@check("Task 4 · Compare, with a leakage check")
def _():
    m = metrics()
    metric(m, "random_split_family_overlap", 0.50, 0.85,
           "the share of test proteins whose family is also in the training part")
    kr, er = num(m.get("kmer_random", "0"), "kmer_random"), num(m.get("esm2_random", "0"), "esm2_random")
    kf = metric(m, "kmer_family", 0.55, 0.85, "use GroupKFold with groups=family")
    kt = metric(m, "kmer_toplevel", 0.40, 0.70, "use GroupKFold with groups=top_group")
    ef = metric(m, "esm2_family", 0.80, 0.98, "use GroupKFold with groups=family")
    et = metric(m, "esm2_toplevel", 0.60, 0.92, "use GroupKFold with groups=top_group")
    if kf > kr + 0.02 or ef > er + 0.02:
        raise Fail("the family split should not score higher than the random split")
    if kt > kr - 0.1 or et > er - 0.03:
        raise Fail("the top-level split should drop clearly below the random split")
    if (kr - kt) <= (er - et):
        raise Fail("the k-mer features should drop further than ESM-2 under the top-level split")


@check("Task 5 · Look at the errors")
def _():
    path = "results/errors.tsv"
    rows = read_rows(RESULTS / "errors.tsv")
    for c in ("accession", "gene", "family", "true", "predicted"):
        column(rows, c, path=path)
    data = {r["accession"].upper(): r for r in dataset()}
    if not 10 <= len(rows) <= 50:
        raise Fail(f"{path} lists {len(rows)} errors; the family split should give a few dozen")
    for r in rows:
        a = r["accession"].upper()
        if a not in data:
            raise Fail(f"{a} in {path} is not in results/dataset.tsv")
        if r["true"] != data[a]["label"]:
            raise Fail(f"the true label of {a} in {path} does not match results/dataset.tsv")
        if r["predicted"] == r["true"] or r["predicted"] not in LABELS:
            raise Fail(f"{a}: predicted should be a different class from true")
    m = metrics()
    ef = num(m.get("esm2_family", "0"), "esm2_family")
    if abs((360 - len(rows)) / 360 - ef) > 0.03:
        raise Fail("the number of errors does not fit esm2_family; use cross_val_predict with "
                   "the same GroupKFold and family groups")


@check("Task 6 · Write a short honest report")
def _():
    text = text_of(RESULTS / "report.md", min_words=250)
    heads = [h.strip().lower() for h in re.findall(r"^#+\s*(.+)$", text, flags=re.M)]
    order = ["question", "answer", "methods", "results", "errors", "limits"]
    pos = []
    for h in order:
        hits = [i for i, x in enumerate(heads) if x.startswith(h)]
        if not hits:
            raise Fail(f"results/report.md needs a heading called {h.capitalize()}")
        pos.append(hits[0])
    if pos != sorted(pos):
        raise Fail("the headings in results/report.md should come in the order "
                   + ", ".join(h.capitalize() for h in order))
    low = text.lower()
    if "0.333" not in low and "33.3" not in low:
        raise Fail("results/report.md should put chance (0.333) next to your accuracies")
    if "random" not in low or "family" not in low:
        raise Fail("results/report.md should say which split each number comes from")
    if "rest.uniprot.org" not in low:
        raise Fail("the methods should give the UniProt query URLs")
    if not re.search(r"\b20\d\d\b", text):
        raise Fail("the methods should give the date of the download or the UniProt release")


finish()
