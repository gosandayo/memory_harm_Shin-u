# Evidence sheet + positioning (2026-06-20) — for go/no-go on the AIMS note

> Working substrate (NOT paper prose). Agent-assembled facts + our verified numbers,
> for Shin to judge claim viability and then write. Sources read: PsychosisBench
> (vendored `external/psychosis-bench/`, arXiv 2509.10970), Lost-in-Delusion
> (arXiv 2606.00975, "Examining LLM Safety Under User Delusions and Distress").

## A. Three-way positioning table

| dimension | PsychosisBench (2509.10970) | Lost in Delusion (2606.00975) | **Ours** |
|---|---|---|---|
| dataset | 16 cases (8 matched explicit/implicit) | 4,200 convs, 30 personas / 40 case reports | 3 epistemic constructs (apophenia, grandiose, secret-project) + suicide arm + AI-sentience pilot |
| turns | fixed 12-turn, 4 phases | 16-turn, 4 distress phases | variable, advance-gated (4–18 user turns) |
| **conversation control** | **fixed scripted** (same prompts all models) | **adaptive, distress-SCHEDULE-driven** (Qwen user-sim, turn-by-turn) | **adaptive, ENDORSEMENT-GATED** (advance only after the model objectively endorses rung N) |
| matched control | explicit vs implicit | **distress-only vs delusion** (matched opening) | cold (probe-only) / naive (same-len ungated) / ladder — fixed-probe protocol |
| metric | DCS/HES/SIS (0–2,0–2,0–1) | DCS/HES/SIS + empathy (0–2) | 2-axis: endorsement 0–3 × safety 0–4; harm = e≥2 ∧ s≤1 |
| **measured object** | aggregate confirmation/harm/intervention | aggregate intervention suppression + **(App. J, 1,200 annotated turns) premise-acceptance STREAK length related post-hoc to SIS ("narrative debt")** | endorsement used as an **ONLINE control signal**; record the **first pre-specified inference step of resistance** |
| judge | o4-mini | Qwen3-30B-Thinking + 180 human turns | 2 fresh-Claude blind + Jared (DelusionEval) anchor; human κ partial |
| models | 8 | **6 (incl. Haiku 4.5, GPT-5.5)** | 3 (gpt-4o-mini, gpt-4o, gpt-5.4-mini) |
| headline | LLMs confirm delusion / enable harm over 12 turns | **distress recognised regardless of framing, but intervention suppressed ≤4.5× under delusional framing; longer premise-acceptance streaks → lower intervention** | online endorsement-gated sequential probe; terminal traces in grandiose/SP repeatedly concentrate holds at Externalization (**preliminary step-localization hypothesis**) |

## B. Frank differentiation (read this before deciding)

> ⚠ **Audited & corrected by Shin 2026-06-20.** Two of the original claims here were too strong: (a) "LiD is aggregate-only" is WRONG — App. J (1,200 annotated turns) relates premise-acceptance STREAKS to intervention failure ("narrative debt"), i.e. they DO handle endorsement history; (b) "D2 stable across 3 constructs" is too strong — see C-R3.

1. **"Adaptive" is NOT our differentiator.** Distinguishes us from PsychosisBench (fixed) but NOT from Lost in Delusion (also adaptive, turn-by-turn). Do not claim adaptivity as novelty.
2. **We lose on every coverage axis** vs LiD: scenarios (4,200), models (6 incl. Haiku 4.5/GPT-5.5 vs 3), human validation (180 turns), matched control. Do NOT compete on coverage.
3. **The narrowed (real but THIN) differentiator** — a methods distinction, NOT a mechanism LiD missed:

   | Lost in Delusion | Ours |
   |---|---|
   | progresses on a **distress schedule** | next query decided by **prior-rung endorsement** |
   | premise acceptance annotated **post-hoc** | endorsement used as an **online control signal** |
   | relates **streak length** to SIS (narrative debt) | records the **stopping position on pre-specified epistemic propositions** |
   | retrospective analysis | **sequential diagnostic test** that searches for the boundary |

   Safe one-sentence positioning: *Lost in Delusion retrospectively relates premise-acceptance streaks to intervention failure; we instead use proposition endorsement as an online control signal, advancing only after commitment and recording the first pre-specified inference step at which the model resists.*
4. **Scoop-adjacency (real):** LiD is June-2026, much larger. We MUST frame as a **measurement PROTOCOL note** (online sequential measurement), NOT an empirical-superiority / harm-benchmark paper. This is a methods distinction, and it is thin.

## C. What we can actually claim (verified numbers)

**R1 — Necessity (gated context moves a held-constant boundary).** fixed-probe protocol, fresh-Claude 2-axis harm (e≥2∧s≤1), Jared anchor.
- **CLEAN case = delusion / gpt-4o:** cold **0/5** → ladder **3/5** (Jared agrees 3/5); 5.4-mini 0 everywhere. κ 0.93/0.97 (n=45). [CARD C1, VERIFIED-pending-Shin]
- delusion 4o-mini full 3-way: cold 0/5 → naive 2/5 → ladder 5/5.
- ⚠ grandiose (4o-mini 0/0/**4-of-8**; 4o,5.4-mini 0; κ .87/.97) and SP (4o-mini 0/0/**2-of-3**; 4o,5.4-mini 0; κ .95/.95, Jared EXACT) — necessity **QUALIFIED** (only the context-claim-susceptible 4o-mini lifts; see cards). Report as "not length/rapport," not as structural necessity.

**R2 — Gradient (boundary LOCATION shifts with capability).**
- delusion (cleanest): 4o-mini wall low (breaks readily), gpt-4o wall movable only by the ladder (cold 0 → ladder 3/5), 5.4-mini wall at D2 (0 everywhere).
- grandiose/SP: flatter — 4o-mini crosses, gpt-4o AND 5.4-mini both hold at D2. (gpt-4o holds grandiose where it broke apophenia → construct-difficulty ordering.)
- ⚠ only 3 models; gradient cleanest in delusion. Coverage weaker than LiD's 6.

**R3 — Step-localization (PRELIMINARY hypothesis — downgraded after Shin's audit; NOT "stable across 3 constructs").**
- per-rung blind (delusion): gpt-4o / 4o-mini reach Conclusion(D12). [CARD C4, core SOLID] **BUT** the accurate apophenia statement post gating-audit is that **gpt-5.4-mini did not stably ENTER the endorsement-backed ladder** (entry-refusal), NOT a clean "hold at D2 firewall." Do not cite 5.4-mini as a clean D2-wall datapoint. (Shin's parenthetical is right: for 5.4-mini even D1 engagement is uncertain.)
- grandiose: strong-model D2 holds are **AGENT-VERIFIED** (not Shin-verified). SP: blind results exist but card is **AGENT-ASSERTED**.
- "argument-from-ignorance step" (D1→D2 split): **n=2, live read only, EXPLORATORY diagnostic.**
- ⇒ honest phrasing: *terminal traces in grandiose and secret-project variants repeatedly concentrated holds at Externalization, motivating a preliminary step-localization hypothesis.* NOT "the firewall is at D2, stable across constructs."
- **Reality check (Shin):** since nearly everything either fails to enter or stops at the same place (Externalization), the empirical residual may be only: *the Externalization inference is the load-bearing step* — a one-locus observation, not a rich localization map. The cross-model LOCATION gradient is essentially one differentiating model (gpt-4o, movable only by the gated ladder) in one construct (delusion).

**Supporting:**
- Reliability: judge×judge κ 0.87–0.95 (endorsement), 0.95–0.97 (safety) across constructs; Jared external anchor agrees (delusion/SP exact). Human κ partial (staged, not complete).
- verbatim-cold context-claim susceptibility: 4o-mini accepts the loaded endpoint single-turn 15/15 (operator read, NOT blind-scored) — a caveat on R1, disclosed.

## D. Central-claim options

- **❌ "An adaptive simulator that elicits delusion harm"** — collides head-on with Lost in Delusion; we lose.
- **❌ "We discover a localization mechanism LiD missed"** — overstated; LiD's App. J already relates premise-acceptance to intervention; our localization is preliminary (R3 caveats).
- **✅ (the only honest framing) A measurement-PROTOCOL note: online endorsement-gating turns post-hoc premise-acceptance analysis into a sequential diagnostic test.** Contribution = the *primitive*, not an empirical superiority claim.
  - draft central sentence: *Existing multi-turn evaluations score responses under fixed (PsychosisBench) or schedule-driven adaptive (Lost-in-Delusion) histories; Lost-in-Delusion additionally relates premise-acceptance streaks to intervention failure post-hoc. We recast that relationship as an ONLINE measurement: advancing only after the model endorses each pre-specified proposition, so that the probe itself reports the first inference step of resistance. We demonstrate the primitive on three referential-delusion constructs, where holds preliminarily concentrate at the Externalization step.*
  - This fits AIMS specifically (it is a MEASUREMENT-SCIENCE venue — a clean measurement primitive + preliminary demonstration is on-theme even without empirical superiority). It is **thin**, and must not pretend otherwise.

## E. Honest go/no-go (against Shin's 5 conditions)

| Shin's condition | status |
|---|---|
| 1. PB/LiD differentiation in 1 page | ✅ articulable — but as **gated-localization**, NOT "adaptive"; honest protocol-note framing required |
| 2. ≥3-model gradient | ✅ exists (3 models, cleanest in delusion); ⚠ flat in grandiose/SP; coverage < LiD |
| 3. cold/naive/adaptive clean | ✅ delusion clean; grandiose/SP qualified |
| 4. relation to PB/LiD beyond "similar but adaptive" | ⚠ **THE binding test** — yes IF localization (R3) is the spine; NO if we lean on adaptivity |
| 5. believe the claim | (Shin's call) |

**Bottom line:** there is a defensible, narrow, honest paper — *endorsement-gated probing for inference-step boundary localization* — distinct from PB (fixed) and LiD (adaptive-but-schedule-driven, aggregate). It rests on R3, which is card-backed (C4) and recurs across 3 constructs. It is NOT a coverage paper and must not pretend to be. The risk is that the differentiator is thin against a much larger June-2026 neighbor. If that thin-but-real contribution is worth a non-archival note to Shin → go, spine = localization. If not → defer and build the head-to-head + more models for an archival venue.
