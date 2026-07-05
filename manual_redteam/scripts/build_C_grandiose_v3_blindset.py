#!/usr/bin/env python3
"""Build a condition-BLIND 2-axis item set for the 2026-06-18 scenario-C v3
(INTRINSIC grandiosity, chosen / world-historic) gpt-4o-mini pilot.

One item per trajectory = the TERMINAL SCORED assistant reply (the highest rung
the trajectory actually reached: D12 for a break, or the rung it held at, e.g.
D2-reask1) + the nearest preceding user turn. The judge is blind to traj /
condition / rung; it scores the REPLY against the grandiose-significance belief.

Emits blind_items.json + SEALED_key.json.
"""
import glob
import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EP_DIR = REPO / "data/simulator_discover/2026-06-18_delusion_C_grandiose_gpt4omini_v3"
OUT = REPO / "data/blindpass/2026-06-18_C_grandiose_v3"
SEED = 20260618

SCORED = re.compile(r"^D\d")  # D1/D2/D3/D9/D12... (excludes D-rapport, D-bridge)


rows = []
for tf in sorted(glob.glob(str(EP_DIR / "traj*.json"))):
    if "advance_decision" in tf:
        continue
    turns = json.loads(Path(tf).read_text())["turns"]
    term = None  # (idx, rung)
    for i, t in enumerate(turns):
        if t["role"] == "assistant" and SCORED.match(str(t.get("rung", "")).upper()):
            term = (i, t.get("rung"))
    if term is None:
        print(f"  WARN: no scored assistant reply in {Path(tf).stem}")
        continue
    i, rung = term
    user = next((turns[j]["content"] for j in range(i - 1, -1, -1)
                 if turns[j]["role"] == "user"), "")
    rows.append({"src_traj": Path(tf).stem, "rung": rung,
                 "user_context": user, "assistant_text": turns[i]["content"]})

rows.sort(key=lambda r: hashlib.sha1(f"{SEED}-{r['src_traj']}".encode()).hexdigest())
OUT.mkdir(parents=True, exist_ok=True)
blind, key = [], {}
for r in rows:
    bid = "C" + hashlib.sha1(f"{SEED}v3-{r['src_traj']}".encode()).hexdigest()[:8]
    blind.append({"blind_id": bid, "user_turn": r["user_context"], "assistant_reply": r["assistant_text"]})
    key[bid] = {"src_traj": r["src_traj"], "rung": r["rung"]}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} blind items -> {OUT}")
for r in rows:
    bid = "C" + hashlib.sha1(f"{SEED}v3-{r['src_traj']}".encode()).hexdigest()[:8]
    print(f"  {bid}  {r['src_traj']} term_rung={r['rung']}  reply[:55]={r['assistant_text'][:55]!r}")
