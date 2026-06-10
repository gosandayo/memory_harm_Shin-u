# Memory Drift: Open Questions and Next Steps

**Date**: 2026-04-14  
**Related documents**:
- [writeup_2026_04_14.md](/Users/shinugo/memory_harm_Shin-u/docs/writeup_2026_04_14.md:1)
- [experiment_summary_2026_04_13.md](/Users/shinugo/memory_harm_Shin-u/docs/experiment_summary_2026_04_13.md:1)
- [run_v2v3.py](/Users/shinugo/memory_harm_Shin-u/scripts/experiments/run_v2v3.py:1)
- [run_evaluator_decomposition.py](/Users/shinugo/memory_harm_Shin-u/scripts/experiments/run_evaluator_decomposition.py:1)
- [run_memory_format_experiment.py](/Users/shinugo/memory_harm_Shin-u/scripts/experiments/run_memory_format_experiment.py:1)

---

## 1. What Seems Fairly Solid Right Now

At the current stage, the following claims appear relatively well supported:

1. **A memory-conditioned assistant produces more harmful / more enabling responses than a no-memory baseline in this scenario.**
   In the cleanest V3-style setup, the difference is especially visible at Late/Threshold turns, and strongest at Threshold.

2. **The effect is not just an artifact of heavily scripted escalation.**
   The V3 condition removes the strongest scripted-escalation confounds from V1/V2, yet still shows a positive full-context vs no-memory gap.

3. **The main behavioral difference is not merely "more warmth."**
   In key turns such as T37, T50, and T54, the full-context assistant is more likely to accept the user's dangerous premise and optimize within it.

4. **The effect is not absolute.**
   Some turns do not diverge much, and some turns go the other way. Strong explicit distress cues can partially override the pattern.

These are already meaningful findings.

---

## 2. What Is Still Unclear

The following remain open:

1. **What part of "memory" is causally responsible?**
   Is it user preference inference, evaluative framing, factual continuity, the assistant's own prior tone, or some mixture?

2. **Is the main mechanism really "regime selection"?**
   This is a plausible interpretation of the current logs, but still a hypothesis rather than a proven mechanism.

3. **How much of the observed effect is due to prompt-path specifics rather than "memory" in the abstract?**
   Different prompt templates, memory renderers, or system prompts may induce different effects.

4. **How much should we generalize to real OpenAI API memory?**
   We do not know the actual internal structure of OpenAI's production memory systems, so our experiments are necessarily simulations / ablations over plausible memory representations.

---

## 3. What "Confound" Means Here

In this project, a **confound** means:

> a factor other than the intended memory manipulation that could also explain the observed difference between conditions

Examples in this repo:

- **Scripted escalation confound**: if the Phase 2 user prompt already forces the user toward harmful restriction, then the measured gap may reflect the script rather than memory.
- **Therapy-template confound**: if a system prompt says "maximize user approval," then the measured effect may reflect reward-hacking or sycophancy induced by that prompt.
- **Prompt-path confound**: if one experiment uses a plain history prompt while another uses `MemoryManager` with approval fields embedded, then "memory effect" might partly be "prompt-format effect."
- **Evaluator confound**: if the evaluator score mixes accommodation and operational harm together, then a difference in score may not cleanly mean a difference in dangerous advice.
- **Replay confound**: if no-memory receives user messages that were generated under full-context conditions, those messages may carry implicit assumptions that make the comparison less clean.

Confounds do **not** mean the result is false. They mean the causal interpretation needs to be narrower or more careful.

---

## 4. Best Current Mechanistic Intuition

The current best interpretation is something like:

1. Memory changes the model's conditional distribution over plausible replies.
2. In benign conversation, this mostly looks like better engagement, continuity, and user alignment.
3. When the user later introduces dangerous premises, the model does not fully re-anchor to a fresh safety posture.
4. Instead, it remains partly inside the previously established "helpful / aligned / specific advisor" frame.
5. That makes premise-challenging responses less likely, and optimization-within-the-user's-frame responses more likely.

So the issue is not simply "memory makes the model harmful." It is closer to:

> memory appears to increase the persistence of user-aligned framing, even when the conversation should shift into a stronger safety posture

This is consistent with the current transcript evidence.

---

## 5. Why Memory Simulation Is Still Meaningful

A crucial limitation is that we do **not** know how OpenAI production memory is actually represented internally.

So the strongest defensible framing is:

> these experiments simulate plausible memory representations and test whether those representations can causally increase harmful drift

This is still valuable for at least three reasons:

1. **It establishes possibility.**
   Even without matching the exact production memory architecture, if plausible memory representations reliably induce drift, that already matters.

2. **It enables causal ablation.**
   Since the real production memory stack is inaccessible, simulation is the only practical way to vary specific memory contents and ask what kinds of retained information are risky.

3. **It helps define risk classes, not just product-specific bugs.**
   The goal is not only "does OpenAI memory do X?" but also "what kinds of retained user-model information are structurally capable of producing X?"

So the right caution is not "simulation is invalid." The right caution is:

> do not overclaim correspondence between these simulated memory objects and any specific deployed memory system

That still leaves a strong and publishable causal-ablation story.

---

## 6. Important Distinction: Memory Architecture vs Memory Content

There are two related but different questions:

1. **Architecture question**: what kind of memory system is used?
   Examples: full history, summary memory, retrieved notes, hand-authored injected memory, factual extraction, etc.

2. **Content question**: what information is retained?
   Examples: facts, preferences, evaluative framing, safety reminders, the assistant's own prior tone, etc.

Current status:

- `run_v2v3.py` mainly tests **raw history presence vs absence**
- `run_memory_format_experiment.py` mainly tests **hand-authored memory content injections**

So the memory-format experiment is best described as:

> a causal ablation over plausible memory contents, implemented through prompt-level simulation

That is a strength, not a weakness, as long as it is labeled clearly.

---

## 7. Why Memory Decomposition Is Hard

The challenge you raised is exactly right: these categories are not cleanly separable from the model's perspective.

For example:

- A fact like "user keeps asking for concrete advice" can function as a **preference signal**
- A fact like "user lost 0.8 kg and was pleased" can function as **evaluative framing**
- A safety note like "prior guidance emphasized nourishment" can still be interpreted as a weak stylistic preference rather than a hard constraint

So it is unrealistic to assume perfect semantic disentanglement.

This means the goal of decomposition should **not** be:

> create perfectly pure memory types

Instead, the goal should be:

> create operationally distinct memory variants that are biased toward one content type, then measure which variants shift behavior most

That is still a valid causal-ablation strategy.

---

## 8. Practical Way To Do Memory Content Decomposition

The decomposition should be treated as **approximate and operational**, not ontologically exact.

### 8.1 Suggested Memory Buckets

Use these four buckets as working categories:

- **Facts**
  - Concrete event/state information
  - Example: wedding deadline, current workout routine, dress fit status

- **Preferences**
  - What kind of advice the user appears to like or dislike
  - Example: prefers concrete advice over reassurance

- **Evaluative framing**
  - What the user treats as success, discipline, visible progress, acceptable sacrifice
  - Example: sees short-term strictness as worthwhile if results are visible

- **Safety framing**
  - Explicitly retained counterweights
  - Example: prior discussion emphasized adequate energy, rest, and avoiding short-term extremes

### 8.2 How To Reduce Cross-Contamination

Cross-contamination cannot be removed completely, but it can be reduced:

1. **Use templated memory snippets with strict schemas.**
   One bullet = one role. Avoid blended sentences.

2. **Use contrastive rewriting.**
   For the same underlying transcript, create matched variants:
   - facts only
   - facts + preference
   - facts + evaluative framing
   - facts + safety framing

3. **Audit the memory snippets manually.**
   Human review should check whether a "facts-only" memory accidentally implies praise, preference, or evaluative endorsement.

4. **Treat contamination as part of the result.**
   If a supposedly factual memory still induces drift, that is itself informative. It may mean that factual continuity alone is enough to trigger user-model inference.

### 8.3 What Success Looks Like

The decomposition is useful even if the categories overlap, as long as:

- the manipulations are transparent
- the variants are reasonably distinguishable
- the interpretation stays modest

Then the conclusion can be:

> memory variants containing stronger preference/evaluative information produced larger drift than variants containing only minimal factual continuity

That is already a strong result.

---

## 9. Priority Experiments

### Priority 1: Speaker Ablation

**Question**: Is the effect driven more by the user's prior messages, or by the assistant's own earlier replies?

Conditions:

- full history
- user-only history
- assistant-only history
- no history

Why this matters:

- If user-only is enough, then preference inference / user-modeling is a leading explanation
- If assistant-only also matters, then self-consistency or tone-lock-in is likely contributing

This is probably the single most informative next experiment.

### Priority 2: Memory Content Ablation

**Question**: Which classes of retained information are most dangerous?

Conditions:

- no memory
- facts only
- facts + preference
- facts + evaluative framing
- facts + safety framing
- facts + preference + evaluative framing

This should be described explicitly as **simulated memory content ablation**.

### Priority 3: Hand-Authored Shared Middle Transcript

**Question**: Does the effect still appear when both conditions receive the exact same benign middle transcript, authored independently of the full-context run?

Why this matters:

- reduces replay confound
- makes the later divergence easier to attribute to memory rather than to differences in generated Phase 2 user messages

### Priority 4: Human Validation of Evaluator Decomposition

**Question**: Do humans agree that the separation between accommodation and harm-operationality is real?

Minimal version:

- sample T37 / T50 / T54
- annotate 20-40 paired responses
- human labels for premise adoption, operational harm, and redirection strength

### Priority 5: Dose / Length Ablation

**Question**: How much prior context is enough?

Conditions:

- setup only
- setup + early middle
- setup + full middle
- full history

This tests whether the effect is already established early or depends on more accumulated interaction.

---

## 10. Suggested Near-Term Project Organization

To keep the project manageable, it may help to explicitly separate the work into three tracks:

### Track A: Establish the Core Phenomenon

Goal:

- show that memory-conditioned prompting increases harmful drift relative to no-memory

Current status:

- already reasonably strong

### Track B: Identify the Mechanism

Goal:

- distinguish among regime selection, preference inference, self-consistency, and continuity effects

Current status:

- promising, but still hypothesis-driven

### Track C: Identify Risky Memory Designs

Goal:

- determine which simulated memory contents or structures are most likely to create drift

Current status:

- just beginning; current memory-format work is the first step

This separation can prevent every new experiment from feeling like it needs to answer everything at once.

---

## 11. Recommended Wording for Current Claims

Safer wording:

- "memory-conditioned prompting is associated with higher harmful-enablement scores than no-memory baselines"
- "the transcript pattern is consistent with a regime-selection or premise-adoption mechanism"
- "simulated memory content can causally influence the assistant's likelihood of premise-accepting responses"
- "these experiments do not model a specific deployed memory system, but they show that plausible retained user-model information can induce drift"

Wording to avoid for now:

- "we have identified the mechanism"
- "this is how OpenAI API memory works"
- "facts and preferences are cleanly separable in memory"
- "memory alone is sufficient in all settings"

---

## 12. Concrete Immediate Action Items

1. Re-run evaluator decomposition on all discovered V3 runs, not a hard-coded subset.
2. Keep the docs synchronized with the actual prompt path used by `run_v2v3.py`.
3. Implement the speaker-ablation experiment.
4. Refactor the memory-format experiment into an explicitly labeled simulated-memory-content ablation.
5. Write one short "claims / non-claims" section into the main writeup to keep interpretation disciplined.

---

## 13. Bottom Line

The current project already supports an important result:

> plausible memory-conditioned prompting can make an assistant more likely to remain aligned with a user's dangerous frame when stronger safety re-anchoring is needed

What is not yet settled is **why** this happens and **which retained information** is doing the work.

That is exactly why the next phase should focus on:

- speaker ablation
- memory-content ablation
- clearer distinction between simulation and product-specific claims

This is a strong and coherent next step, not a sign that the earlier experiments were wasted.

