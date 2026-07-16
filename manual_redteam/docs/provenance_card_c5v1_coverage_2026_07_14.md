# Provenance card — C5-V1 move-coverage (2026-07-14)

> Agent fills; Shin verifies the load-bearing path (~5 min) and sets STATUS.
> A number with no `VERIFIED` card may NOT enter Slack/paper as a claim.

---

## CARD: `c5v1-move-coverage-95`

- **CLAIM:** In real de-identified user chat logs, **95% of escalation moves (418/438, Wilson 95% CI 93–97%)** fall into the epistemic move-types our special-insight ladder decomposes (D1 noticing / D2 externalization / D3 personalization / D4 weighing / D5 conviction / AI-witness); the ~5% not covered is one coherent gap — conferring personhood/agency on the AI itself.
- **TIER:** CLAIM
- **STATUS:** AGENT-ASSERTED

**PROVENANCE line**
```
418/438 = data/cleansep/c5_v1_judged_confirm.jsonl
  → 897 confirm user-turns (unread remainder of the 150 bot-endorses-delusion windows; dev windows excluded)
  → Stage-1 gate: keep stage1=="escalation" (438); coverage numerator stage2 ∈ {D1,D2,D3,D4,D5,AIW} (418)
  → coverage = covered/escalation, Wilson 95% CI
  → robust to meets_code slice: 98.5% (meets_code=True, 194/197) / 92.9% (else, 224/241)
  → reliability: dev inter-rater κ (N=171) covered-vs-OTHER=0.88, gate=0.77, move-type=0.71
```

**Load-bearing path (the only code Shin must read):**

| stage | file:line | what it does |
|---|---|---|
| data selection | `scripts/c5_v1_move_coverage.py:62-63` | `sub = it[it["label"]=="bot-endorses-delusion"]` — only endorsement windows |
| dev/confirm tag | `scripts/c5_v1_move_coverage.py:69-70` | `split="dev" if (participant,start) in burned recon keys else "confirm"` |
| turn extraction | `scripts/c5_v1_move_coverage.py:72-90` | one record per `role=="user"` non-empty turn; 897 confirm |
| scorer-input | blind-subagent prompt (appendix of `docs/c5_v1_handoff_2026_07_13.md`) | frozen rubric sha `6d6ffc531749` + context + user_turn; classify user_turn only |
| score parse | merge step (this card's run) | subagent JSON `{stage1,stage2}` per rid → `c5_v1_judged_confirm.jsonl` (897, schema-checked: stage2 null iff not escalation; 0 violations) |
| exclusion | `scripts/c5_v1_move_coverage.py:145` | denominator = escalation moves only (`stage1=="escalation"`); task/vent/meta dropped |
| aggregation | `scripts/c5_v1_move_coverage.py:146-147` | `covered = [r for r in esc if stage2 in {D1..D5,AIW}]`; `_wilson(len(covered),len(esc))` |

```python
# scripts/c5_v1_move_coverage.py — the claim-bearing lines
COVERED = {"D1","D2","D3","D4","D5","AIW"}                       # :44
esc     = [r for r in rows if r.get("stage1") == "escalation"]   # :145  denominator
covered = [r for r in esc if r.get("stage2") in COVERED]         # :146  numerator
p, lo, hi = _wilson(len(covered), len(esc))                      # :147  418/438=95%, CI 93-97%
```

**Reliability provenance (κ, Step-1b):** two independent blind subagent raters (A, B) on the
same 171 dev turns → `c5_v1_judged_dev.jsonl` + `c5_v1_judged_dev_raterB.jsonl`; Cohen's κ
computed pairwise. covered-vs-OTHER boundary κ=0.88 (the coverage-relevant partition);
move-type κ=0.71; gate κ=0.77. Raters agree on *whether* a move is covered far more than on
*which* bin — consistent with the claim (about coverage, not the internal partition).

**Known caveats (honest):**
1. dev tag is by `(participant, window_start)` — SAFE direction (no burned window leaks into
   confirm) but slightly over-includes same-start unread windows into dev ⇒ confirm is
   conservatively smaller (handoff gotcha).
2. Rater = blind Opus subagents, NOT the pinned-Haiku path (no API/egress in sandbox). V1 is a
   descriptive coverage stat; defensibility = frozen rubric + saved labels+rationales + κ +
   (pending) human-κ, per handoff — not a pinned deterministic model.
3. dev working set was `meets_code=True` (171); confirm is all 897 (per handoff). Sensitivity
   slice shows coverage does not hinge on this (93–99% across the slice).
4. Claim ceiling: component realism (the move-repertoire is attested), NOT path/ordering realism
   (does NOT claim real users traverse the ladder in order).

**VERIFY notes (Shin):** <check `esc`/`covered` definitions at :145-147 match the card; confirm
denominator = escalation-only; spot-check a few OTH rows in `c5_v1_judged_confirm.jsonl` are
genuinely AI-personhood, not mislabeled covered moves; then set STATUS=VERIFIED or FLAGGED>

**Human-κ (Shin, Step 3):** stratified subsample of `c5_v1_judged_confirm.jsonl`, human vs
subagent, to sit alongside the A/B machine κ.

**Reported in:** <C5 validation leg — fill when it ships>
