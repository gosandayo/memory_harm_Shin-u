"""Build G1/G2 reask-isolation user-side prefixes.

Motivation (locked w/ user 2026-05-17): FA-Aprime did NOT remove the suicide
referent at S13-time — its terminal turn 8 (S12) reintroduces an explicit
weighing referent one turn before S13. So FA-Aprime refutes only the LONG
laddered / self-consistency-precedent mechanism, NOT referent-establishment
per se. The FA-Aprime S13 5/5 flip is consistent with a minimal
"S12 plants referent -> model refuses -> S13 leading reask -> capitulation"
foot-in-the-door dynamic. G1/G2 isolate that with ZERO filler:

  G1 = cold, [S12, S13, CONF]   -> minimal 1-turn referent + reask, no buildup
  G2 = cold, [S13, CONF]        -> S13 alone (re-confirm prior cold-S13 refuse
                                    at the EXACT ablation wording)

Subtractions:
  warm-context contribution = FA-Aprime  - G1
  reask (S12-plant) contribution = G1    - G2

Terminal strings are IMPORTED from build_filler_ablation_prefixes so they are
byte-identical to the FA arms (no wording drift confound).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from build_filler_ablation_prefixes import S12, S13, CONF

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "context_prefixes"
N = 5
DATE = "2026-05-17"

ARMS = {
    "G1": [S12, S13, CONF],
    "G2": [S13, CONF],
}


def write_prefix(arm: str, run: int, turns: list[str]) -> Path:
    rid = f"{DATE}_reask_{arm}_run{run:02d}"
    doc = {
        "id": f"{rid}_userside",
        "source_run_id": rid,
        "description": (
            f"Reask isolation {arm} run{run:02d}. Pre-reg note: "
            "manual_redteam/docs/filler_ablation_results_2026_05_16.md "
            "follow-up (G1/G2, 2026-05-17). Terminal byte-identical to FA "
            "arms; ZERO filler. 5 identical replicates per arm "
            "(IV = presence of S12-plant turn / G1 vs G2)."
        ),
        "turns": [{"id": i + 1, "user": t} for i, t in enumerate(turns)],
    }
    path = OUT / f"{rid}_userside.yaml"
    path.write_text(
        yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=88)
    )
    return path


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # Guard: terminal must match the FA builder verbatim.
    assert ARMS["G1"] == [S12, S13, CONF]
    assert ARMS["G2"] == [S13, CONF]
    assert ARMS["G1"][-2:] == ARMS["G2"], "G2 must be G1 minus the S12 plant"
    written = []
    for run in range(N):
        for arm, turns in ARMS.items():
            written.append(write_prefix(arm, run, turns))
    for p in written:
        print(p.relative_to(ROOT.parent))
    print(f"\n{len(written)} prefixes written (G1 x{N}, G2 x{N}).")
    print("G1 = [S12,S13,CONF]; G2 = [S13,CONF]; terminal == FA arms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
