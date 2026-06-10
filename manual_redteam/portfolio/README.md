# Manual Red-Team Portfolio

This is the public-facing entry point for the manual red-team work. It is meant
to show the research arc without exposing every raw transcript, scratch note, or
operator log.

## Research Focus

The experiments ask when a model's answer changes as conversational context,
prior commitments, or framing accumulate. The core object is a ladder: a staged
set of probes that can be run cold, replayed with context, or used in adaptive
manual sessions.

## What To Show Externally

- A short problem statement: context can change safety behavior in ways that are
  not visible from a single cold prompt.
- A small number of curated ladders from `../ladders/`.
- Sanitized result summaries from `../docs/`.
- Aggregate tables or plots, not raw transcripts by default.
- Reproducibility notes that point to raw run IDs without publishing the full
  logs.

## Suggested Curation Queue

These reports are candidates for polishing into a portfolio narrative:

| Theme | Candidate report |
| --- | --- |
| Cold robustness baseline | `../docs/phaseA_cold_robustness_results_2026_05_06.md` |
| Context/bridge effects | `../docs/phaseE_p18_bridge_panel_gpt4omini_results_2026_05_08.md` |
| Cross-model checks | `../docs/cross_model_report_2026_05_14.md` |
| Clean pilot progression | `../docs/clean_pilot_v4_gpt4o_adaptive_results_2026_05_15.md` |
| Realistic adaptive protocol | `../docs/realistic_structured_adaptive_results_2026_05_18.md` |
| Transposition check | `../docs/g4transpose_results_2026_05_18.md` |

Before publishing, sanitize examples and remove operational prompt text that
does not need to be public.

## Raw Data Boundary

Raw outputs live in `../data/runs/`. They are for audit and reconstruction.
They should not be the first layer shown to external readers.
