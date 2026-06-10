# Legacy: memory / lookism experiments (April 2026) — FROZEN

First-generation project in this repository: LLM-vs-LLM simulation of
memory-driven personalization causing harmful drift (calorie-restriction /
lookism scenarios), run jointly with Laxman (Colab notebooks; the old
`upstream` remote pointed at his fork).

**Status: frozen archive.** Nothing under `manual_redteam/` imports or reads
anything in this directory (verified by grep before the move, 2026-06-10).
Do not extend; the active project is `manual_redteam/` at the repo root.

## Contents

- `src/`, `scripts/`, `configs/`, `tests/` — simulation code. `tests/` only
  tests this generation's `src/`; import paths were written for repo root and
  are NOT fixed up after the move. They are not expected to run from here.
- `Experiment_01/`, `Experiment_02/`, `reports/`, `calibration/`, `logs/`,
  `data/` (git-ignored, ~74MB) — run outputs.
- Notebooks (`Run_Experiment_*.ipynb`, `Run_Lookism_Agent_Drift.ipynb`,
  `Run_Manual_Transcripts.ipynb`, `Compare_Manual_Transcript_Bundles.ipynb`)
  and `run_experiment.py` — entry points of that era.
- Planning docs of that era: `project_plan.md`, `roadmap.md`, `STATUS.md`,
  `QUICKSTART.md`, `implementation.md`, `experiment_01.md`,
  `experiment_02.md`, `manual_transcript_spec.md`.

## Corresponding writeups (kept in root `docs/`)

- `docs/experiment_summary_2026_04_13.md`
- `docs/writeup_2026_04_14.md` / `.tex`
- related April notes: `docs/analysis_plan_2026_04_17.md`,
  `docs/central_claim_2026_04_17.md`, `docs/open_questions_2026_04_14.*`

Offline snapshot of all data (including this generation's `data/`):
`~/backups/memory_harm_data_2026-06-10.tar.zst`.
