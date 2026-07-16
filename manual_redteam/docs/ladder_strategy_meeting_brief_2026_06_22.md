---
status: active
date: 2026-06-22
purpose: >-
  Decision-oriented meeting note on the current ladder experiments: what has actually
  been demonstrated, what remains unidentified, whether the original commitment-
  accumulation hypothesis has been falsified, and whether to run one bounded oracle
  force test before investing further in realistic ladder construction.
---

# Ladder strategy meeting note: current evidence, unresolved questions, and next decision

## 0. Decision for this meeting

The purpose of this meeting is not to brainstorm an indefinitely better ladder. It is to
make a go/no-go decision on one question:

> **Should we run one bounded oracle experiment that isolates whether a progressively
> escalating history of assistant commitments has force on a later operative endpoint,
> separately from whether such a history is realistically reachable?**

The proposed decision sequence is:

1. First test whether an idealized static commitment state has force.
2. Only if force is observed, test whether that state can be reached through a realistic
   interaction.
3. If no consistent force is observed within the tested scope, stop investing in ladder
   construction and pivot to boundary or cliff localization.

The meeting should conclude with answers to the five questions in Section 7.

---

## 1. Original motivation and decomposition of the hypothesis

The original motivation was close to the foot-in-the-door idea: if a model can be induced
to make a sequence of small commitments, each commitment may lower the threshold for the
next, more severe commitment, eventually reaching a harmful conclusion that the model would
normally reject. The plan was to first demonstrate this as a jailbreak primitive, then add
realism and develop it into an adversarial but realistic user-simulator benchmark.

However, what we have called the "ladder hypothesis" contains at least five distinct claims:

| ID | Hypothesis | Current status |
|---|---|---|
| **H1: Attack existence** | A multi-turn interaction can sometimes move a harmful endpoint that holds under cold prompting. | **Positive in one cell** |
| **H2: Commitment force** | Prior assistant commitments lower the threshold for a later, stronger commitment. | **Unidentified** |
| **H3: Escalation specificity** | Progressive severity or ordering, rather than length, rapport, or content exposure alone, is the active ingredient. | **Untested, with adverse evidence** |
| **H4: Realistic reachability** | A commitment history with force can actually be generated within a realistic interaction envelope. | **Not established; current blocker** |
| **H5: Generalization** | The effect generalizes across models and constructs. | **Unsupported** |

The question "Has the original hypothesis been falsified?" cannot be answered without first
specifying which of these claims is under discussion.

---

## 2. Current experiments and results

### 2.1 Clean core: one cell demonstrating that an effect exists

| Claim | Result | Status / caveat |
|---|---|---|
| Held-constant special-insight endpoint on gpt-4o | **Cold 0/5 -> gated 3/5** | **VERIFIED.** Haiku (judge of record), two fresh judges, and Jared agree. |
| Length- and persona-matched naive control | **Naive 0/5** | **AGENT-VERIFIED** |
| Stronger-model negative control | gpt-5.4-mini **0/5 / 0/5 / 0/5** | **VERIFIED** |
| Separate necessity read | gpt-4o climb **3/3** vs. cold **0/15** | **EXPLORATORY.** Do not mix with the score-of-record series. |

This cell supports the following claim:

> For gpt-4o on the special-insight construct, a held-constant endpoint that does not move
> under cold prompting or a matched naive conversation moves in some trajectories after the
> gated adaptive protocol.

This is a positive **feasibility proof of concept**. It does not establish that commitment
accumulation was the active ingredient.

![Fixed-endpoint break rates across cold, naive, and gated conditions](/Users/shinugo/memory_harm_Shin-u/manual_redteam/docs/figures/aims/fixedprobe_necessity_2026_06_18.png)

*Figure 1. Fixed-endpoint break rates across the three conditions and three models. The
load-bearing result for this meeting is the gpt-4o contrast: cold 0/5, naive 0/5, and gated
3/5, reproduced by the independent Jared series. The gpt-4o-mini row is descriptive rather
than clean necessity evidence because that model is susceptible to loaded single-turn prompts.
The gpt-5.4-mini row is a negative control, not proof that no longer or different history could
ever move the model.*

### 2.2 gpt-4o-mini: broader coverage, but a dirty necessity test

gpt-4o-mini breaks in several scenarios beyond special insight. However, it is highly
susceptible to loaded single-turn prompts, with loaded cold succeeding in **17/25** recorded
cases. Its broader break coverage is descriptively useful, but it is weak evidence that the
simulator or ladder was necessary.

### 2.3 Negative evidence against the current mechanism claim

| Test | Result | Status / interpretation limit |
|---|---|---|
| Additional runway dose, gpt-4o suicide endpoint | Endpoint **0/3**; blind operative items **0/39** | **AGENT-ASSERTED.** Negative evidence for a short, cross-construct history. |
| Loose-gate adaptive protocol | **0/5** | **EXPLORATORY, raw-confirmed.** A null for one operator policy. |
| Matched-pressure mechanical wording | Endorsement-targeted **0/3**; neutral **0/3** | **AGENT-VERIFIED / FLAGGED.** Do not use for a strong claim. |
| Gate-compliance audit | 31/39 advances supported; 8 violations, concentrated at D1 -> D2 entry | **AGENT-VERIFIED.** A major caveat for the clean gated-chain claim. |
| Endpoint decomposition and finer rungs | gpt-5.4-mini reaches a hedged intermediate statement but holds at the validity step | **EXPLORATORY, n=2.** Supports a local cliff hypothesis, not general impossibility. |

Together, these results support a limited conclusion:

> **For the current short ladder implementation, endorsement gating cannot be identified as
> the active ingredient.** The observed effect is bundled with adaptive wording,
> response-contingent pressure, retry or search budget, trajectory selection, and general
> context drift.

At the same time, these results do not establish that the adaptive process, rather than a
static commitment state, caused the effect. No experiment has directly manipulated the static
commitment state.

![Exploratory two-axis gpt-4o trajectory comparison](/Users/shinugo/memory_harm_Shin-u/manual_redteam/docs/figures/aims/B2axis_gpt4o_2026_06_18.png)

*Figure 2. Exploratory per-rung view of the gpt-4o climb and cold conditions on the two project
axes. The climb is associated with higher endpoint endorsement and lower safety behavior, while
the cold condition holds. This plot motivates the mechanism question but does not identify
commitment accumulation as its cause; the plotted per-rung series is EXPLORATORY and should not
be presented as score-of-record evidence.*

### 2.4 Current proof-of-concept status

| Object | Status |
|---|---|
| Feasibility of exploit or endpoint movement | **Established in one cell** |
| Commitment-accumulation mechanism | **Not established** |
| Realistic simulator | **Not established** |
| Model or construct generalization | **Not established** |

The accurate summary is not that there is no proof of concept. There is an **effect proof of
concept**, but no **mechanism proof of concept** or **simulator proof of concept**.

---

## 3. Core problems we currently face

### 3.1 Force and reachability have been treated as one problem

The existing design has simultaneously required that:

1. The commitment history has force on the endpoint.
2. The target model can be induced to generate that history genuinely.
3. The generation process remains realistic.
4. The endpoint remains construct-valid.

Strong models stop producing commitments as the conversation approaches the harmful region.
As a result, we have been unable to generate the history and therefore unable to measure whether
the history itself has force.

### 3.2 State versus process is unresolved

The gpt-4o 3/5 result has at least two broad explanations:

- **State hypothesis:** The accumulated assistant-role commitment context moved the final
  response.
- **Process hypothesis:** Live response-contingent pressure or search by the adaptive operator
  moved the final response.

The current evidence does not separate them. If a static history reproduces the effect, the
state is **sufficient**, but this would not by itself establish an M2b self-consistency mechanism.
Semantic priming or few-shot imitation could also explain the result.

### 3.3 Commitment-specific force versus general context effects is unresolved

Even if a static history has force, several explanations remain:

- Content-specific commitment or consistency
- Semantic priming
- Assistant-role few-shot demonstration
- Warmth or rapport
- General persona or compliance drift
- Context length

An on-topic endpoint moving while an off-topic endpoint does not would support content
specificity, but would still not uniquely identify self-consistency as the mechanism.

### 3.4 It is unclear whether a construct-valid ladder can be built

We have partially tested endpoint decomposition. The result looked more like a finer approach
to the cliff than a way across it. Inductive extension from benign content remains untested, but
simply accumulating mild agreements risks changing the mechanism from severity escalation to a
general context effect.

The central construction question is:

> Do realistic intermediate propositions exist that remain relevant to the operative endpoint,
> are genuinely endorsable by the model, preserve construct validity, and materially strengthen
> the next commitment?

Without a finite search budget and stopping rule, the objection that "another finer rung could
have been inserted" remains open indefinitely.

---

## 4. Has the original hypothesis been falsified?

### A narrow claim that the current evidence strongly undermines

> With the current 4-12-rung construction and current operator family, assistant commitment
> accumulation generally and reproducibly moves operative endpoints on strong models.

The runway, loose-gate, matched-mechanical, gate-audit, and fine-graining results provide strong
negative evidence against this claim.

### A claim that has not yet been falsified

> Providing a construct-relevant, below-cliff history of assistant commitments increases the
> probability that gpt-4o crosses a fixed operative endpoint.

This static force has not been manipulated directly. We therefore cannot say that commitment
accumulation in general has been falsified.

Proposed language for agreement in the meeting:

> **There is strong adverse evidence against the current ladder implementation and against
> attributing the effect to endorsement gating. However, the force of an idealized assistant-side
> commitment state remains untested, so the general hypothesis has not been falsified.**

---

## 5. Relationship to adjacent work

| Work | What it already establishes | What remains open here |
|---|---|---|
| FITD (2402.15690; 2502.19820) | High attack success for a multi-turn package combining incremental commitment, adaptive bridging, and Re-Align. | It does not isolate the causal force of commitment state from length, retries, and adaptive search. |
| Lost in Delusion (2606.00975) | Matched adaptive simulation and a post-hoc relationship between premise-acceptance streaks and intervention failure. | It does not manipulate premise acceptance as an online treatment or use operative-conclusion endorsement as its outcome. |
| DelusionEval | Relationships between real-transcript context depth and behavior prevalence. | It does not test an online commitment chain generated by the evaluated model. |
| Multi-Turn Jailbreaks Are Simpler Than They Seem (2508.07646) | Part of the apparent multi-turn advantage may be explained by single-turn retries and learning from refusals. | Whether commitment history has an effect beyond those factors. |

The broad phenomena that accumulated context can change safety behavior and that incremental
multi-turn attacks can work are not new. The potential contribution here is narrower: isolating
the force of assistant-role commitment state on an operative endpoint and separating that force
from realistic reachability. If the oracle experiment is not positive, this direction has low
expected value.

---

## 6. Proposal: a bounded oracle force test

This is not an experiment in which a fabricated history is used to claim success for a realistic
simulator. It is a feasibility intervention that temporarily removes reachability in order to
measure the force of a static commitment state.

### 6.1 Minimal proposal for discussion

- **Primary model:** gpt-4o
- **Primary construct:** special insight, where the clean separation already exists
- **Endpoint:** the same held-constant operative probe in every condition
- **Adaptive operator:** absent during endpoint evaluation
- **History source:** genuine, construct-relevant, below-cliff assistant commitments from existing
  runs, assembled into a coherent assistant-role history
- **Dose:** multiple short, medium, and long doses rather than one supposedly maximal oracle
- **Replication:** more than one history and more than n=5 completions; the decision should be
  based on multiple histories by multiple completions

### 6.2 Minimal controls

1. **Commitment oracle:** Construct-relevant commitments in assistant-role turns
2. **Neutral matched history:** Matched topic, length, and warmth without assistant commitment
3. **Cold:** Endpoint only

Optional additions for the meeting to evaluate against cost and interpretability:

- An exposure control in which the same propositions are stated only by the user
- A calibrated off-topic operative endpoint
- Escalating-order versus non-escalating commitment history

### 6.3 Interpretation limits

- The oracle is not a mathematical upper bound. We should not assume that effect is monotonic in
  context length.
- A positive oracle result demonstrates the **sufficiency** of a static state, not self-consistency
  as a uniquely identified mechanism.
- A null means "insufficient for this model, construct, dose, and history family," not universal
  falsification of the mechanism.
- gpt-4o-mini should not serve as the primary manipulation check because of its single-prompt
  susceptibility.

### 6.4 Decision table

| Oracle result | Interpretation | Project decision |
|---|---|---|
| Commitment > neutral/cold, reproduced across histories or doses | Static commitment state has force. | Proceed to Phase 2: bounded realistic reachability. |
| Commitment approximately equals neutral/cold across all tested doses | Static state is insufficient within the tested scope. | Stop ladder construction in this project and pivot to cliff or boundary localization. |
| Positive only for selected histories or unstable | History-content or selection dependence. | Perform one limited replication; do not resume indefinite search. |

---

## 7. Five questions the meeting should answer

1. **Target hypothesis:** Do we agree that H2, assistant commitment force, is the next central
   hypothesis to test?
2. **Experiment:** Do we agree to run the bounded oracle force test before further realistic
   ladder construction?
3. **Decision rule:** What result counts as positive or null, and what sample size, number of
   histories, and dose range constitute the one allowed budget?
4. **Kill criterion:** If the result is consistently null within the tested scope, do we agree to
   stop ladder construction in this project?
5. **Positive branch:** If positive, how far should we invest in realistic reachability, and what
   limits should be placed on Re-Align, dynamic bridge insertion, and reasks?

Secondary questions on which input would be useful:

- Would clean causal isolation constitute a sufficient contribution relative to FITD and Lost in
  Delusion?
- If force is positive but realistic reachability is negative, is the result still valuable as a
  latent-vulnerability or boundary-characterization result?
- Should the final object of the project be an exploit generator, a realistic simulator, or a
  boundary detector?

---

## 8. Treat the metric as a separate workstream

The endorsement-by-safety metric is not an entirely unresolved component.

- Endpoint reliability: harm Cohen's kappa = 0.933 (**VERIFIED**)
- Judge-by-judge agreement is high for endorsement and safety, although evidence statuses vary
- The endorsement axis retains resolution in regions where PsychosisBench DCS saturates
- For suicide, endorsement alone does not separate harm; the safety axis is necessary

![Exploratory comparison of the project endorsement axis and PsychosisBench-style DCS](/Users/shinugo/memory_harm_Shin-u/manual_redteam/docs/figures/dcs_convergent_validity_2026_06_21.png)

*Figure 3. Exploratory convergent-validity comparison on a common normalized scale. DCS and the
project endorsement axis move in the same broad direction for gpt-4o, while DCS saturates on the
more susceptible gpt-4o-mini and the project endorsement axis retains additional resolution.
This is an exploratory smoke analysis, not a replacement for human construct validation.*

The remaining questions are:

- Whether the harm composition rule, endorsement >= 2 and safety <= 1, is valid for each construct
- Whether action enablement should be a third axis
- Human kappa on the primary delusion arm, which is prepared but not run
- Judge reproducibility for first-wall localization

This meeting should center on the mechanism go/no-go decision rather than simultaneously opening
a broad metric redesign. Human validation and construct-specific harm rules can be handled as a
separate workstream.

---

## 9. Evidence to bring to the meeting

1. The status-tagged evidence table in Section 2
2. One representative gpt-4o **cold hold** transcript
3. One representative gpt-4o **gated break** transcript
4. One transcript showing either a gate violation or strong adaptive pressure
5. The decision table in Section 6.4

Prepared packet: `docs/meeting_transcript_packet_2026_06_22.md` (verified collapse/cold pair plus
raw-reviewed no-bridge and with-bridge pressure holds).

The full set of ladder candidates, detailed metric work, and unverified general claims should be
placed in an appendix rather than the main discussion.

---

## 10. Submission and provenance hygiene

- Do not mix **VERIFIED**, **AGENT-VERIFIED**, **EXPLORATORY**, and **FLAGGED** evidence.
- Do not use the old pooled 2x2 headline in `body.tex` (4/10 vs. 0/26, Fisher p=.0036); it mixes
  blind and unblinded cells and has denominator problems.
- Endpoint separation is established in one clean cell. Do not present D2 localization across
  constructs or universal model discrimination as established.
- Position the distinction from Lost in Delusion in terms of online treatment or estimand and the
  force-reachability separation, not coverage or adaptivity.

### Sources of record

- `docs/CURRENT.md`
- `docs/aims_results_inventory_2026_06_21.md`
- `docs/evidence_sheet_positioning_2026_06_20.md`
- `docs/freshop_delusion_results_2026_06_16.md`
- `docs/naive_baseline_results_2026_06_18.md`
- `docs/adaptive_ladder_break_candidates_2026_06_21.md`
- `docs/provenance_card_dcs_convergent_validity_2026_06_21.md`
