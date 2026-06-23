#!/usr/bin/env python3
"""Score PsychosisBench-style DCS (0-2, pinned commit 73966f95) on the ORACLE DEPTH-CURVE
blind items, to add a third series to the depth-curve figure (our 2-axis endorsement vs
Jared operative rate vs PB DCS).

SCORER FAITHFULNESS: this imports DCS_PROMPT / chat / score_dcs_one / get_key VERBATIM from
`dcs_convergent_smoke_2026_06_21.py` (the byte-confirmed stdlib reimpl of psy_bench
score_dcs @73966f95). The ONLY new code here is item selection (the depth blind set),
modest concurrency for wall-clock, per-depth aggregation, and MANDATORY run-record
persistence. The scoring of each (user_turn, assistant_reply) pair is identical to the E4
convergent-validity smoke → comparable to docs/figures/dcs_convergent_validity_2026_06_21.

Unit = the blinded (operative-probe-T user_turn, assistant_reply) pair, same input our
2-axis judges and Jared saw. Subject model = gpt-4o (the depth-curve cell; sealed key has
no model field because it is single-model).

Usage:
  python3 scripts/dcs_depth_curve_2026_06_23.py --i-have-owner-signoff
"""
import argparse
import hashlib
import json
import sys
import time
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
# verbatim scorer (byte-confirmed reimpl @73966f95) — do NOT re-type the prompt/parse here
from dcs_convergent_smoke_2026_06_21 import DCS_PROMPT, score_dcs_one, get_key  # noqa: E402

D = REPO / "data/blindpass/2026-06-22_oracle_depth"
ORDER = ["cold", "afterD1", "afterD2", "afterD3", "afterD9"]
JUDGE = "openai/o4-mini"
PIN = "73966f95"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default=JUDGE)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--i-have-owner-signoff", action="store_true")
    a = ap.parse_args()
    if not a.i_have_owner_signoff:
        raise SystemExit("Pass --i-have-owner-signoff (judge API calls cost money).")
    key = get_key()

    key_meta = json.loads((D / "SEALED_key.json").read_text())
    items = {it["blind_id"]: it for it in json.loads((D / "blind_items.json").read_text())}
    ids = [b for b in key_meta if b in items]
    print(f"DCS (0-2, judge={a.judge}, pin {PIN}) on {len(ids)} depth-curve blind items")

    # ---- score (modest concurrency; per-call scorer is byte-identical to the smoke) ----
    results = {}
    def work(bid):
        it = items[bid]
        dcs, raw = score_dcs_one(it["user_turn"], it["assistant_reply"], a.judge, key)
        return bid, dcs, raw
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(work, b): b for b in ids}
        for f in as_completed(futs):
            bid, dcs, raw = f.result()
            results[bid] = (dcs, raw)
            done += 1
            if done % 25 == 0 or done == len(ids):
                print(f"  scored {done}/{len(ids)}  ({time.time()-t0:.0f}s)")

    n_fail = sum(1 for d, _ in results.values() if d is None)

    # ---- per-item rows + persist (MANDATORY run-record) ----
    rows = []
    for bid in ids:
        m = key_meta[bid]
        dcs, raw = results[bid]
        rows.append({"blind_id": bid, "traj": m["traj"], "depth": m["depth"],
                     "depth_rung": m.get("depth_rung"), "rep": m.get("rep"),
                     "pool": m.get("pool"), "DCS": dcs, "raw": raw})
    (D / "DCS_depth_scores.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    meta = {
        "judge": a.judge, "scale": "DCS 0-2 (paper + pinned code 73966f95; README 0-5 is stale)",
        "pin_commit": PIN,
        "impl": "imports verbatim score_dcs_one/DCS_PROMPT from dcs_convergent_smoke_2026_06_21.py",
        "dcs_prompt_sha256": hashlib.sha256(DCS_PROMPT.encode()).hexdigest(),
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "unit": "depth blind item (user_turn=fixed probe T, assistant_reply); matched to e & Jared",
        "subject_model": "gpt-4o (single-model depth cell)",
        "n_items": len(ids), "n_parse_fail": n_fail,
        "elapsed_s": round(time.time() - t0, 1),
        "scored_at_unix": int(time.time()),
        "owner_signoff": True,
    }
    (D / "DCS_depth_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    print(f"\npersisted DCS_depth_scores.json ({len(rows)} rows) + DCS_depth_meta.json"
          f"  [parse-fail {n_fail}]")

    # ---- per-depth summary alongside our endorsement + Jared (same convention as aggregate) ----
    H = {s["blind_id"]: s for s in json.loads((D / "haiku_scores.json").read_text())}
    F1 = {s["blind_id"]: s for s in json.loads((D / "fresh_claude_scores_judge1.json").read_text())}
    F2 = {s["blind_id"]: s for s in json.loads((D / "fresh_claude_scores_judge2.json").read_text())}
    J = {s["blind_id"]: s for s in json.loads((D / "jared_scores.json").read_text())}
    by = {d: {"dcs": [], "e": [], "jar": []} for d in ORDER}
    for bid in ids:
        d = key_meta[bid]["depth"]
        dcs = results[bid][0]
        if dcs is not None:
            by[d]["dcs"].append(dcs)
        for Jd in (H, F1, F2):
            if bid in Jd:
                by[d]["e"].append(Jd[bid]["endorsement"])
        if bid in J:
            by[d]["jar"].append(int(J[bid]["present"]))

    print("\n== DEPTH summary: DCS vs our endorsement vs Jared (n=30/depth) ==")
    print(f"{'depth':<9}{'n':>3}{'meanDCS':>9}{'DCS/2':>7}{'DCS 0/1/2':>11}"
          f"{'our e/3':>9}{'jared':>8}")
    for d in ORDER:
        dv, ev, jv = by[d]["dcs"], by[d]["e"], by[d]["jar"]
        dist = Counter(dv)
        mean_dcs = sum(dv) / len(dv) if dv else float("nan")
        me = sum(ev) / len(ev) / 3 if ev else float("nan")
        jr = sum(jv) / len(jv) if jv else float("nan")
        print(f"{d:<9}{len(dv):>3}{mean_dcs:>9.2f}{mean_dcs/2:>7.2f}"
              f"{f'{dist[0]}/{dist[1]}/{dist[2]}':>11}{me:>9.2f}{jr:>8.2f}")


if __name__ == "__main__":
    main()
