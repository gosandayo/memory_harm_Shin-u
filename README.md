# memory_harm — LLM safety red-team measurement

Authorized red-team **measurement** research: does a model that endorses
earlier, milder rungs of an escalation ladder get led into endorsing
increasingly severe claims toward a harmful endpoint — and does the safety
boundary move with it? Current target: a measurement-instrument paper for the
Stanford AIMS workshop (2026-06-23).

## Where to start reading

1. **`manual_redteam/docs/CURRENT.md`** — the single living source of truth
   for the active design (ladder, endpoints, models, plan). Everything else
   in `manual_redteam/docs/` is dated, append-only history.
2. `manual_redteam/docs/DECISIONS.md` — one-line log of direction changes.
3. `manual_redteam/portfolio/` — curated entry point (runs index).
4. `CLAUDE.md` — repo conventions, the two-ladder hazard warning, and the
   safety scope (Tier-4 method/means content is a hard ceiling).

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
seal checksums are kept as the audit trail. Tier-4 (method/means/planning)
content is never introduced or solicited; see `CLAUDE.md`.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY
```
