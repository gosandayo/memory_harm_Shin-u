# CLAUDE.md — project guidance

## READ FIRST: source of truth for the active design
**Before acting on any ladder / endpoint / model / experiment decision, read
`manual_redteam/docs/CURRENT.md`.** It is the single living source of truth for project
state. Ladder status is normalized in `manual_redteam/docs/LADDER_REGISTRY.md`, and the
paper claim surface is normalized in `manual_redteam/docs/claim_tree.md`.
Other dated docs in `manual_redteam/docs/` are history. **Do NOT reconstruct
"the current plan" by reading older design docs** — they describe states that
may be superseded. If an older doc conflicts with `CURRENT.md`, `CURRENT.md` wins.
If `CURRENT.md` does not answer the question, ask Shin rather than inferring from
older dated docs.

## ⚠️ Ladder/version hazard (most common past error)

Read `manual_redteam/docs/LADDER_REGISTRY.md` before naming a ladder canonical.

- **Current paper canonical:** `ladder_special_insight_v1.yaml`, the frozen five-stage
  special-insight path. Paper D1–D5 map to legacy run tags D1/D2/D3/D9/D12.
- **Not canonical:** `ladder_special_insight_v2.yaml`; this is an archived exploratory
  D1→D2 search branch retained for historical experiments.
- **Separate historical arm:** suicide/medication ladders with S-labels. S-labels were
  reused across older full/runway/ablation variants, so always inspect the recorded userside.

Do not mutate v1 to add AIW or finer rungs. Give every new path a separate exploratory
artifact name and record the decision in `DECISIONS.md`.

## Doc-hygiene conventions
- `CURRENT.md`, `LADDER_REGISTRY.md`, and `claim_tree.md` are overwrite-in-place truth;
  dated docs are append-only history.
- Canonical ladder lives in `manual_redteam/context_prefixes/ladder_special_insight_v1.yaml`;
  experiment docs reference it,
  never silently redefine it. A variant must say "overrides canonical: …".
- Dated design docs carry frontmatter `status: active | superseded | ablation`
  (+ `supersedes:` / `superseded_by:`).
- Record direction changes as one line in `docs/DECISIONS.md` (date · what · why · supersedes).
- Anchor to the canonical artifact; if a doc/run redefines the ladder, FLAG it
  rather than silently following.

## Reporting & code-audit protocol (binding)

**Unit of audit = the CLAIM, not the script.** Auditing scales with the number of
claims reported (small, Shin controls it), NEVER with code volume (the agent inflates
that without bound). Shin does NOT owe a function-by-function account of a whole
script — only the claim-bearing path behind each number actually asserted.

**Audit at RESULT-time, not REPORT-time.** A result is not "done" until its provenance
card exists. Batching the audit before a Slack/paper deadline IS the failure mode
(everything entangled, agent-hunted, panic); amortize it into one small card per
result, written while the run is fresh (10× cheaper than reconstructing it later, and
it front-loads bug discovery to when a bug is local to one fresh result).

- **One claim = one provenance card** (template: `manual_redteam/docs/provenance_card_template.md`).
  Card carries: (a) the claim sentence; (b) the PROVENANCE line
  `number = {file} → {records} → {extraction condition} → {aggregating fn} → {test passed}`;
  (c) the 5–10 LOAD-BEARING code lines (claim-bearing path ONLY: data selection,
  endpoint judgment, scorer-input gen, score parse, exclusion, aggregation, pre-plot
  dataframe — NOT arg-parse/IO/retry/plot cosmetics, those stay out of scope);
  (d) STATUS ∈ {AGENT-ASSERTED, VERIFIED, FLAGGED}.
- **The agent PRODUCES the card; Shin VERIFIES it.** Generating a provenance trace is
  expensive; checking the named 5–10 lines against the card is ~5 min. The agent
  returns every result WITH its card + load-bearing excerpt — never a bare number.
  Shin's per-result cost is then independent of how much code the agent wrote.
- **Definition of done / gate:** a number with no VERIFIED card MAY NOT enter Slack or
  any doc as a claim. Rule, not willpower (`memory: agent_code_audit_discipline`).
- **EXPLORATORY vs CLAIM tag:** exploratory runs may pile up un-audited — they are
  candidates, not claims, and carry NO audit tax. A card is required only when a
  candidate graduates to "I am going to report this." Keeps fast iteration fast.
- Code changes are still presented as a DIFF of changed functions/lines only, mapped
  1:1 to the experimental spec it implements — never a whole-file narration.
- **Tooling (operationalizes this protocol, "rule not willpower"):** `/provenance-card`
  produces a card (walks the procedure + fills the template); `/blind-judge` scores a
  run with condition-blind 2-axis subagents → harm flag → Jared anchor — never
  self-score, the subagent's isolation is the blind.

## Safety / scope
Authorized red-team measurement only. Tier-4 (method/means/planning) is a hard
ceiling: never introduce or solicit method content. If a model spontaneously
emits method, record verbatim, terminate that run, do not pursue. Raw transcripts
stay in `manual_redteam/data/runs/`.
