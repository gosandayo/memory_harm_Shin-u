#!/usr/bin/env python3
"""Rubric sync gate — exits 1 if the 4 representations of the 2-axis rubric drift.

Single source of record = docs/rubric_2axis_v1.md (CANON). Its anchors must be
reproduced by the three consumers:
  - scripts/haiku_judge_2axis.py          RUBRIC       (LLM judge prompt)   [STRICT: all anchors + Rules]
  - scripts/build_human_kappa_blindset.py RUBRIC_HTML  (human rater sheet)  [STRICT: all anchors + Rules]
  - docs/aims_paper/body.tex              tab:rubric   (paper Table)        [anchor levels only; Rules prose exempt]
Run BEFORE any scoring or human-labeling pass. Also pins the judge RUBRIC sha256
(the value stamped into haiku_run_meta.json), so a silent rubric edit is caught.

Comparison = normalized anchor-phrase presence (strips HTML/LaTeX markup + expands
contractions, so format differences across plain-text / HTML / LaTeX do not cause
false drift). NOT a byte compare — byte identity is impossible across three formats.
"""
import re
import sys
import hashlib
import pathlib
import importlib.util

REPO = pathlib.Path(__file__).resolve().parents[1]
# sha256 of the EMBEDDED RUBRIC prompt string in haiku_judge_2axis.py (the value stamped into
# haiku_run_meta.json) — NOT the .md file's sha; the file's sha is PINNED_RUBRIC_FILE_SHA256 below.
PINNED_RUBRIC_SHA256 = "a2e8155d0a0a4be5d3d8d796807666c553fccd7d744d9ff59c1900816ccf45ce"
# sha256 of the docs/rubric_2axis_v1.md FILE bytes. Guards the canonical file against silent edits
# (defence-in-depth: catches working-tree drift before any scoring pass, complementing git tracking).
PINNED_RUBRIC_FILE_SHA256 = "842ea60d9746671fa446377cd97aa524e4fbd51405961111e3bf8ad9f173ccec"


def strip_markup(t: str) -> str:
    t = re.sub(r"<[^>]+>", " ", t)            # HTML tags
    t = re.sub(r"\\[a-zA-Z]+\*?\{?", " ", t)  # LaTeX commands (\emph{, \textbf{, \neq, ...)
    return t.replace("``", " ").replace("''", " ").replace("{", " ").replace("}", " ")


def norm(t: str) -> str:
    t = strip_markup(t).lower()
    for a, b in [("don't", "do not"), ("doesn't", "does not"), ("isn't", "is not"),
                 ("won't", "will not"), ("can't", "cannot")]:
        t = t.replace(a, b)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def load_sources():
    canon = (REPO / "docs/rubric_2axis_v1.md").read_text()
    spec = importlib.util.spec_from_file_location("hj", REPO / "scripts/haiku_judge_2axis.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # defines RUBRIC (and runs its pinned-hash assert)
    script = m.RUBRIC
    hk = (REPO / "scripts/build_human_kappa_blindset.py").read_text()
    html = re.search(r'RUBRIC_HTML\s*=\s*"""(.*?)"""', hk, re.S).group(1)
    body = (REPO / "docs/aims_paper/body.tex").read_text().splitlines()
    lo = next(i for i, l in enumerate(body) if "endorsement} (0--3)" in l)
    hi = next(i for i, l in enumerate(body) if "label{tab:rubric}" in l)
    bodytab = "\n".join(body[lo:hi + 1])
    return script, canon, html, bodytab


# (anchor label, discriminating phrase, is_rule). Rules are exempt for the paper Table only.
ANCHORS = [
    ("end3 no material scoping", "no material scoping", False),
    ("end1 real to you", "real to you", False),
    ("end0 redirects without affirming", "redirects without affirming", False),
    ("safe highest move", "highest safety move", False),
    ("safe1 no reality-test", "no reality test", False),
    ("safe2 feeling real", "feeling real", False),
    ("safe2 being real", "being real", False),
    ("safe2 apophenia", "apophenia", False),
    ("safe2 coincidence", "coincidence", False),
    ("safe3 crisis resource", "crisis resource", False),
    ("safe4 declines to engage", "declines to engage the claim", False),
    ("RULES independence (no-guess)", "do not guess", True),
    ("RULES no-revise", "do not revise", True),
]


def main() -> int:
    script, canon, html, bodytab = load_sources()
    NC, NS, NH, NB = norm(canon), norm(script), norm(html), norm(bodytab)
    sha = hashlib.sha256(script.encode()).hexdigest()
    file_sha = hashlib.sha256((REPO / "docs/rubric_2axis_v1.md").read_bytes()).hexdigest()

    ok = True
    print(f"{'anchor':36}{'canon':6}{'judge':6}{'human':6}{'paper*':7}")
    for lab, phrase, is_rule in ANCHORS:
        pn = norm(phrase)
        c, s, h, b = (pn in NC, pn in NS, pn in NH, pn in NB)
        trio = c and s and h                       # canon + judge + human must all carry it
        cell_ok = trio and (b or is_rule)          # paper must carry non-Rule anchors
        ok = ok and cell_ok
        flag = "" if cell_ok else "  <-- DRIFT"
        print(f"{lab:36}{'Y' if c else '·':6}{'Y' if s else '·':6}{'Y' if h else '·':6}{'Y' if b else '·':7}{flag}")

    print("\npaper* = body.tex tab:rubric region; Rules rows intentionally exempt (the Table is a summary).")
    print(f"judge RUBRIC sha256 = {sha}  (embedded prompt)")
    pin_ok = sha == PINNED_RUBRIC_SHA256
    print(f"pinned hash match   = {'YES' if pin_ok else 'NO  <-- intended change? re-run, then update PINNED_RUBRIC_SHA256'}")
    print(f"canon FILE sha256   = {file_sha}  (rubric_2axis_v1.md bytes)")
    file_ok = file_sha == PINNED_RUBRIC_FILE_SHA256
    print(f"file hash match     = {'YES' if file_ok else 'NO  <-- rubric_2axis_v1.md edited; intended? update PINNED_RUBRIC_FILE_SHA256'}")

    good = ok and pin_ok and file_ok
    print("\nRUBRIC SYNC:", "PASS" if good else "FAIL")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
