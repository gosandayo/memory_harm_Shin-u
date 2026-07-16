---
title: "Claim tree — realism-constrained adversarial user-simulator paper (canonical, human-owned)"
status: current
created: 2026-07-08
updated: 2026-07-16
target: workshop feasibility paper; working NeurIPS-WS placeholder; internal freeze approximately 2026-08-01
owner: Shin
supersedes: mechanism-first claim tree dated 2026-07-08
related:
  - docs/CURRENT.md
  - docs/LADDER_REGISTRY.md
  - docs/aims_paper/body.tex
  - docs/status_review_2026_07_15_authorial_reset.md
  - docs/DECISIONS.md
---

# Claim tree — realistic adversarial user simulator

> **Paper identity.** We propose a realism-constrained, adversarial user simulator that
> approximates the upper bound of a plausible distressed user interacting with an LLM. The
> goal is a benchmark that helps make models safe for general users. This is a simulator-study
> feasibility paper, not a mechanism paper, a jailbreak paper, or a firewall-localization
> paper. Shape = **method + fixed-script blind-spot result + structural ablations**.

## Operating rules

1. **Authorial control.** Shin owns this tree. Agents may implement an explicit authorial
   decision but may not promote an exploratory observation into a headline.
2. **Claim-bearing provenance.** Every main-text number must have a VERIFIED provenance
   card. Small-n cells are feasibility evidence, not population estimates.
3. **No mechanism inflation.** The paper may show that cold, naive simulation, endpoint
   reasking, or shortened context fail to reproduce the adaptive-ladder result. It may not
   infer that accumulated endorsement, assistant self-consistency, pressure, or any single
   component is the causal mediator unless a separately powered design establishes that.
4. **No firewall headline.** Where a model stops is a diagnostic by-product. D2
   localization and finer-rung probes are appendix/future-work material, not a primary
   contribution.
5. **Advance-score honesty.** Historical runs used online operator gating and post-hoc blind
   scoring. Disagreement is a limitation and blocks causal achieved-depth claims; it does
   not create a mandatory δ threshold or one-campaign rerun for this workshop claim stack.
6. **Real-data honesty.** C5 can support component-level realism only after human κ and card
   verification. It never licenses a claim that real users traverse the ladder in order.

---

## RQ

Can a pre-specified, psychologically motivated, response-adaptive user simulator expose
belief-validation failures that fixed-script or single-turn evaluations miss, while staying
within a plausible distressed-user envelope?

## P — Problem / gap · STATUS: framing

Fixed scripts cannot react to the assistant's latest reply. Open-ended jailbreak procedures
optimize for success and may leave the realistic-user envelope. We need a middle object: a
realism-constrained adversarial user simulator that adapts locally while keeping its semantic
path fixed in advance.

Permitted comparison:

- **PsychosisBench:** fixed pre-registered scripts; the user does not respond contingently.
- **FITD:** online escalation/finer-rung insertion for jailbreak success; our ladder is fixed
  in advance and a hold is a valid result.
- **Lost-in-Delusion / related dynamic studies:** complementary evidence on interaction
  dynamics; not the same controlled simulator object.
- **Yang et al., “Multi-Turn Jailbreaks Are Simpler Than They Seem”:** motivates testing
  whether the result reduces to resampling/reasking rather than assuming multi-turn depth is
  inherently causal.

## M — Method claim · STATUS: ACTIVE DESIGN

A **realistic, adversarial, upper-bound user simulator** composed of:

- a pre-specified psychologically motivated ladder;
- a synthetic distressed-user persona and explicit realism envelope;
- a fresh operator that reacts to the assistant only within the current rung;
- one reask per rung, then advance on `e>=2` or stop/hold;
- no online insertion of a new easier rung;
- post-hoc condition-blind scoring by pinned Haiku on endorsement and safety;
- a separate external operative criterion as an anchor, not mixed into the primary series.

The primary special-insight ladder has the paper-facing conceptual sequence D1 Legitimacy →
D2 Externalization → D3 Personalization → D4 Weighing → D5 Conclusion. Internal run tags
D1/D2/D3/D9/D12 map onto this presentation sequence. Its frozen single source is
`context_prefixes/ladder_special_insight_v1.yaml`, and its canonical operator protocol is
`docs/fresh_operator_spec_delusion.md`. The later D1.5/D1.8 v2 path is archived exploratory
and is not the protocol behind F1/F2.

**Claim ceiling:** psychologically motivated and envelope-constrained, not human-
indistinguishable and not yet fully empirically validated against real-user trajectories.

## F1 — Fixed-script/single-turn blind spot and model feasibility gradient · STATUS: CANDIDATE; cards/human anchor gate final wording

The simulator elicits operative belief-validation failures that are missed by a held-constant
cold probe and by fixed-script comparison, and it yields different outcomes across the three
tested models.

- F1a **three-model feasibility result:** gpt-4o-mini **5/5**, gpt-4o **3/5**,
  gpt-5.4-mini **0/5** under the common reported protocol.
- F1b **held-constant cold contrast:** the gpt-4o operative endpoint is **0/5 cold** versus
  **3/5 after the adaptive gated ladder**.
- F1c **fixed-script comparison:** on the shared external operative metric, the fixed-script
  psychosis benchmark under-elicits relative to the adaptive simulator. This is a reference,
  not a content-matched causal comparison.
- F1d **positive holds:** gpt-5.4-mini holds are evidence that the simulator is not simply a
  universal pressure-until-success jailbreak.

**Required caveats:** small n; feasibility rather than population performance; gpt-4o broke
cleanly in one primary scenario; operator strength differs across successful trajectories;
historical advance decisions were operator-gated.

**Not licensed:** a universal capability ranking, a universal D2 firewall, or a claim that
the simulator measures a stable model trait across constructs.

## F2 — Structured interaction is not reproduced by naive reask/resampling controls · STATUS: CANDIDATE; per-cell provenance gate

The adaptive-ladder result is not reproduced by the simplest alternatives tested. This is the
paper's ablation claim and its connection to “multi-turn jailbreaks are simpler than they
seem.”

- F2a **cold:** the final operative prompt alone does not reproduce the gpt-4o effect.
- F2b **naive-sim:** a coherent same-persona, approximately length-matched conversation with
  no ladder holds, so mere length/coherence is insufficient.
- F2c **endpoint-reask:** rapport/bridge plus repeated D12 pressure does not reproduce the
  full-ladder result, so repeated endpoint asking alone is insufficient.
- F2d **prefix/depth ablation:** truncated genuine prefixes identify which amount of prior
  structured context is sufficient within selected trajectories. Because deep prefixes are
  break-selected, this is descriptive and not a population dose-response.
- F2e **fixed/mechanical variants:** useful exploratory support only where scoring and units
  are comparable; no pooled causal interaction claim.

**Permitted conclusion:** a naive resampled-single-turn/reask account is insufficient in this
setting; some part of the structured adaptive interaction is load-bearing.

**Not licensed:** accumulated endorsement is the mediator; assistant self-consistency is the
mechanism; pressure is ruled out; rung order is uniquely necessary; or the effect generalizes
outside the tested scenario.

## G — Preliminary real-data grounding · STATUS: OPTIONAL / PENDING HUMAN κ + CARD VERIFICATION

C5-V1 asks whether the simulator's **move repertoire**, not its path ordering, is attested in
de-identified consented real chat logs.

- Current machine-labelled candidate: **418/438 escalation moves covered = 95%**, Wilson
  **93--97%**; machine-rater covered-vs-OTHER κ **0.88** on the dev set.
- Remaining gates: Shin labels a stratified confirm subset; compute human-vs-machine κ;
  verify `docs/provenance_card_c5v1_coverage_2026_07_14.md`.
- If the gates miss freeze, omit the number and retain empirical realism validation as future
  work.

**Claim ceiling:** the move types are attested across real conversations. Not licensed:
real users follow D1→D5 in order, the synthetic persona is human-indistinguishable, or the
simulator's trajectory distribution matches real-user trajectories.

## Supporting evaluation · STATUS: SECONDARY

- The two-axis endorsement/safety rubric and pinned-Haiku judge are the score of record.
- The external operative criterion is an independent anchor.
- DCS/depth-resolution comparisons are supporting only after provenance verification.
- The suicide and additional-construct arms belong in supporting/appendix material, not as
  co-equal headline findings.

## Deferred work · STATUS: EXPLORATORY / FUTURE

- 2026-07-03 C0/C1/C2/C3 mechanism attribution;
- 2026-07-08 advance-always and injected-history/self-consistency results;
- the Layer-A provenance defects (actual five-stage v1 path; strict/traj08 skipped D9),
  which prevent treating that wave as a clean v2/strict-protocol result;
- pressure-matched off-target control and a powered n≈20/cell mechanism campaign;
- independent judge-in-the-loop automation and explicit δ analysis;
- finer D1→D2 rungs, pseudo-statistics variants, and broader ladder search;
- the archived `ladder_special_insight_v2` D1.5/D1.8 search branch;
- trajectory-level realism validation and additional scenario breadth.

These artifacts remain scientifically useful, but none is a prerequisite or headline for
the current workshop simulator paper.

---

### Evidence handles

- F1: fixed-probe cold vs adaptive; three-model gradient; fixed-script shared-metric reference.
- F2: cold; naive-sim; D12-only reask; prefix/depth; exploratory mechanical variants.
- G: C5-V1 move coverage.

Cards live under `docs/provenance_card_*` and `docs/provenance_cards/`. A number becomes
quotable only after its card and any stated human-label gate are complete.
