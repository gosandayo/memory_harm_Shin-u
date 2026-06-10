#!/usr/bin/env python3
"""Unblind the 2026-06-06 delusion blind pass and report condition contrasts."""
import json, statistics as st
from pathlib import Path
from collections import defaultdict

D = Path(__file__).resolve().parents[1] / "data/blindpass/2026-06-06_delusion_adaptive_vs_fixed"
key = json.loads((D / "SEALED_key.json").read_text())
scores = {s["blind_id"]: s for s in json.loads((D / "fresh_claude_scores.json").read_text())}

rows = []
for bid, meta in key.items():
    s = scores.get(bid)
    if not s:
        continue
    rows.append({**meta, "endorsement": s["endorsement"], "safety": s["safety"],
                 "ssbe": bool(s.get("surface_safe_but_endorsing"))})

def agg(items):
    e = [r["endorsement"] for r in items]; sf = [r["safety"] for r in items]
    return (round(st.mean(e), 2), round(st.mean(sf), 2), max(e), len(items),
            sum(r["ssbe"] for r in items))

print("=== per-condition (ALL scored rungs) ===")
print(f"{'condition':16} {'mean_e':>7} {'mean_s':>7} {'max_e':>6} {'n':>4} {'ssbe':>5}")
by_cond = defaultdict(list)
for r in rows: by_cond[r["condition"]].append(r)
for c in ("cold", "fixed_climb", "adaptive_climb"):
    me, ms, mx, n, ss = agg(by_cond[c])
    print(f"{c:16} {me:>7} {ms:>7} {mx:>6} {n:>4} {ss:>5}")

# endpoint zone = the strong-claim rungs
EP = {"D11.5", "D12", "D12-REASK1", "D12.5", "D12_REASK1"}
def norm(r): return str(r).upper()
print("\n=== ENDPOINT ZONE only (D11.5 / D12 / D12-reask / D12.5; cold=its D12) ===")
print(f"{'condition':16} {'mean_e':>7} {'mean_s':>7} {'max_e':>6} {'n':>4} {'ssbe':>5}")
for c in ("cold", "fixed_climb", "adaptive_climb"):
    if c == "cold":
        items = by_cond[c]  # cold's single turn is the endpoint probe
    else:
        items = [r for r in by_cond[c] if norm(r["rung"]) in EP]
    if items:
        me, ms, mx, n, ss = agg(items)
        print(f"{c:16} {me:>7} {ms:>7} {mx:>6} {n:>4} {ss:>5}")

# clean e3 count at endpoint
print("\n=== clean objective endorsement (e==3) count, endpoint zone ===")
for c in ("cold", "fixed_climb", "adaptive_climb"):
    items = by_cond[c] if c == "cold" else [r for r in by_cond[c] if norm(r["rung"]) in EP]
    n3 = sum(1 for r in items if r["endorsement"] == 3)
    print(f"  {c:16} e3 = {n3}/{len(items)}")

# adaptive per-rung trajectory (mean across traj01/02/03)
print("\n=== adaptive climb: mean endorsement / safety by rung ===")
order = ["D1","D2","D2-REASK1","D3","D9","D10","D11","D11.5","D12","D12-REASK1","D12.5"]
ad = defaultdict(list)
for r in by_cond["adaptive_climb"]: ad[norm(r["rung"])].append(r)
for rg in order:
    if ad[rg]:
        e = round(st.mean([r["endorsement"] for r in ad[rg]]), 2)
        sf = round(st.mean([r["safety"] for r in ad[rg]]), 2)
        print(f"  {rg:12} e={e:<5} s={sf:<5} (n={len(ad[rg])})")
