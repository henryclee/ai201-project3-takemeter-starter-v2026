"""Validate labels.csv against the brief's contract (collect_plan.md §8).

Usage:
    python validate_labels.py [labels.csv] [labels_meta.csv|""] [min_rows] [pre|final]

Run at stage `pre` (default) straight after collecting: label/note must be blank.
Run it again at stage `final` once labelling is done: every label must be filled,
must be spelled like the taxonomy, and no label may exceed the 70% cap. Re-run
after any manual prune — that is where duplicates and blank rows creep in.

Prints the numbers that would otherwise hurt a run quietly: duplicates (which leak
between train and test and inflate the score), sub-40-char rows, HTML left over
from the feed parser, bare-URL rows, and the long tail that hits bart-large-mnli's
~1,024-token window. Exits non-zero if anything fails.
"""
import csv
import collections
import re
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "labels.csv"
META = sys.argv[2] if len(sys.argv) > 2 else "labels_meta.csv"
MIN_ROWS = int(sys.argv[3]) if len(sys.argv) > 3 else 500
STAGE = sys.argv[4] if len(sys.argv) > 4 else "pre"
TAXONOMY = {"announcement", "advice", "news/discussion", "showcase"}

problems = []


def check(label, bad, ok_note):
    """`bad` = nothing (ok), a bool, or a list of offending CSV line numbers."""
    n = len(bad) if isinstance(bad, (list, tuple, dict)) else int(bool(bad) or 0)
    if not n:
        print(f"  ok   {label} ({ok_note})")
        return
    if isinstance(bad, (list, tuple)):
        ids = ", ".join(str(x) for x in list(bad)[:15])
        shown = ids + (f" (+{n - 15} more)" if n > 15 else "")
    else:
        shown = str(bad)
    problems.append(f"{label} -> {shown}")
    print(f"  FAIL {label} -> {shown}")


rows = list(csv.reader(open(PATH, encoding="utf-8")))
hdr, body = rows[0], rows[1:]
print(f"{PATH}: header={hdr} rows={len(body)} stage={STAGE}")

check("header", hdr != ["text", "label", "note"], "text,label,note")
check("row count", len(body) < MIN_ROWS, f">= {MIN_ROWS}")
check("ragged rows", [i for i, r in enumerate(body, 2) if len(r) != 3], "3 fields each")
check("empty text", [i for i, r in enumerate(body, 2) if not r[0].strip()], "none")
check("rows under 40 chars", [i for i, r in enumerate(body, 2) if len(r[0].strip()) < 40],
      "none")
norm = [" ".join(r[0].lower().split()) for r in body]
check("duplicate text", [i for i, t in enumerate(norm, 2) if t in norm[:i - 2]], "none")
check("html remnants", [i for i, r in enumerate(body, 2)
                        if re.search(r"<[a-z]+>|\[link\]|\[comments\]|&amp;|&#x", r[0])],
      "none")
check("bare-url rows", [i for i, r in enumerate(body, 2)
                        if r[0].lower().startswith(("http://", "https://"))], "none")

filled = [r[1].strip() for r in body if r[1].strip()]
if STAGE == "pre":
    check("label blank", [i for i, r in enumerate(body, 2) if r[1].strip()], "all blank")
    check("note blank", [i for i, r in enumerate(body, 2) if r[2].strip()], "all blank")
else:
    check("blank label", [i for i, r in enumerate(body, 2) if not r[1].strip()],
          "none left")
    check("unknown label", sorted({l for l in filled if l not in TAXONOMY}),
          "all in taxonomy")
    counts = collections.Counter(filled)
    top, n_top = counts.most_common(1)[0] if counts else ("-", 0)
    share = n_top / len(body) if body else 0
    check(f"label share (top: {top})",
          f"{n_top} of {len(body)} rows ({share:.0%}) - over the cap" if share > 0.70
          else False, "no label above 70%")
    print(f"  counts: {dict(counts)}")
    print(f"  cold-start rows (note=cold): "
          f"{sum(1 for r in body if r[2].strip() == 'cold')}")

print(f"  unique={len(set(norm))}  longest={max(len(r[0]) for r in body)} chars  "
      f">3000 chars={sum(1 for r in body if len(r[0]) > 3000)}  "
      f"title-only={sum(1 for r in body if chr(10) + chr(10) not in r[0])}")

try:
    import pandas as pd
    print(f"  pandas round-trip: {pd.read_csv(PATH).shape}")
except ImportError:                                  # pragma: no cover
    print("  pandas not installed - skipped round-trip")

if META:
    try:
        meta = list(csv.DictReader(open(META, encoding="utf-8")))
    except FileNotFoundError:
        print(f"{META} not found - no sidecar to check")
        meta = None
    if meta is not None:
        kinds = collections.Counter(x["kind"] for x in meta)
        wins = collections.Counter(x["window"] for x in meta)
        print(f"{META}: rows={len(meta)} kind={dict(kinds)} windows={dict(wins)}")
        check("sidecar row count",
              "sidecar %d != labels %d" % (len(meta), len(body)) if len(meta) != len(body)
              else False, "matches labels.csv")
        check("comments collected", sorted(set(kinds) - {"post"}) or False, "posts only")
        need = {"text", "source", "url", "score", "kind", "window", "rank"}
        check("sidecar columns", sorted(need - set(meta[0])) or False,
              "provenance present")

print("\nPASS" if not problems else "\nFAIL:\n  " + "\n  ".join(problems))
sys.exit(1 if problems else 0)

