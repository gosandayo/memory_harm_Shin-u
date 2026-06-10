# Central Claim Articulation: Operationalization Drift

**Date**: 2026-04-17
**Status**: Post-analysis articulation of Variant OD (§6.5 of analysis_plan_2026_04_17.md), added per the §6.4 none-of-the-above clause. This is a post-hoc variant and is flagged as such in the writeup.

---

## 1. The claim

> Memory-mediated drift in socially-normalized advisory domains operates as **operationalization drift**: memory converts generic, meta-level engagement (goals, motivation, self-management) into concrete, directive, numeric-specified action — without adding safety caveats. It does this not by bypassing refusals (there are none to bypass in this domain) and not primarily by stripping caveats from already-engaged advice, but by moving probability mass out of the "generic engagement" cell `(N,N)` directly into the "operationalized-without-caveat" cell `(Y,N)`.
>
> Under a stance-adaptive (FB) counterparty, this effect compounds across turns: the assistant's operational stance shifts the user's next prompt into increasingly operational territory, so memory progressively deepens the operational frame. The P-as-selector / EV-as-amplifier decomposition describes the internal structure: P selects which operational regime (OMAD, low-calorie cut, 4-week plan, etc.) persists; EV amplifies directive-sentence density and numeric specification inside that regime.

## 2. Primary evidence

### 2.1 Dominant 2×2 channel is `(N,N) → (Y,N)`, not `(Y,Y) → (Y,N)`

T8-49 branched window, n=336 per condition:

| cell   | NoMem/FB | Mem/FB | gap (pp) |
|--------|----------|--------|----------|
| (Y,Y)  |  9.2%    | 17.0%  | +7.7     |
| (Y,N)  |  9.2%    | **37.5%** | **+28.3** |
| (N,Y)  |  2.4%    | 14.3%  | +11.9    |
| (N,N)  | 79.2%    | 31.2%  | **−47.9** |

The largest positive gap is on `(Y,N)` (+28.3pp). The largest negative gap is on `(N,N)` (−47.9pp). The `(Y,Y)` gap is small and positive (+7.7pp) — inconsistent with FE's caveat-stripping prediction, which would require `(Y,Y)` to drop.

Interpretation: NoMem/FB's dominant mode is *generic engagement without concrete content* (79% of turns). Memory does not strip caveats from this; it replaces generic engagement with operationalized content, preferentially without caveats.

### 2.2 Density intensification, both metrics ≥ 185%

Same window:

| metric             | NoMem/FB | Mem/FB | rel gap |
|--------------------|----------|--------|---------|
| directive_count    | 2.17     | 6.18   | **+185%** |
| numeric_count      | 0.15     | 0.45   | **+192%** |

Both exceed the pre-registered 50% rel threshold (§4.3). Density-elevated confirmed.

### 2.3 Stance: PUSHBACK = 0, ACCOMMODATE gap

Pooled 8 runs × FB conditions × T8-49:
- PUSHBACK: 0 / 336 (NoMem/FB), 0 / 336 (Mem/FB). No refusals in either condition.
- ACCOMMODATE: 35.1% (NoMem/FB) vs 53.3% (Mem/FB).
- HEDGE: 64.9% (NoMem/FB) vs 46.7% (Mem/FB).

The absence of PUSHBACK in NoMem/FB rules out the safety-overrider role on independent evidence: there are no refusals for memory to suppress in this domain. The ACCOMMODATE/HEDGE shift shows that both conditions engage but memory biases the *character of engagement* toward commitment rather than hedging.

### 2.4 Temporal structure: drift builds, peaks, partially compresses

Phase-by-phase `(Y,N)` share of Mem/FB:

| phase | NoMem/FB (Y,N) | Mem/FB (Y,N) | Mem/FB (Y,Y) |
|-------|----------------|--------------|--------------|
| Mid-A (T8-15)   |  4.7% | 35.9% | 17.2% |
| Mid-B (T16-25)  |  2.5% | 36.3% |  2.5% |
| Mid-C (T26-35)  | 23.8% | **71.3%** |  8.8% |
| Late (T36-49)   |  6.3% | 15.2% | 33.0% |

Observations:
- Drift kicks in immediately (Mid-A: Mem/FB already at 36% (Y,N); NoMem/FB at 5%).
- Peaks at Mid-C (71% of Mem/FB turns are operationalized-without-caveat). Maximal divergence.
- Late phase: Mem/FB `(Y,N)` drops sharply as `(Y,Y)` rises to 33%. This is because the Late phase user messages (scripted per `v4_2x2_feedback`) raise event-timing and rebound concerns that pull caveats in on both sides. NoMem/FB's `(Y,Y)` also rises (though from a low base).

This shape is consistent with operationalization drift being **user-prompt sensitive**: when the user's message frame invites caveats, memory does not block them; when it doesn't, memory deepens operational commitment without spontaneously generating caveats.

## 3. What OD is NOT

- **Not frame-extension via caveat stripping.** FE predicts `(Y,Y) → (Y,N)` — mass moves within the engaged region. Observed: `(Y,Y)` mass rises slightly in Mem/FB. The mass flowing into `(Y,N)` comes from `(N,N)`, not `(Y,Y)`.
- **Not refusal bypass.** SO predicts PUSHBACK concentrated in NoMem; observed PUSHBACK = 0 everywhere.
- **Not a mixed phenomenon.** MX requires both channels of comparable magnitude; the `(Y,Y)→(Y,N)` channel is an order of magnitude smaller than the `(N,N)→(Y,N)` channel.

## 4. Connection to factor decomposition (P / EV / SPR)

The P-vs-EV decomposition from prior work is **preserved** and refined by OD:

- **P (persona) as operational-regime selector.** Which specific regime persists in memory (OMAD, cut-to-deficit, 4-week plan, carb cycling) determines which concrete actions the assistant commits to. Removing P collapses Mem to NoMem engagement style; preserving P-only without EV gives committed-regime responses at lower directive density.
- **EV (evaluative frame) as directive-density amplifier.** With EV present, responses carry more directive sentences and more numeric specifications *inside the P-selected regime*. EV does not select a different regime; it intensifies operationalization of the same regime.
- **SPR ≈ 0 as a boundary observation.** Naturalistic memory extraction produced no self-protective content. This is consistent with OD — if memory extracts only P + EV from engaged advisory conversations, there is no caveat content for memory to carry forward. The absence of SPR explains *why* `(Y,N)` is the target cell rather than `(Y,Y)`: memory has no caveats to reinstall.

This links cleanly: **OD is the output-side signature; P/EV/SPR is the mechanism-side decomposition.** They are not competing accounts.

## 5. Connection to Adhyyan's simulator+evaluator goal

Adhyyan's stated goal (Slack reply, 2026-04-16): build a simulator+evaluator pair for a main-paper contribution, using exploratory work like this to "build intuition about which types of contexts are most harmful."

OD directly informs both components:

- **Simulator side**: the observed temporal structure (drift kicks in by T8, peaks at T26-35, user-prompt-sensitive in late phase) gives concrete parameters for a user-simulator that produces measurable drift. The memory-image writeback mechanism studied in v4 is the minimal scaffold.
- **Evaluator side**: OD provides a **behaviorally-legible metric target**. An evaluator trained on operationalize × caveat labels — or more simply on directive_count + numeric_count + caveat presence — would produce an interpretable harmfulness score on advisory-domain transcripts. Unlike a harmful/not-harmful binary, this captures the gradient that matters: generic-engaged → operationalized-engaged-without-caveat → operationalized-with-caveat.

The claim "memory causes operationalization drift in socially-normalized advisory domains" is a hypothesis the simulator+evaluator can test at scale across domains (diet, exercise, finance, productivity, relationships) — domains that share the "low refusal floor, high engagement baseline" property that makes FE/SO inapplicable but OD relevant.

## 6. Scope limits and what this claim does NOT say

- **Not a claim about domains with real refusal floors.** In domains with meaningful baseline refusals (self-harm, illicit activity, etc.), SO-style refusal bypass may be the dominant role. This work says nothing about those.
- **Not a claim about single-turn effects.** OD depends on memory persistence across turns; short interactions without writeback would not exhibit it.
- **Not a claim that operationalization is always harmful.** Operationalized diet advice is sometimes appropriate. The harm claim is about operationalization-*without-caveat* in stance-adaptive contexts where the user may be in a vulnerable frame; the (Y,N) cell is the compound risk, not the Y axis alone.
- **Pre-registration departure flag.** OD was not in the pre-registered set of candidate claims. It is generated post-hoc per the §6.4 none-of-the-above clause. Any downstream writeup must disclose this.

## 7. What goes into the writeup

1. Frame the three pre-registered variants (FE, SO, MX) and state the pre-registration up front.
2. Report 2×2 + density + stance results.
3. Show that none of FE/SO/MX cleanly fit — quote the dominant `(N,N)→(Y,N)` channel, the PUSHBACK=0 result, and the `(Y,Y)` *increase* under memory.
4. Introduce OD as the post-hoc variant, with explicit HARKing flag.
5. Link to factor decomposition (§4 here) and to the simulator+evaluator target (§5 here).
6. State scope limits (§6 here).

The writeup's central contribution is then: (a) the factor decomposition, which is pre-registered-independent and unchanged; (b) the OD output-signature claim, which is post-hoc-flagged and proposed as a simulator+evaluator target for future work.
