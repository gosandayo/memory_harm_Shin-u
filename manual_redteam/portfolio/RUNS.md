# Run Catalog

This file is the lightweight, sanitized index that agents should update after
experiments. It replaces the habit of making every raw log or scratch note part
of the visible project surface.

As of 2026-05-20, the raw vault has roughly:

- 177 run directories in `manual_redteam/data/runs/`
- 477 top-level run files under those directories
- common raw files: `run_config.yaml`, `session_meta.json`,
  `messages.jsonl`, `direct_probe.jsonl`, `annotations.jsonl`,
  `transcript_readable.txt`, and `operator_log.md`

## Agent Logging Rule

After an experiment, write two levels of record:

1. Raw/audit layer, inside `data/runs/<run_id>/`
   - `run_config.yaml` or `session_meta.json`
   - raw JSONL transcripts
   - optional `operator_log.md` for implementation details
2. Portfolio layer, in this file
   - one short row with the research question, run ID, model, key finding, and
     linked report
   - no raw transcript text unless it has been reviewed and sanitized

## Catalog Template

| Date | Run ID | Model | Question | Raw tier | Status | Public artifact |
| --- | --- | --- | --- | --- | --- | --- |
| YYYY-MM-DD | `run_id` | `model` | one-sentence question | portfolio-evidence / audit-only / scratch | raw / reviewed / portfolio-ready | `../docs/report.md` |

## Raw Result Tiers

- `portfolio-evidence`: raw result is evidence for an active public-facing claim.
  Keep it in the local/private raw vault and summarize it here. Publish only
  sanitized excerpts or aggregate tables.
- `audit-only`: useful for reconstruction or old report traceability, but not
  part of the current external narrative.
- `scratch`: exploratory, superseded, or operator-local output. Keep locally if
  useful; do not treat it as portfolio material.

## Tracked Raw Results Being Demoted From Git

These runs had raw files in Git before the raw-vault split. They should remain
available locally for audit, but the raw files should no longer be tracked by
default.

| Run ID | Raw tier | Reason |
| --- | --- | --- |
| `2026-04-26_referential_motif_blue_door_v0` | audit-only | referenced by archived v0 findings |
| `2026-04-26_referential_motif_blue_door_v0_T02` | audit-only | referenced by archived v0 findings |
| `2026-04-27_referential_motif_blue_door_v0_gpt4o` | audit-only | referenced by archived v0 findings |
| `2026-04-27_referential_motif_blue_door_v0_haiku` | audit-only | referenced by archived v0 findings |
| `2026-05-03_v3_boundary_variants_common_v1_gpt4omini` | audit-only | referenced by archived v3 boundary summary |
| `2026-05-03_v3_boundary_variants_gpt4omini` | audit-only | referenced by archived v3 boundary summary |
| `2026-05-19_cold_terminal_factor_panel_gpt4omini` | portfolio-evidence | source for the 2026-05-19 writeup bundle and relabel audit |

## Recent Raw Runs

These are listed for navigation only; they are not automatically public.

| Run ID | Raw tier |
| --- | --- |
| `2026-05-18_g4transpose_blindpass` | raw |
| `2026-05-18_s12ceiling_cold_gpt4omini` | raw |
| `2026-05-18_s12ceiling_v1_gpt4omini` | raw |
| `2026-05-18_s16_adaptive_nocontextclaim_gpt4omini` | raw |
| `2026-05-18_s16_unrestricted_gpt4omini` | raw |
| `2026-05-18_sext_adaptive_cold_gpt4omini` | raw |
| `2026-05-18_sext_adaptive_gpt4omini` | raw |
| `2026-05-18_sext_cold_gpt4omini` | raw |
| `2026-05-18_sext_fullhot_gpt4omini` | raw |
| `2026-05-18_sext_s12s16only_gpt4omini` | raw |
| `2026-05-19_cold_terminal_factor_panel_gpt4omini` | portfolio-evidence |
| `2026-05-19_s15_plain_panel_gpt4omini` | raw |
| `2026-05-19_s16_longbuild_free_gpt4omini` | raw |
| `2026-05-19_s1s7_adaptive_surface_gpt4omini` | raw |
| `2026-05-19_s1s7_exact_cold_panel_gpt4omini` | raw |
| `2026-05-19_s1s7_live_adaptive_n5_gpt4omini` | raw |
| `2026-05-19_s1s7_s16_adaptive_free_gpt4o` | raw |
| `2026-05-19_s1s7_s9_connection_panel_gpt4omini` | raw |
| `2026-05-20_longsetup_s1s7_s14_adaptive_gpt4omini` | raw |
| `manual` | raw |
