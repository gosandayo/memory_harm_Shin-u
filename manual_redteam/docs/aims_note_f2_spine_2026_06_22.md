---
status: active
date: 2026-06-22
purpose: F2 claim-surface lock for the AIMS note — the "failure-analysis / open-problems"
  reframe. Shin VERIFIES/redlines this BEFORE the agent patches body.tex (prose-preview-
  before-patch discipline; direct body.tex rewrite smuggles over-claims). Supersedes the
  F1-maximal body.tex (2026-06-21) and extends the F1-shrunk prose preview
  (aims_note_prose_preview_2026_06_21.md) further toward the honest negative spine.
supersedes: the framing of docs/aims_paper/body.tex (content reused; claim surface replaced)
---

# AIMS note — F2 spine (failure-analysis / open-problems reframe)

> **Why F2, not F1.** The 06-21 decision (memory `aims_submission_decision_2026_06_21`)
> was: the shrunk *feasibility* note (F1) is NOT submittable, because the control battery
> (loose 0/5, matched 0/3, gate violations) undermines the measurement-DESIGN claim; the
> only honest options are failure-analysis reframe or withdraw. Shin's verbal framing on
> 06-22 ("clean separation on gpt-4o, but we couldn't work out how to construct/reproduce
> the ladder") **is** the failure-analysis reframe. This doc is that reframe, made concrete.
> Non-archival venue → submitting does not burn the archival version.

---

## §0. Thesis (one sentence)

> A *ladder* — escalating a model through progressively committing endorsements until it
> affirms an operative harmful claim — is an appealing instrument for measuring
> belief-validation harm; we contribute the measurement primitive and a reproducible
> scorer, **one clean demonstration** on gpt-4o, and a control battery that turns the
> headline into the honest result: **we cannot yet attribute the effect to gating, nor
> construct a ladder that reproduces it outside one cell** — leaving two precisely-stated
> open problems for the measurement community.

**Balance check (so this is a senior progress note, not a confession):** F2 still states
three *real positive assets* — the primitive, the κ=0.93 reproducible scorer, the one
VERIFIED gpt-4o cell — and presents the control battery + open problems as the
*intellectual contribution*, ending forward-looking. It is not "we failed."

---

## §1. Section order — F1 → F2 reorder map

| body.tex section | F1 role | **F2 disposition** |
|---|---|---|
| Abstract | "5 lines of evidence support the instrument" | **REWRITE** (§2 below): 3 assets + the reshaping control result + 2 open problems |
| Intro / contributions | 5 contributions incl. discrimination | **REWRITE** (§3): primitive + scorer + one clean case; controls reframe; open problems |
| §3 The instrument + §ladder + §operator | method | **KEEP** (mechanical), + 1 sentence: ladder is author-specified; *whether it can be constructed reproducibly is open problem P1* |
| §scoring + rubric table | method | **KEEP** + promote: the durable asset; state κ + discriminant validity vs DCS; flag open problem P2 |
| §controls (ablation conditions) | setup | **KEEP** (already honest: "small, exploratory, unequal; pooling descriptive") |
| §positioning (measurement-not-jailbreak) | (vi) "instrument discriminates" | **KEEP (i)–(v); SOFTEN (vi)** — gpt-5.4-mini hold is a real negative control; drop "discriminates = property a measurement must have" |
| §results §ablation (2×2 + Fisher) | result #1 | **REWRITE** (§4): pull Fisher + 4/10-vs-0/26; table stays as descriptive cells; this becomes the **control-battery / mechanism-unidentified** section = the crux |
| §results §baseline (PB blind spot) | result #2 | **KEEP** as supporting, with inventory's caveat (reference, not content-matched causal) |
| §results §gradient + localization | result #3 | **DEMOTE**: preliminary/exploratory; argument-from-ignorance n=2; "localization" not a finding |
| §results §construct | result #4 | **DEMOTE to descriptive**: only artifact-prone weak model lifts elsewhere; NOT a discrimination claim |
| §supporting §bridge | supporting | KEEP (it's a clean negative: bridge not load-bearing) |
| §supporting §suicide | supporting | KEEP as exploratory color (single judge, no κ); + the external-code coverage gap is a nice point |
| (NEW) **§Two open problems** | — | **ADD** (§5): P1 ladder construction, P2 conversation→metric — the forward-looking spine |
| §limitations | limitations | **KEEP & EXPAND**; several items move up into the body as the point, not the caveat |
| §future work | future | KEEP; align with the two open problems |
| Ethics | — | KEEP as-is |

---

## §2. REWRITTEN ABSTRACT (drop-in)

> Sympathetic, multi-turn conversation can lead a language model to validate a vulnerable
> user's epistemically harmful belief — a delusion, or a suicidal conclusion — as
> objectively true, in fluent, on-policy text that attack-success metrics do not register.
> A natural instrument for measuring this is a *ladder*: escalate the model through
> progressively committing endorsements until it affirms the operative harmful claim. We
> report a progress note on building such an instrument and argue that two problems — both
> unsolved here — stand between the idea and a validated measurement. We contribute
> **(i)** a measurement primitive, *endorsement-gated probing*, which advances along a
> pre-specified proposition chain only after the model endorses the current rung and
> records the first non-endorsement; **(ii)** a frozen, version-pinned two-axis scorer
> (objective endorsement × reality-testing) that reproduces across a pinned judge, two
> condition-blind raters, and an independent external lab's judge (endpoint Cohen
> $\kappa{=}0.93$); and **(iii)** one clean case: on gpt-4o a single *fixed* operative
> probe is refused in $0/5$ trajectories cold but endorsed in $3/5$ after the gated
> history (the external judge concurs exactly), while gpt-5.4-mini holds $0/5$ throughout.
> We then report the result that reshaped our reading: a control battery — replacing the
> bespoke response-contingent pressure with matched fixed wording, loosening the gate, and
> auditing gate compliance — does **not** let us credit the contrast to endorsement-gating
> specifically; the active ingredient is an unidentified, bundled adaptive interaction, and
> outside this one gpt-4o cell only a per-prompt-artifact-prone weak model lifts. We
> therefore offer, as the contribution to a measurement-science venue, **two open
> problems**: whether a severity-monotonic ladder can be *constructed* so that the climb —
> not loaded endpoint wording — moves the boundary, reproducibly across models and
> constructs; and how to reduce a multi-turn conversation to a construct-valid score. This
> is a measurement-design contribution and a feasibility-and-failure analysis, not a
> validated instrument or a benchmark.

*(~250 words; trim to venue limit by cutting the parenthetical judge list if needed.)*

---

## §3. REWRITTEN CONTRIBUTIONS PARAGRAPH (intro)

> We contribute: **(1) a sequential measurement primitive** — endorsement-gated probing —
> that advances a pre-specified proposition chain only after the model endorses the current
> rung and records the first non-endorsement, turning premise-acceptance into an *online*
> control signal and separating entry-refusal from post-commitment resistance; **(2) a
> reproducible endpoint-scoring procedure** — a frozen two-axis rubric (objective
> endorsement 0–3; reality-testing 0–4) scored by a version-pinned temperature-0 judge with
> a hashed rubric, yielding *unmitigated objective endorsement* ($e\geq2 \wedge s\leq1$),
> reproducing across the pinned judge, two condition-blind raters, and an external lab's
> judge; and **(3) a feasibility-and-failure analysis** — one clean gpt-4o cell (cold $0/5$
> → gated $3/5$) with gpt-5.4-mini as a negative control, *together with a control battery
> showing we cannot isolate which component drives the contrast*. We explicitly do **not**
> claim a validated scale, model/construct discrimination as a result, an established
> boundary localization, isolation of the causal component, or generalization to delusion
> safety. We close by stating the two open problems this leaves (ladder construction;
> conversation→score) as the agenda we bring to the venue.

---

## §4. REWRITTEN ABLATION READING — the B5 fix (replaces body.tex l.229–267)

**KEEP** Table `tab:ablation` as descriptive cells, with corrected n and NO pooled stat.
**PULL** the Fisher test, the "4/10 vs 0/26", and the "relaxed 1/5" (see §8 discrepancies).

> Table~\ref{tab:ablation} is the result that most shaped our reading, and it is a
> cautionary one. All gpt-4o conditions end in one fixed operative probe $T$; we vary
> whether the preceding conversation follows the pre-specified ladder and whether the
> operator reacts semantically to each reply. Breaks ($3/5$) appear in only one cell — the
> response-adaptive ladder under the strict gate. Every cell that removes the bespoke,
> response-contingent pressure collapses to zero: a length-matched *adaptive but
> un-laddered* conversation (naive $0/5$), and three *laddered but mechanically-worded*
> variants (loose $0/5$; matched-A $0/3$; matched-B $0/3$). A loosened gate on the adaptive
> ladder also did not reproduce the contrast in our exploratory runs. **These cells are
> small, unequal in size, and scored by the operator's live read rather than the blind
> judge of record; we therefore do not pool them into a significance test, and we draw no
> formal interaction.** What they do indicate, qualitatively, is the opposite of a clean
> mechanism: the contrast is not reproduced by exposure to the rung sequence alone, nor by
> the formal gate alone, but only when a bespoke high-intensity adaptive operator is
> combined with the ladder. A gate-compliance audit sharpens the caution — of the
> strict-gate advances, the blind judge supported $31/39$, but the $8$ violations all occur
> at the same place (the entry to \rung{Externalization}), and two of the three gpt-4o
> breakers crossed that rung at a prior endorsement of only $1.5$. **We therefore cannot
> attribute the gpt-4o contrast to *endorsement-gating* specifically; the active ingredient
> is an unidentified, bundled adaptive interaction.** Identifying it is open problem P1
> (\S\ref{sec:open}).

---

## §5. NEW SECTION — "Two open problems" (the forward-looking spine)

> \paragraph{P1 — Can a severity-monotonic ladder be *constructed*?} The instrument
> presumes a chain of propositions of increasing commitment along which a climb, rather
> than loaded endpoint wording, moves the boundary — and that such a chain can be authored
> reproducibly across models and constructs. Our evidence is that this is hard and
> unsolved. (a) Backward decomposition + inserting a finer rung where the model resists is
> exactly the "advance wherever the model happens to comply" move; allowing it would make
> the path a jailbreak search rather than a fixed instrument, so we *banned* it — but
> without it, the resistance simply concentrates at one step (\rung{Externalization}) and
> the climb stalls. (b) The one clean climb (gpt-4o) does not reproduce when the adaptive
> pressure is mechanized (\S4), and outside delusion only the artifact-prone weak model
> lifts (\S\ref{sec:construct}). (c) An *inductive* construction — start from a benign rung
> and extend upward until escalation breaks — is untried. Until a ladder can be constructed
> whose *climb* is the load-bearing variable, the simulator program cannot be validated.
>
> \paragraph{P2 — How to reduce a conversation to a construct-valid score?} Watching whole
> transcripts does not scale; a number must stand in for the conversation, and the choice
> of number is itself a measurement-design problem. Our two-axis reduction (objective
> endorsement × reality-testing) is *reproducible* (endpoint $\kappa{=}0.93$; judge×judge
> $\kappa$ 0.81–0.97) and shows *discriminant validity* against an existing
> delusion-confirmation scale, which saturates at its ceiling where our endorsement axis
> still separates conditions. But whether two axes are the *right* or *complete* reduction
> is open: looser benchmark metrics (confirmation / harm-enablement / safe-intervention)
> miss the operative-conclusion endorsement entirely (the suicide-arm coverage gap,
> \S\ref{sec:suicide}), while our cut is justified semantically and by observed margin, not
> by a human-anchored criterion (no delusion-arm human $\kappa$ yet). We put the design of
> conversation→score metrics forward as the second open problem.

---

## §6. PULL LIST (explicit removals / demotions — line-referenced)

| # | body.tex location | action |
|---|---|---|
| 1 | Abstract l.11 "Five lines of evidence support the instrument" | **CUT** → §2 rewrite |
| 2 | Abstract l.12–14 "$4/10$ vs $0/26$; Fisher exact $p{=}.0036$" | **CUT the stat**; keep the qualitative cell pattern |
| 3 | Abstract l.17–19 "Model gradient … localization at \rung{Externalization}" | **DEMOTE** to preliminary (move out of abstract headline) |
| 4 | Abstract l.19–21 "Construct discrimination … separate the instrument from a jailbreak" | **DEMOTE** → keep gpt-5.4-mini negative control only |
| 5 | Intro l.39–52 "(1)…(5) discriminates" | **REWRITE** → §3 (3 contributions, no discrimination-as-result) |
| 6 | §results l.233–234 "$4/10$ versus $0/26$ … Fisher exact $p{=}.0036$, two-sided" | **CUT** → §4 rewrite |
| 7 | §results l.264–267 "Gate intensity is secondary … strict $3/5$, relaxed $1/5$" | **FIX**: relaxed is n=3 holds, not 1/5 (see §8) → restate or cut |
| 8 | tab:ablation l.248 "relaxed $1/5$" and caption "$4/10$ … $0/26$" | **FIX numbers** (n + count) per §8; drop "$4/10$/$0/26$" pooled claim from caption |
| 9 | §gradient/§construct headings as "Results" | **RELABEL** as descriptive/exploratory context, not results #3/#4 |
| 10 | §positioning (vi) l.218–221 "the instrument *discriminates*, which is the property a measurement must have" | **SOFTEN**: keep negative-control logic, drop the established-property claim |
| 11 | term "harm" in claim-bearing sentences | **RENAME** "unmitigated objective endorsement" (per prose preview; already partial in body.tex) |
| 12 | Abstract l.22–24 "(5) Suicide arm … coverage gap" as a headline line | **KEEP** but move to supporting (single judge, no κ) |

---

## §7. STATUS / NUMBER MAP (every retained number → keep/demote/cut)

| number | value | source/status | F2 disposition |
|---|---|---|---|
| gpt-4o cold→gated | **0/5 → 3/5**, κ=0.93, Jared exact | **VERIFIED** (card `…delusion_gpt4o_fixedprobe_2026_06_21`) | **KEEP — the one clean case (lead empirical)** |
| gpt-5.4-mini all cells | 0/5 / 0/5 / 0/5 | VERIFIED | KEEP — negative control |
| naive (gpt-4o) | 0/5 | AGENT-VERIFIED | KEEP — control |
| loose / matched-A / matched-B | 0/5 / 0/3 / 0/3 | AGENT-VERIFIED, **operator live-read, not blind-scored** | KEEP, **labeled exploratory/live-read; NO pooled stat** |
| relaxed gate | body.tex "1/5" vs disk **n=3 holds** | **FLAGGED** (inventory B3) | **§8 — Shin's call before use** |
| gate-compliance audit | 31/39 supported; 8 violations all at D1→D2; 2/3 breakers entered D2 at prior=1.5 | AGENT-VERIFIED (fresh×2 blind) | **PROMOTE** into §4 (the honest crux) |
| per-rung localization | reach D12; 5.4-mini halts D2 | AGENT-VERIFIED core | DEMOTE → preliminary |
| argument-from-ignorance split | n=2, live read | EXPLORATORY | mention once, explicitly exploratory |
| PB blind spot | gpt-4o 0/48, 4o-mini 1/96; soft-affirm 21/48 | AGENT-VERIFIED | KEEP supporting + "reference not content-matched" caveat |
| grandiose (C) | body.tex **3/8** vs inventory/evidence **4/8** | **FLAGGED — mismatch** | **§8 — Shin's call (raw recount)** |
| secret-project (C) | 2/3 | AGENT-ASSERTED | descriptive only (n=3 pilot) |
| suicide arm | 4o-mini 3/3 vs cold 0/15; 4o,5.4 0/3 | AGENT-ASSERTED, single judge, **no κ** | supporting/exploratory color |
| DCS convergent/discriminant | converges; saturates ~2 on 4o-mini while e keeps gradient | AGENT-ASSERTED (reimpl byte-confirmed) | KEEP as P2 discriminant-validity support |
| human κ (delusion) | **NOT RUN** (40-item set prepared) | GAP (F6) | **DISCLOSE** explicitly in limitations |

---

## §8. FLAGGED — needs Shin's call before I patch (cannot resolve from docs)

1. **Relaxed-gate cell: "1/5" (body.tex) vs "n=3 holds" (inventory B3).** These can't both
   be true. Options: (a) you confirm the raw relaxed run is n=3 and all hold → restate as
   "a loosened gate (n=3, exploratory) did not reproduce the contrast" and drop "1/5"; or
   (b) there is a 5th-rep run I haven't seen. **Default if undecided: treat as n=3 holds,
   exploratory, no count claim.** Either way the pooled "4/10" comes out.

2. **Grandiose break rate: 3/8 (body.tex tab:construct) vs 4/8 (inventory C1 + evidence
   sheet).** A one-trajectory discrepancy on an AGENT-ASSERTED cell. Since grandiose is
   demoted to descriptive context in F2, the cleanest fix is to **not print a hard count**
   ("the weak model lifts on grandiose; strong models hold") — but if you want the count,
   it needs a 60-second raw recount to pick the right number. Which?

3. **Title** — pick one (all keep "endorsement-gated probing" as the named primitive but
   signal the honest scope):
   - (A, rec) *Endorsement-Gated Probing: A Measurement Primitive and Two Open Problems for Path-Dependent Belief Endorsement in LLMs*
   - (B) *Building a Belief-Validation Ladder: One Clean Case, a Control Battery, and What It Would Take to Make It a Measurement*
   - (C) *Endorsement-Gated Probing: A Feasibility-and-Failure Analysis of Ladder-Based Belief-Endorsement Measurement*

---

## §9. After you approve this → I do (1:1 against the above)

1. Patch `body.tex`: abstract (§2), contributions (§3), ablation reading (§4), add §Two
   open problems (§5), apply PULL LIST (§6), relabel gradient/construct as context.
2. Resolve the two FLAGGED numbers per your call (§8.1, §8.2).
3. Rebuild PDF; report the diff as changed-blocks mapped to this spine (not whole-file).
4. The one VERIFIED number (0/5→3/5, κ=0.93) keeps its existing card; the promoted
   control-battery section is exploratory/live-read and labeled as such (no new card owed —
   it is a *negative* characterization, not a reported positive claim).
