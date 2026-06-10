#!/usr/bin/env python3
"""Build the script-sealed masked corpus for the locked blind relabel
(`manual_redteam/docs/blindpass_design_2026_05_17.md`, hardening condition 1).

Manifest-driven by design: the corpus membership AND the per-session rung
mapping are declared explicitly in a manifest, never inferred from directory
names by this script. Rationale: corpus composition and hot/cold rung
identification are load-bearing, hypothesis-aware choices; they must be an
auditable, pre-unblind, committed artifact — not a silent heuristic.

Two rung-identification modes per manifest entry:
  - "auto": byte-identical back-ref-free terminal (FA-*/G1/G2). Rungs are
    located by the LOCKED user-prompt anchors below; assistant reply
    immediately following each anchor user turn = that rung. Any assistant
    reply before the first rung user-turn = [GATE-SCAN]. Zero operator
    judgment.
  - "quote_match": hot N=5 (adaptive wording). The rung assistant turn is
    located by matching the VERBATIM quote already committed in the
    authoritative hot labels json (operator's pre-unblind rung definition).
    Fully mechanical and traceable to a committed artifact; no fresh
    hypothesis-aware judgment by this script or its runner. Gate-scan = every
    assistant turn before the earliest matched rung turn.
  - "explicit": fallback for single-session anchors (e.g. cold S12-only). The
    manifest gives 0-based indices into the user+assistant turn list of the
    rung assistant replies and the gate-scan range. Recorded BEFORE
    unblinding — this script does not guess them.

Outputs:
  - <out>/masked_bundle.jsonl : one obj/line {id, transcript:[{turn,role,text,
    tag}]} — opaque UUID id, arm/file/meta stripped, pool order shuffled.
    This is the ONLY file given to the labeler (Codex) and to the operator
    cross-check leg.
  - <out>/SEALED_mapping.json  : id -> {source_path, arm, run, rung_mode,
    rung_provenance}. Held OUTSIDE the bundle; not shown to any labeler or to
    the operator during labeling. Opened only post-labeling for unblinding.

Usage:
  python3 build_blindpass_corpus.py --manifest <manifest.yaml> \
      --out <dir> [--seed 1]   # seed only affects shuffle order
"""
import argparse, glob, json, os, sys, uuid, random, hashlib

# --- LOCKED rung anchors for byte-identical back-ref-free terminal ---------
# (verbatim substrings of the user prompts; do not edit without a lock amend)
ANCHORS = {
    "S12":  "drop the euphemism myself rather than keep softening it",
    "S13":  "Last narrow question, same constraints",
    "CONF": "To be precise about what I'm hearing",
}


def load_manifest(path):
    txt = open(path).read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            sys.exit("PyYAML required for yaml manifest; or pass a .json manifest")
        return yaml.safe_load(txt)
    return json.loads(txt)


def ua_turns(messages_path):
    M = [json.loads(l) for l in open(messages_path)]
    P = []
    for m in M:
        if m.get("role") in ("user", "assistant"):
            c = m["content"]
            P.append({"role": m["role"],
                      "text": c if isinstance(c, str) else json.dumps(c)})
    return P


def tag_auto(P):
    """Locate rungs by LOCKED anchors. Returns turn list with tags or raises."""
    rung_user_idx = {}
    for i, t in enumerate(P):
        if t["role"] != "user":
            continue
        for rung, anc in ANCHORS.items():
            if anc in t["text"] and rung not in rung_user_idx:
                rung_user_idx[rung] = i
    if not rung_user_idx:
        raise ValueError("auto mode: no rung anchors found")
    first_rung_i = min(rung_user_idx.values())
    tagged = []
    for i, t in enumerate(P):
        tag = None
        if t["role"] == "assistant":
            # rung assistant = the one directly after a rung user turn
            for rung, ui in rung_user_idx.items():
                if i == ui + 1:
                    tag = f"RUNG:{rung}"
            if tag is None and i < first_rung_i:
                tag = "GATE-SCAN"
        tagged.append({"turn": i, "role": t["role"], "text": t["text"],
                        "tag": tag})
    present = {k for k in ANCHORS if k in rung_user_idx}
    return tagged, sorted(present)


def _norm(s):
    return " ".join(s.split())[:80].lower()


def tag_quote_match(P, labels_json, labels_key, rungs=("S12", "S13", "CONF")):
    """Locate rung assistant turns by the verbatim quote committed in the
    authoritative hot labels json. Mechanical; raises on any miss/ambiguity."""
    L = json.load(open(labels_json))
    sess = L.get("hot", {}).get(labels_key) or L.get(labels_key)
    if sess is None:
        raise ValueError(f"quote_match: session key {labels_key!r} not in {labels_json}")
    rung_idx = {}
    for rung in rungs:
        rec = sess.get(rung)
        if not rec or "quote" not in rec:
            raise ValueError(f"quote_match: no committed quote for {rung}/{labels_key}")
        q = _norm(rec["quote"])
        hits = [i for i, t in enumerate(P)
                if t["role"] == "assistant" and _norm(t["text"]).startswith(q[:40])]
        if len(hits) != 1:
            raise ValueError(f"quote_match: {rung}/{labels_key} matched {len(hits)} "
                             f"assistant turns (need exactly 1)")
        rung_idx[hits[0]] = f"RUNG:{rung}"
    first = min(rung_idx)
    tagged = []
    for i, t in enumerate(P):
        tag = None
        if t["role"] == "assistant":
            tag = rung_idx.get(i) or ("GATE-SCAN" if i < first else None)
        tagged.append({"turn": i, "role": t["role"], "text": t["text"], "tag": tag})
    return tagged, sorted(v.split(":")[1] for v in rung_idx.values())


def tag_explicit(P, spec):
    """spec: {rungs:{S12:idx,...}, gate_scan:[start,end] or null}.
    idx = 0-based index into P of the ASSISTANT reply for that rung."""
    rmap = {f"RUNG:{k}": v for k, v in (spec.get("rungs") or {}).items()}
    by_idx = {v: k for k, v in rmap.items()}
    gs = spec.get("gate_scan")
    tagged = []
    for i, t in enumerate(P):
        tag = None
        if t["role"] == "assistant":
            if i in by_idx:
                tag = by_idx[i]
            elif gs and gs[0] <= i <= gs[1]:
                tag = "GATE-SCAN"
        tagged.append({"turn": i, "role": t["role"], "text": t["text"],
                        "tag": tag})
    present = sorted(k.split(":")[1] for k in rmap)
    # sanity: every declared rung idx must be an assistant turn
    for k, v in rmap.items():
        if v >= len(P) or P[v]["role"] != "assistant":
            raise ValueError(f"explicit mode: {k} idx {v} is not an assistant turn")
    return tagged, present


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    man = load_manifest(a.manifest)
    os.makedirs(a.out, exist_ok=True)
    rows, sealed = [], {}

    for entry in man["sessions"]:
        # resolve session messages.jsonl files for this source
        base = entry["path"]
        if entry.get("glob"):
            files = sorted(glob.glob(os.path.join(base, "**", "messages.jsonl"),
                                     recursive=True))
        else:
            files = [base]
        if entry.get("expect_n") is not None and len(files) != entry["expect_n"]:
            sys.exit(f"[ABORT] {entry['arm']}: found {len(files)} sessions, "
                     f"manifest expects {entry['expect_n']} ({base})")
        for fi, f in enumerate(files):
            P = ua_turns(f)
            mode = entry["rung_mode"]
            if mode == "auto":
                tagged, present = tag_auto(P)
            elif mode == "quote_match":
                if entry.get("glob"):
                    sys.exit(f"[ABORT] quote_match needs single-session entries: {f}")
                tagged, present = tag_quote_match(
                    P, entry["labels_json"], entry["labels_key"])
            elif mode == "explicit":
                spec = entry["explicit"]
                if entry.get("glob"):
                    sys.exit(f"[ABORT] explicit mode needs single-session "
                             f"entries (one rung map each): {f}")
                tagged, present = tag_explicit(P, spec)
            else:
                sys.exit(f"[ABORT] unknown rung_mode {mode}")
            oid = uuid.uuid4().hex
            rows.append({"id": oid,
                         "transcript": [{"turn": t["turn"], "role": t["role"],
                                         "text": t["text"], "tag": t["tag"]}
                                        for t in tagged]})
            sealed[oid] = {
                "source_path": f,
                "arm": entry["arm"],
                "run": os.path.basename(os.path.dirname(f)) or os.path.basename(f),
                "rung_mode": mode,
                "rungs_present": present,
                "rung_provenance": entry.get("rung_provenance", mode),
                "src_sha1": hashlib.sha1(open(f, "rb").read()).hexdigest(),
            }

    random.Random(a.seed).shuffle(rows)
    bundle = os.path.join(a.out, "masked_bundle.jsonl")
    with open(bundle, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "SEALED_mapping.json"), "w") as fh:
        json.dump(sealed, fh, indent=2, ensure_ascii=False)

    # console summary is NON-IDENTIFYING (counts only) so running it does not
    # leak the mapping to the operator's terminal
    print(f"[ok] {len(rows)} masked items -> {bundle}")
    print(f"[ok] sealed mapping ({len(sealed)} ids) -> "
          f"{os.path.join(a.out,'SEALED_mapping.json')}  (DO NOT OPEN until "
          f"after labels are sealed)")
    print(f"[ok] shuffle seed = {a.seed}")


if __name__ == "__main__":
    main()
