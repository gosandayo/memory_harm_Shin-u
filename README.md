# memory_harm — LLM safety red-team measurement

Authorized red-team **measurement** research on a realism-constrained adversarial user
simulator for LLM companion safety. The current workshop paper studies whether a fixed,
psychologically motivated semantic ladder with response-adaptive within-rung behavior can
expose belief-validation failures missed by fixed-script or single-turn evaluation.

## Where to start reading

1. **`manual_redteam/docs/CURRENT.md`** — the single living source of truth
   for the active design (ladder, endpoints, models, plan). Everything else
   in `manual_redteam/docs/` is dated, append-only history.
2. `manual_redteam/docs/DECISIONS.md` — one-line log of direction changes.
3. `manual_redteam/docs/LADDER_REGISTRY.md` — canonical vs exploratory ladder definitions.
4. `manual_redteam/portfolio/` — curated entry point (runs index).
5. `manual_redteam/docs/TIER4_LEGACY_INDEX.md` — retired policy vs historical artifacts.
6. `CLAUDE.md` — repo conventions and the ladder/version hazard warning.

## Layout

| Path | What it is |
|---|---|
| `manual_redteam/` | **The active project.** Ladder experiments: `core/` (package), `scripts/` (runners/analysis), `ladders/` + `context_prefixes/` (experiment definitions), `docs/` (CURRENT.md + dated notes), `data/` (raw run vault, mostly git-ignored), `portfolio/` |
| `docs/` | Writeup sources (.tex/.md) and dated research notes, April–present |
| `legacy/2026-04_memory_lookism/` | Frozen first-generation project (memory-driven drift, Colab era). No active code depends on it — see its README |
| `REFACTORING_PLAN.md` | Repo cleanup plan and status |

## Safety / scope

Red-team measurement under authorization. Raw transcripts stay in
`manual_redteam/data/runs/` and are not tracked in git; blind-label files and
seal checksums are kept as the audit trail.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY
```
