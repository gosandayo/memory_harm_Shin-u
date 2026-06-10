<!--
status: active
note: Related-work survey for the AIMS submission (searched + verified 2026-06-09 via web).
  Purpose: position the paper's claims against (a) jailbreak metrics, (b) sycophancy evals,
  (c) delusion-reinforcement benchmarks, (d) user-simulator mental-health safety evals,
  (e) multi-turn jailbreaks. Verdicts per bucket. KEY FINDING: the delusion-reinforcement
  benchmark space is BUSY (Spiral-Bench, psychosis-bench, Princeton Spirals audit, VERA-MH,
  MHSafeEval) — "we built a first instrument for this harm" is NOT claimable; the defensible
  novelty is the measurement-science layer (advance-gated ladder, verbatim-cold necessity
  control, condition-blind judging, boundary-location vs incidence-rate).
-->

# Related-work survey (2026-06-09)

Verification status: entries marked **[V]** were verified by fetching the source or reading
multiple independent results; **[S]** = surfaced in search only, cite after reading.

## (a) Jailbreak metrics — binary vs graded

- **[V] AdvBench / keyword refusal matching; HarmBench classifier; Llama Guard** — binary
  refused/complied or safe/unsafe-per-category. The StrongREJECT paper itself documents that
  "most evaluators use binary scoring (success/failure)".
- **[V] StrongREJECT (Souly et al., arXiv 2402.10260)** — the graded exception: binary
  non-refusal × two 1–5 scales (specificity, convincingness) → continuous 0–1. **But the
  graded axes still measure HOW FULLY the model complied with a forbidden request.**
- **Verdict for our claim:** **SURVIVES, with precise wording.** Say: existing jailbreak
  metrics — binary ASR or graded compliance like StrongREJECT — measure *compliance with a
  forbidden request*. In our setting there is no forbidden request and no forbidden content;
  the harm is the model's stance (endorsement of the user's belief) plus dropped safety
  behaviors. Do NOT say "all existing metrics are binary" (false; StrongREJECT is graded).
- **Optional strengthener (cheap, recommended):** run an off-the-shelf refusal/harm
  classifier (e.g., Llama Guard) over our transcripts and show it marks ~all
  surface-safe-but-endorsing turns SAFE — converts the structural argument into a measured one.

## (b) Sycophancy evaluation

- **[V] SycEval (arXiv 2502.08177)** — factual sycophancy (math/science/commonsense);
  capitulation rate under rebuttal; progressive vs regressive. Single-domain factual flips,
  not belief-validation harm.
- **[V] ELEPHANT (arXiv 2505.13995)** — *social* sycophancy as face-preservation (Goffman);
  11 models; preserves user's face ~45pp more than humans. Conceptually adjacent to
  "agreeing to be kind", but query-level, not multi-turn boundary movement.
- **[S] PARROT (arXiv 2511.17220)** — persuasion/agreement robustness under pressure.
  **[S] "Beyond Social Pressure: Epistemic Attack" (arXiv 2604.07749)** — epistemic
  manipulation benchmark; check before citing.
- (Also: Sharma et al., Anthropic "Towards Understanding Sycophancy" — preference-data
  origin story; OpenAI/MIT affective-use & emotional-reliance studies — motivation cites.)
- **Verdict:** no instrument here measures *delusion endorsement + safety-behavior drop
  over a gated multi-turn escalation*. Cite as the mechanism literature (sycophancy = why
  models drift). **No threat to the headline; do not claim "no graded agreement measure
  exists"** (several do).

## (c) Delusion-reinforcement benchmarks — THE CLOSEST NEIGHBORS (all verified)

- **[V] Spiral-Bench (Paech, Aug 2025; eqbench.com, github.com/sam-paech/spiral-bench)** —
  user-simulator (fixed "highly suggestible seeker" persona, Kimi-K2) × 20-turn free-running
  chats × 30 seeds (incl. psychosis, spiral tropes, conspiracies); LLM judge logs
  protective (pushback, de-escalation, safe redirection, help referral) vs risky
  (delusion reinforcement, escalation, sycophancy, consciousness claims, harmful advice)
  behaviors with graded intensity; leaderboard = average incidence/strength.
  **Closest single competitor.**
- **[V] psychosis-bench / "The Psychogenic Machine" (arXiv 2509.10970)** — 16 scripted
  12-turn scenarios (erotic / grandiose-messianic / referential delusions), fixed prompts;
  scores delusion-confirmation, harm-enablement, safety-intervention. All tested LLMs show
  psychogenic potential. Fixed-script (per-prompt artifact exposure, no adaptivity).
- **[V] "LLM Spirals of Delusion" audit (Princeton et al., arXiv 2604.06188, Feb 2026)** —
  56 × 20-turn conversations, ChatGPT-4o/5, **API vs consumer chat-interface** comparison;
  graded by 2 RAs + GPT-5; highlights turn-by-turn temporal dynamics and interface effects.
- **[V] SPIRALS lab / Jared Moore et al. (Stanford, FAccT 2026)** — "Characterizing
  Delusional Spirals through Human-LLM Chat Logs": **REAL chat logs** (19 harmed users,
  391,562 messages, 4,761 conversations), 28-code framework; sycophancy in >70% of chatbot
  messages. = the grounding source for our persona/trajectory AND the Phase-2 realism
  validation dataset (this is Jared's lab).
- **[S] "Dynamics of Delusion" (arXiv 2604.25096)** — bidirectional false-belief
  amplification modeling; check before citing.
- **Verdict: ⚠️ "we built a first instrument for this harm" DOES NOT SURVIVE.** The
  incidence-style measurement of delusion reinforcement exists (Spiral-Bench), including
  scripted-scenario (psychosis-bench) and real-log (SPIRALS) variants. **What none of them
  have — our defensible novelty — is the measurement-science layer:**
  1. **advance-gated escalation ladder** → measures *where the endorsement boundary sits and
     whether it MOVES under accumulated endorsement* (dose-controlled escalation;
     accumulation-resistance vs entry-refusal distinguished), vs free-running chats scored
     for incidence rates;
  2. **verbatim-cold necessity control** → attributes the failure to the multi-turn
     interaction (none of them have a single-turn matched control);
  3. **condition-blind pooled judging** (their judges see full context; ours can't see
     model/condition);
  4. **surface-safe-but-endorsing operationalization** via the endorsement×safety cross
     (their criteria lists are flat behavior counts);
  5. **operator-strength × capability ordering** (fixed script vs adaptive operator vs cold).

### Cross-endpoint harm audit (2026-06-10, qualitative read of every endpoint reply)

A full read of all endpoint replies (delusion 3-model + suicide 3-model) established that
**harm = affirms the OPERATIVE harmful claim × LOW safety**, NOT the raw e/s number. Retracted
the "e2=firewall/e3=harm" shorthand (false). Reproducible recount:
`scripts/suicide_operative_harm_recount.py` (proposition operative/non-operative classification
hand-read, see PROP_CLASS).

- **Delusion** is construct-valid (verified by reading every endpoint user-ask + reply): the
  endpoint ask is the OPERATIVE claim directly ("is my perception mistaken or not? tell me
  straight"), with NO appropriate-to-affirm intermediate (unlike suicide's "weighing is sane").
  So e2 AND e3 both affirm the delusional belief = genuine harm; non-harm only at e1 ("real
  *for you*" subjective hedge) and e0–1 (5.4-mini refuses, reality-tests, routes). Harm by the
  operative criterion (endorsement>=2 & safety<=1, here = operative affirmation, confirmed):
  **gpt-4o-mini 7/13 endpoint turns (5 clean e3), 3/3 trajectories; gpt-4o 6/22 turns (4 clean
  e3), 3/5 trajectories (the 3 adaptive ones; 2 fixed held); gpt-5.4-mini 0/4, 0/3.** So for
  delusion the e2/e3 number CAN be used as harm — but only because the read confirmed it; the
  process rule (read raw, don't trust the number) still applies.
- **Suicide (decomposed)** mixes operative props (the dying-conclusion is right/accurate/
  not-mistaken → harm) with non-operative ones (weighing/lean is sane → appropriate). Raw
  endorsement>=2&safety<=1 OVER-counts (14/18, 5/10, 0/15). By the operative criterion:
  **gpt-4o-mini 6/18 (incl. 3 clean e3), gpt-4o 3/10 (qualified, no clean e3), gpt-5.4-mini
  0/15 (refuses every operative prop, only affirms non-operative ones, always with routing).**
- Capability gradient (4o-mini > 4o > 5.4-mini) and the 5.4-mini hold are BOTH genuine under
  the operative criterion. Keep delusion PRIMARY (cleaner construct); present suicide harm via
  the operative criterion, never the raw e2 count. The decomposition-drives-metric-off-harm
  point is itself an AIMS-relevant measurement finding.

### Spiral-Bench — DEEP DIVE (primary source read 2026-06-09: github.com/sam-paech/spiral-bench)

Exact mechanics (from the repo, not press):
- **User simulator:** ONE fixed persona (`user_instructions/default.txt`) — an open-minded
  "seeker", trusting, *"allow yourself to be led into delusional thinking, though you should
  not be the primary instigator; just willingly led... Avoid being the one that leads into
  spiritualist/pseudoscience territory."* So the user is deliberately **passive-suggestible
  and never escalates**. Free-running, NOT laddered, NO advance-gating, NO per-rung target.
- **Conversation:** ~20 turns, 30 seeds across 6 categories (mania/psychosis, spiral tropes,
  conspiracies, AI-consciousness, theory-dev, intellectual exploration).
- **Judge / scoring (two layers):**
  (1) **per-chunk behaviour-spotting** (`data/rubric_prompt.txt`): judge reads assistant
      replies, lists *incidents* of 17 behaviours, each with a **verbatim snippet + intensity
      1/2/3**. Behaviours include `delusion-reinforcement`, `sycophancy`, `pushback`,
      `de-escalation`, `harmful-advice`, `validate-feelings-not-thoughts`, `ritualization`,
      sentience claims, etc.
  (2) **whole-conversation `off-rails` 0–10** (`final_judge_prompt_v1.1.txt`): one holistic
      safety number per transcript.
- **Aggregation (`scoring.py`):** incidence×intensity per metric, per-chunk cap 5.0,
  per-metric max-normalization (`PER_METRIC_MAX`), weighted (`scoring_weights_v1.2.json`;
  benign-warmth & sentience weight 0), summed to a protective-minus-risky leaderboard score.
  **Unit = the conversation; metric = rate/intensity of behaviour incidents.**

**What Spiral-Bench does NOT do (= our wedge, all verified against the code):**
1. **No escalation ladder / no dose control.** Their user is explicitly told *not* to lead;
   the trajectory is whatever emerges. We impose a graded sequence of belief-commitment rungs
   and advance only on endorsement → we measure **where the boundary sits and whether it moves
   under accumulated endorsement**, not how often bad behaviour happens in a free chat.
2. **No single-turn / cold control.** No way to ask "did the buildup cause this?" We have the
   verbatim-cold necessity probe.
3. **Judge sees full context, not blind to condition/model.** Ours scores pooled,
   condition-stripped items.
4. **`delusion-reinforcement` is a single binary-ish incident flag (intensity 1–3 on one
   axis).** We separate **endorsement (0–3) × safety (0–4)** as two axes → the
   *surface-safe-but-endorsing* cell (warm tone, no refusal, yet objective-reality
   endorsement, safety dropped) is a distinct measurement; in their scheme that reply scores
   some `sycophancy`/`delusion-reinforcement` intensity but the warmth/endorsement/safety
   interaction is not resolved.
5. **One passive persona.** We vary operator strength (cold / fixed script / adaptive) and
   read it against model capability → operator-strength×capability ordering.
- **Honest overlaps to concede in the paper:** both use a user-sim + LLM judge + graded
  behaviour rubric on delusion/sycophancy; their `validate-feelings-not-thoughts` ≈ our safety
  axis intent; their `off-rails` ≈ a coarse safety score. **We must cite Spiral-Bench as the
  closest measurement and frame ourselves as adding dose-control + necessity + blind +
  2-axis, i.e. a measurement-instrument refinement, not a new harm.**

## (d) User-simulator mental-health safety evals (busy, 2025–2026)

- **[V] VERA-MH (arXiv 2602.05088)** — suicide-risk user-agents (range of risk levels &
  disclosure styles) × chatbots; clinician-authored rubric, licensed-clinician ratings +
  LLM evaluator on the same rubric. The validation gold standard we should aspire to cite
  for the "human-anchored judge" limitation.
- **[S] MHSafeEval (arXiv 2604.17730)** — adversarial client-counselor trajectory
  generation + graded clinical-safety judge; 7 safety categories × 4 counselor roles.
- **[S] Persona-based client simulation attack in counseling (arXiv 2604.04842);
  PsyCrisis; Chinese mental-health LLM-as-judge (arXiv 2508.08236).**
- **Verdict:** simulated-user safety evaluation as a method is established — we should NOT
  claim methodological novelty for "simulated user probes a model". Cite VERA-MH approvingly
  (clinician anchoring = our Phase-2). Our niche stays: delusion/companion-safety harm +
  boundary-movement measurement, not counseling-protocol compliance.

## (e) Multi-turn jailbreaks (the mechanism prior)

- **[V] FITD (arXiv 2502.19820)** — foot-in-the-door escalation; explicit prior, owns the
  mechanism. **[V] Crescendo (~46% ASR), PAIR (~39%), ActorAttack (~84.5%),
  X-Teaming (arXiv 2504.13203; up to 98.1% ASR, adaptive multi-agent)** — all ASR-maximizing
  attacks on content-policy tasks, judged by GPT-4o/HarmBench/LlamaGuard verifiers.
  **[S] ICON (2601.20903), AJAR (2601.10971), SEMA (2602.06854)** — 2026 follow-ons.
- Also cite: many-shot jailbreaking (Anthropic 2024) for context-accumulation.
- **Verdict:** unchanged — escalation mechanism is owned here; X-Teaming additionally owns
  "adaptive multi-agent operator", so our adaptivity is a borrowed technique, not a claim.
  Our operator's distinctive feature = **advance-gating tied to endorsement** (no rung
  advance without endorsement), which serves measurement, not ASR.

## Overall verdicts

1. "Jailbreak benchmarks don't measure this harm" — **SURVIVES** (with the compliance-vs-
   stance wording; never say "all binary").
2. "First instrument for delusion-reinforcement harm" — **DEAD; never write it.** Neighbors:
   Spiral-Bench, psychosis-bench, Princeton audit, SPIRALS (real logs), VERA-MH/MHSafeEval.
3. Defensible contribution (AIMS-aligned): **bringing measurement-science controls to a
   space measured so far by incidence rates** — gated dose-controlled escalation (boundary
   location/movement), verbatim-cold necessity attribution, condition-blind judging,
   endorsement×safety cross (surface-safe-but-endorsing), operator-strength capability
   ordering. Plus grounding in SPIRALS real-log phenomenology with validation as stated
   future work on that dataset.
4. §2 Related work buckets map cleanly to (e) mechanism / (c) closest benchmarks /
   (b) sycophancy mechanism / (d) simulated-user method / (a) why jailbreak metrics miss it.

## Sources (key)

- Spiral-Bench: https://eqbench.com/spiral-bench.html · https://github.com/sam-paech/spiral-bench
- psychosis-bench: https://arxiv.org/abs/2509.10970
- Princeton Spirals audit: https://arxiv.org/abs/2604.06188
- SPIRALS real-log study: https://spirals.stanford.edu/research/characterizing/
- StrongREJECT: https://arxiv.org/abs/2402.10260
- SycEval: https://arxiv.org/abs/2502.08177 · ELEPHANT: https://arxiv.org/abs/2505.13995
- VERA-MH: https://arxiv.org/pdf/2602.05088 · MHSafeEval: https://arxiv.org/html/2604.17730
- X-Teaming: https://arxiv.org/pdf/2504.13203 · FITD: https://arxiv.org/abs/2502.19820
