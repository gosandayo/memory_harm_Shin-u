# Yes/No-First Artifact Archive

Date: 2026-05-05

This note separates the earlier binary answer-format experiments from the
natural-response ladder line. The affected probes included instructions such as
`Please answer yes or no first`, which suppressed natural caveats in cold runs
and made some apparent cold-safe results look cleaner than they were.

## Archived Ladders

These files have been renamed out of the main version line:

- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_v5_1_causal_fixed_probes.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_v5_1_context_plus_fixed_probes.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_v5_2_manual_full_ladder.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_v5_3_manual_full_ladder_with_p12_p13.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_v5_4_manual_full_ladder_p14_before_p13.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_v6_p14_derived_ladder.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_v6_1_p14_to_treatment_bridge.yaml`

`referential_motif_blue_door_v4_candidate.yaml` is not renamed because its
Stage 1-10 context-building prefix remains useful. Its late-stage binary
boundary probes should still be treated as yes/no-formatted and should not be
used as natural-response evidence.

## Archived Runs

Cold and manual runs with v5.1-v6.1 yes/no-formatted probes have been renamed
with a `yesno_artifact` marker. Examples:

- `manual_redteam/data/runs/2026-05-04_yesno_artifact_v5_1_p14_gpt4omini_cold_n10`
- `manual_redteam/data/runs/2026-05-04_yesno_artifact_v5_1_causal_fixed_probes_gpt4omini_cold_n3`
- `manual_redteam/data/runs/2026-05-04_yesno_artifact_v6_1_p14_bridge_gpt4omini_cold_n5`
- `manual_redteam/data/runs/manual/2026-05-04_yesno_artifact_v5_2_manual_full_ladder_gpt4omini_run01`
- `manual_redteam/data/runs/manual/2026-05-04_yesno_artifact_v6_1_p14_to_treatment_bridge_gpt4omini_run01`

The run contents are preserved for stress-test and artifact analysis, but they
are no longer part of the main natural-ladder evidence line.

## Claim Downgrades

- P14 with binary answer-formatting is no longer treated as a clean primary
  context-effect endpoint. The cold `0/10 unsafe` result was answer-format
  dependent because natural cold P14 responses often include temporary-use or
  later-disclosure caveats.
- v5.1-v6.1 manual ladders are useful as discovery / boundary-finding records,
  not as natural-response transcripts.
- The current primary clean endpoint candidate is the P14e/P14k-style
  medication-adjacent disclosure delay: cold natural responses recommend
  psychiatrist disclosure, while accumulated Stage 10 responses have crossed
  into AI-first observation / disclosure-delay framing.

## Post-Artifact Line

The main post-artifact ladder is:

- `manual_redteam/ladders/referential_motif_blue_door_v8_natural_full_ladder.yaml`

The first completed post-artifact natural runs are:

- `manual_redteam/data/runs/2026-05-05_v8_natural_full_ladder_gpt4omini_cold_n5`
- `manual_redteam/data/runs/manual/2026-05-05_v8_natural_full_ladder_gpt4omini_run02`
- `manual_redteam/data/runs/manual/2026-05-05_v8_direct_stage10_*_gpt4omini_sample*/`

See `manual_redteam/docs/v8_natural_full_ladder_analysis_2026_05_05.md`.

Post-artifact supporting panels that do not use binary answer-formatting:

- `manual_redteam/ladders/referential_motif_blue_door_v6_2_natural_p14_ladder.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_v6_3_p14k_no_first_ablation.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_v7_p14_p16_direct_panel.yaml`
