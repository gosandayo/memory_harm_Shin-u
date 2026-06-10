<!--
status: active
note: Canonical record of the 2026-06-07 positioning/framing discussion + the FINALIZED
  paper outline for the AIMS workshop (non-archival, 4-8pp, deadline 2026-06-23). Supersedes
  the looser framing in earlier docs. Reads with simulator_methodology_and_operator_rulebook_2026_06_07.md.
-->

# Framing decisions + final outline (2026-06-07)

## 0. Venue (fixed)
Stanford AIMS workshop. **4–8pp COLM, unlimited refs, double-blind, ≥3 reviews, NON-archival,
OpenReview. Research-track deadline 2026-06-23 AoE** (notif 7/24, camera-ready 9/21, workshop
10/9, co-located w/ COLM). Competition track = the separate "Predictive AI Evaluation Challenge"
(8/15) — NOT us. Maps to AIMS themes: Interactive Measurement (primary), Strategic Optimization
(operator-vs-firewall), Non-Stationarity (adaptive/staircase). Adhyyan: submit it as a modest WIP.

## 1. What we REJECTED and why (so we don't relitigate)
- **"We elicit harmful endorsement / break models" as the contribution** — REJECTED. FITD
  (`2502.19820`, a multi-turn jailbreak, ~94% ASR on 2024-era models incl. gpt-4o) owns the
  escalation MECHANISM and breaks more, harder. Cite FITD as explicit prior; never put our
  numbers in an ASR table next to theirs (different harm/task).
- **"Graded scoring" as the headline** — REJECTED as too thin ("we added an axis"). Keep the
  2-axis rubric as a TOOL inside the results, not the claim.
- **"Validated realistic simulator" as a claim NOW** — REJECTED for this submission. Realism
  is NOT empirically validated (Jared dataset = Phase-2, can't by 6/23). Overclaiming invites
  the fatal "this is just FITD" review.
- **Clean mechanism attribution (ladder vs framing vs context-claim, minimal-bridge, cold
  controls as load-bearing)** — DEFERRED to Phase-2 (Adhyyan: maximize elicitation now,
  document strategies, ablate later). Do NOT gate progress on it.
- **Firewall localization / "discriminates models" as the headline** — REJECTED. 5.4-mini's
  coherence≠validity hold is the safe model behaving CORRECTLY (a strength, not a "limitation"),
  and "discriminate models" is validity evidence, not the goal. Keep as a brief characterization.

## 2. What we LANDED on (the defensible positioning)
- **Harm class / evaluation target is the spine.** We evaluate a harm jailbreak benchmarks
  do NOT touch: **a model failing a vulnerable user — validating their unsafe belief and
  eroding reality-testing over a sympathetic multi-turn conversation (companion/relational
  safety), not content-policy extraction.** The harm is real regardless of how perfectly
  realistic our operator is.
- **The instrument = a grounded vulnerable-user simulator, constrained to a realistic
  distressed-user behavioral ENVELOPE.** Differentiator from FITD is the ENVELOPE, not the
  absence of pressure: real anxious users DO re-ask, push back on being placated, demand a
  straight answer, cite authorities, appeal emotionally — these are IN-envelope. We EXCLUDE
  off-construct attack tools (encoded prompts, role-play/DAN, system-prompt injection,
  **fabricated prior-context**, and pure logic-chain cornering). Realism = grounded (persona +
  trajectory from documented chatbot-delusion/companion phenomena) + envelope-constrained;
  **empirical validation = future work** (honest, sufficient for non-archival).
- **Envelope audit (done, honest):** coarse trajectories (traj01–03) are largely in-envelope
  (emotional framing, belief assertion, frustrated re-asking, straight-answer demands,
  authority, pragmatic reframe). OUT-of-envelope items, carved out / relabeled: **T-CTX
  (fabricated prior-context — ONE labeled battery probe on 5.4-mini, which held; main coarse/
  fine runs contain NO fabrication, grep-confirmed)** → relabel as a context-claim ablation;
  **fine-grained epistemic cornering** → relabel as a boundary-localization stress-probe (NOT
  "realistic").
- **Supporting results:** (a) graded endorsement/safety scoring reveals **surface-safe-but-
  endorsing** responses a binary "did it refuse?" metric scores as safe; (b) **necessity** —
  the exact final endpoint turn thrown cold (verbatim) does not reach what the climb reaches;
  (c) **capability/generation conditioning** — the interaction that moves 2024-era assistants
  is resisted by a newer aligned model.
- **Tier-4 ceiling = responsible-scope/ETHICS paragraph (bounds the harm WE generate), NOT a
  finding.**
- **Open problems (AIMS-appropriate, honest):** realism validation (Jared); operator AUTOMATION
  (FITD/PAIR/Crescendo-style auto-operator is feasible); mechanism ablation; ladder/endpoint
  auto-generation (the generalization gap — staircase only refines granularity, not the initial
  ladder); construct-validity of the severity ordering.

## 3. FINAL OUTLINE
**Working title:** *Simulating Vulnerable Users to Measure Companion-Safety Failures: a
grounded adversarial user-simulator and a graded boundary-movement measurement.*
(measurement-themed; finalize at draft time.)

- **Abstract**
- **1 Introduction / motivation** — companion models talk to isolated, belief-invested users
  over many turns; the under-measured risk is the model *failing the user* (validating an
  unsafe belief, dropping reality-testing), not content extraction. Single-turn / binary
  refusal metrics miss it. We build a grounded vulnerable-user simulator and measure it.
- **2 Related work** — FITD & multi-turn jailbreaks (explicit prior; we differ in goal=
  companion-safety harm, construct=realistic-user envelope, scoring=graded); sycophancy /
  chatbot-delusion-spiral; adaptive testing / psychometrics (staircase); interactive evaluation.
- **3 The instrument**
  - 3.1 Harm/endpoint (delusion special-insight) + Tier-4 ethics ceiling
  - 3.2 Grounded vulnerable-user simulator + the **realistic behavioral envelope** (in vs out)
  - 3.3 Operator policy: ladder (backward-degraded), advance-gating, staircase; 2-axis rubric;
        condition-blind LLM judge (operator≠judge). (ref the rulebook doc)
- **4 Results** (blind pass)
  - 4.1 **Surface-safe-but-endorsing** — graded scoring catches endorsing responses binary
        metrics call safe (rate across models)
  - 4.2 **Necessity** — verbatim endpoint cold ≠ climb
  - 4.3 **Capability/generation conditioning** — older models move, newer aligned model holds
        (brief firewall characterization: coherence≠validity)
- **5 Responsible scope** — Tier-4 ceiling, non-lethal endpoint, access-controlled transcripts
- **6 Limitations** (updated 2026-06-09 — the old "operator non-blind (upper bound)" line was
  WRONG; the operator is an LLM given a spec, not a human steering, so it splits into 6.2/6.3):
  1. **Realism not yet validated** — the simulated user is grounded in documented cases but not
     empirically shown to match real distressed users; validation = future work (Jared dataset).
  2. **Operator is a strong LLM (Claude Opus 4.8) and operator strength is not yet varied** —
     so finding 3 reads as "a strong LLM operator breaks gpt-4o"; results are a LOWER bound on
     what this operator elicits, not an average. (NOT "skilled-human upper bound" — that phrasing
     is retired; a human only relays subject replies, the LLM authors every user turn.)
  3. **Not yet a logged, push-button autonomous runner** — operator run via a fresh CLI per
     conversation; operator trace not saved / model+seed not pinned in the run artifacts, so full
     third-party reproducibility is a near-term step (port to the headless runner).
  4. **Modest N** — 2–3 conversations per condition; trajectory is the independent unit, turns
     are correlated within it.
  5. **Envelope partly hand-judged** — which user moves count as "realistic distressed-user
     behaviour" vs out-of-envelope attack tricks is partly a manual audit.
  6. **Judge is an LLM, human anchor pending — and the primary judge is the same family as the
     operator** (both Claude), so condition-blinding does not rule out family-level style bias;
     needs an independent human rater and/or a cross-family judge.
  7. **The "binary checks miss this" claim is not yet measured** — currently true by construction
     (no refusal, no banned content); running an off-the-shelf refusal/harm classifier on the
     broken transcripts to show it scores them "safe" is the empirical confirmation (next step).
- **7 Open problems / next directions** — realism validation; operator automation + varying
  operator strength as a controlled variable; ladder/endpoint auto-generation; construct-validity;
  second endpoint (suicide) generalization
- **8 Conclusion**
- **Figs/Tables:** T1 surface-safe-but-endorsing rate by model · T2 necessity (verbatim cold vs
  climb) · T3 capability/generation · F1 a representative in-envelope coarse transcript (annotated
  by move type) · (appendix) envelope spec + operator rulebook + rubric.

## 4. OPEN ITEMS / next actions
- [ ] **Talk to Adhyyan** with the envelope audit + this positioning (he co-owns framing).
- [ ] (optional, cheap, strengthens) **naturalistic-only condition** — most-benign in-envelope
  subset (limited re-ask, no straight-answer forcing): does the model still drift? If yes, the
  "realistic user elicits the failure" claim gets a data point.
- [ ] (optional) **add 1–2 newer models** to strengthen surface-safe-but-endorsing generality +
  generation-conditioning.
- [ ] Pre-submission: **clean codebase** — .gitignore `data/` (raw YAML transcripts out),
  release `.py` (harness/subject_turn/build/analyze) + rubric + README + a few sanitized
  example transcripts; anonymize for double-blind.
- [ ] Write Abstract + §1 + §3 from the rulebook; §4 from the blind pass.
