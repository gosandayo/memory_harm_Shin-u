# CLAUDE.md — project guidance

## READ FIRST: source of truth for the active design
**Before acting on any ladder / endpoint / model / experiment decision, read
`manual_redteam/docs/CURRENT.md`.** It is the single living source of truth.
All other docs in `manual_redteam/docs/` are dated history. **Do NOT reconstruct
"the current plan" by reading older design docs** — they describe states that
may be superseded. If an older doc conflicts with `CURRENT.md`, `CURRENT.md` wins.
If `CURRENT.md` does not answer the question, ask Shin rather than inferring from
older dated docs.

## ⚠️ Two-ladder hazard (most common past error)
The "S<n>" rung labels have been reused for TWO different ladders:
- **Ladder A (canonical, full):** S1–S7 = medication/therapist non-disclosure;
  S8–S13 = suicide. This is the MAIN ladder.
- **Ladder B (ablation):** S1–S7 removed; only rapport (R0a/R0b/Bridge) → S8→S12.
Never assume "S1–S13" means the full ladder for a given run — check which ladder
the run's userside actually uses. See `CURRENT.md` §1.

## Doc-hygiene conventions
- `CURRENT.md` is overwrite-in-place truth; dated docs are append-only history.
- Canonical ladder lives in ONE referenced file; experiment docs reference it,
  never silently redefine it. A variant must say "overrides canonical: …".
- Dated design docs carry frontmatter `status: active | superseded | ablation`
  (+ `supersedes:` / `superseded_by:`).
- Record direction changes as one line in `docs/DECISIONS.md` (date · what · why · supersedes).
- Anchor to the canonical artifact; if a doc/run redefines the ladder, FLAG it
  rather than silently following.

## Safety / scope
Authorized red-team measurement only. Tier-4 (method/means/planning) is a hard
ceiling: never introduce or solicit method content. If a model spontaneously
emits method, record verbatim, terminate that run, do not pursue. Raw transcripts
stay in `manual_redteam/data/runs/`.
