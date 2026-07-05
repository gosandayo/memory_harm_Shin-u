#!/usr/bin/env python3
"""Build a variant-BLIND 2-axis item set for the bridge ablation (gpt-4o delusion).

Three bridge variants, scored under ONE fresh-Claude blind pass, judge blind to
which variant produced each reply:
  dramatic (original)  = data/simulator_discover/2026-06-16_delusion_fresh_op_gpt4o
  mundane / ambiguous  = data/simulator_discover/2026-06-17_delusion_gpt4o_mundanebridge
  no bridge            = data/simulator_discover/2026-06-17_delusion_gpt4o_nobridge

The bridge-ablation comparison is over trajectories that actually REACHED the
endpoint (terminal scored rung == D12). Dramatic traj04/05 held at D2-reask1
BEFORE the bridge (so the bridge was never reached) and are excluded — they are
not part of a bridge effect. One item per kept trajectory = the terminal D12
assistant reply + the nearest preceding user turn. Emits blind_items.json +
SEALED_key.json (variant recorded in the SEALED key only).
"""
import glob
import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = [
    ("dramatic", "2026-06-16_delusion_fresh_op_gpt4o"),
    ("mundane", "2026-06-17_delusion_gpt4o_mundanebridge"),
    ("nobridge", "2026-06-17_delusion_gpt4o_nobridge"),
]
OUT = REPO / "data/blindpass/2026-06-20_bridge_ablation"
SEED = 20260620
SCORED = re.compile(r"^D\d")  # D1/D2/D3/D9/D12 (excludes D-rapport, D-bridge)

rows = []
for variant, d in SRC:
    for tf in sorted(glob.glob(str(REPO / "data/simulator_discover" / d / "traj0?.json"))):
        turns = json.loads(Path(tf).read_text())["turns"]
        term = None
        for i, t in enumerate(turns):
            if t["role"] == "assistant" and SCORED.match(str(t.get("rung", "")).upper()):
                term = (i, t.get("rung"))
        if term is None:
            continue
        i, rung = term
        if str(rung).upper() != "D12":  # bridge comparison = endpoint-reaching trajs only
            print(f"  SKIP (held before endpoint): {variant}/{Path(tf).stem} term_rung={rung}")
            continue
        user = next((turns[j]["content"] for j in range(i - 1, -1, -1)
                     if turns[j]["role"] == "user"), "")
        rows.append({"variant": variant, "src_traj": Path(tf).stem,
                     "src_dir": d, "rung": rung,
                     "user_context": user, "assistant_text": turns[i]["content"]})

# shuffle by hash so order leaks nothing about variant
rows.sort(key=lambda r: hashlib.sha1(f"{SEED}-{r['variant']}-{r['src_traj']}".encode()).hexdigest())
OUT.mkdir(parents=True, exist_ok=True)
blind, key = [], {}
for r in rows:
    bid = "B" + hashlib.sha1(f"{SEED}-{r['variant']}-{r['src_traj']}".encode()).hexdigest()[:8]
    blind.append({"blind_id": bid, "user_turn": r["user_context"],
                  "assistant_reply": r["assistant_text"]})
    key[bid] = {"variant": r["variant"], "src_dir": r["src_dir"],
                "src_traj": r["src_traj"], "rung": r["rung"]}

(OUT / "blind_items.json").write_text(json.dumps(blind, ensure_ascii=False, indent=2) + "\n")
(OUT / "SEALED_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(blind)} blind items -> {OUT}")
for bid, k in key.items():
    print(f"  {bid}  {k['variant']:9s} {k['src_traj']}  rung={k['rung']}")
