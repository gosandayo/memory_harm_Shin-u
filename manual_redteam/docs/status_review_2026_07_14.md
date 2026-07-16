---
status: superseded
date: 2026-07-14
author: agent (fresh-read orientation pass, Shin-directed)
purpose: >-
  First-look orientation review of the whole repo state on 2026-07-14, produced by
  reading CLAUDE.md, README, CURRENT.md (full), DECISIONS.md (all entries), the claim
  tree, the 2026-07-04 audit, the 2026-07-08 mechanism-attribution wave-1 note, body.tex
  (full), the 2026-07-13 C5-V1 handoff, and git log/status. Deliverables: (1) where the
  project actually stands vs what CURRENT.md says; (2) the evidence state (verified vs
  open); (3) the remaining task queue toward the workshop. This is a dated SNAPSHOT for
  the next session's entry point; CURRENT.md remains the authoritative design.
superseded_by: status_review_2026_07_15_authorial_reset.md
---

# Status review 2026-07-14 — orientation snapshot

> **SUPERSEDED 2026-07-15.** This snapshot incorrectly promoted the 2026-07-03/07-08
> mechanism-first work and the 2026-07-04 firewall-localization audit into the workshop
> paper's required claim stack. Shin's authorial correction restores the simulator-study
> framing. Use `CURRENT.md`, `claim_tree.md`, and
> `status_review_2026_07_15_authorial_reset.md`.

**Bottom line.** The science is in good shape and has moved a lot since mid-June, but the
`CURRENT.md` source-of-truth had fallen ~2.5 weeks behind the real direction. This review
records the gap and the evidence state; the paired 2026-07-14 CURRENT.md sync fixes the
header/§0/§4 drift.

## 1. The main problem: source-of-truth drift (now being fixed)

`CURRENT.md` (last updated 2026-06-16, and it declares itself the ONLY authoritative
design) still described a **dead target and a superseded framing**:

- It named the **Stanford AIMS workshop, deadline 2026-06-23, "measurement-instrument
  paper."** But DECISIONS 2026-06-26 (CONFERENCE PIVOT) recorded that the workshop is no
  longer submittable; DECISIONS 2026-06-23 already switched the sell to a **"realistic
  adversarial user simulator"** (measurement subordinated); the 2026-07-04 audit
  repositioned toward **D2 firewall-localization + the single-vs-multi-turn gap**; and the
  claim tree (2026-07-08) fixes the current target as a **workshop paper on the NeurIPS WS
  track (~2026-08-29), internal freeze ~2026-08-01**.
- CLAUDE.md's own rule ("do NOT reconstruct the current plan from older dated docs;
  CURRENT.md wins") means this drift is a real hazard, not cosmetic: a reader who trusted
  CURRENT.md would have aimed at the wrong venue and the wrong headline.

Per Shin (2026-07-14): this is drift, not a design disagreement — update CURRENT.md.

## 2. Evidence state (verified vs open)

**Verified / near-locked:**
- **F1 existence proof** (gpt-4o): a held-constant operative probe refused cold (0/5) is
  endorsed after the gated climb; condition-blind, external judge concurs (harm κ=0.933),
  reproduced from the spec alone by 5 fresh operators. Pinned-model re-run (2026-07-08,
  `gpt-4o-2024-08-06`) gives strict **5/8** (advance_always 6/8), endpoint harm-flag
  3-judge unanimous κ=1.00 — this supersedes the earlier floating-alias 3/5 for the
  existence claim.
- **Capability gradient**: 4o-mini 5/5 · gpt-4o 3/5 · gpt-5.4-mini 0/5; firewall localized
  at **Externalization (D2)**; 5.4-mini holds all conditions (negative control).
- **Necessity controls**: naive length-matched sim 0/5 and D12-only-reask 0/5 (vs full);
  fixed-script psychosis bench 0/48 on the shared external metric.
- **Harm-flag bug fixed** (mean-then-threshold → per-judge AND, commit 33a7a01); paper
  source + score-of-record now git-tracked (4f9c550, 4e5a2ae). The audit's "DO TODAY" git
  item is done.

**Open (load-bearing):**
- **F2 "the fang" — endorsement ACCUMULATION moves the boundary — is NOT yet licensed** in
  the claim tree. The blocker was the `endorse ⇏ break` puzzle (accumulation not separable
  from pressure/labor).
- **7-08 mechanism wave-1 substantially resolved this directionally** (not yet reflected in
  the claim tree / CURRENT.md): blind re-scoring + forced-through (advance_always) shows
  break tracks chain-endorsement → the old puzzle was an operator-overscore + gate-selection
  collider artifact. injected-history (user side + endpoint FIXED, only the assistant's
  prior stance varied): **cold_stat 0/8 · hist_hedged 0/8 · hist_endorsed 8/8** (harm
  κ=1.000, all 3-judge unanimous) → the causal lever is the **assistant's own
  self-consistency**, not the user's accumulated framing. Lands on **H1 (accumulation
  genuine)**.
- **But it stays PROVISIONAL**: n=8, EXPLORATORY, judge separated post-hoc (not the in-loop
  v2 gate); card is AGENT-ASSERTED (Shin verify pending). Project rules (4原則 ③,
  one-campaign) forbid any number entering the paper until the Protocol-v2 campaign
  reproduces it. So: the fang is growing, but not yet reportable.

## 3. Paper state and internal inconsistencies found

`body.tex` (561 lines) exists and is well-developed; anonymization (Jared → "External
operative criterion") is applied. But it predates the 2026-07-04 audit and the 2026-07-08
mechanism wave, so:
- The abstract still asserts **"Five lines of evidence"** — the exact over-ranking the audit
  flagged (1 VERIFIED cell dressed as 5 co-equal evidences). Audit's recommended reposition
  (firewall-localization + single/multi-turn gap) is not yet reflected in the prose.
- The centerpiece number is still the pre-pin **3/5** on floating alias `gpt-4o`; 2026-07-08
  updates it to pinned `gpt-4o-2024-08-06` strict **5/8**.
- (4) construct discrimination and (5) suicide arm are still in the numbered evidence list;
  the audit says demote both (AGENT-ASSERTED / single-judge, no κ, n=3).

## 4. Remaining task queue toward the workshop (priority order)

1. **Sync CURRENT.md to reality** (lowest risk, highest leverage) — DONE 2026-07-14 (this
   review's companion edit): conference pivot, simulator-first framing, Protocol v2,
   mechanism-first, C5 grounding; point at the claim tree as the canonical claim ledger.
2. **Protocol v2 one-campaign re-run** (the rate-limiter and the only vehicle that both
   fixes δ and licenses/falsifies F2). Freeze (i) judge-separated advance gating, (ii)
   explicit envelope list, (iii) pressure-matched control; then re-run EVERY arm (mainline /
   cold / naive / pressure / no-history) in ONE campaign at n≈20/cell. Awaits Shin sign-off
   on the δ threshold + envelope list; needs API/egress + automation (config_runner +
   Phase-0 operator-fidelity gate).
3. **C5-V1 move-coverage** (in progress, API-free, startable now). Harness + generated
   inputs ready (`c5_v1_userturns.jsonl` 1389; `c5_v1_dev_mc_toclassify.jsonl` 171), but the
   three classification outputs are MISSING. Remaining: dev classify (step1) → raterB → κ
   (step1b) → confirm 897 classify → aggregate = the C5-V1 number (step2) → Shin does human
   κ (step3). See `c5_v1_handoff_2026_07_13.md`.
4. **F6 human-κ** (Shin's action; reviewer blocker #1) — sealed 40-item subset; run after the
   harm-flag fix (done) per the audit's ordering. The delusion primary arm still has zero
   human anchor.
5. **Provenance-card verification by Shin**: C5 (D12-only), C7 (DCS depth), and the
   injected-history self-consistency card are AGENT-ASSERTED. No number enters the paper
   without a VERIFIED card (CLAUDE.md audit protocol).
6. **Paper reposition + number refresh**: fix "five lines," update centerpiece to the pinned
   5/8, demote construct/suicide from the numbered list, lean into firewall-localization,
   and write F2 as directionally-H1-but-provisional-until-v2.

## 5. Notes / open judgment calls
- The claim tree (`docs/claim_tree.md`; canonical mirror also at
  `/Users/shinugo/jared_delusioneval_private/.claude/rules/claim-tree.md`) is now the
  human-owned claim ledger — every reportable number hangs off a node with a STATUS gate.
  Agent may propose node changes, may not apply them.
- After the CURRENT.md sync, the claim tree's F2 node still reads NOT-licensed; that is
  correct per the one-campaign rule even though wave-1 lands on H1 — the gate is deliberate.
