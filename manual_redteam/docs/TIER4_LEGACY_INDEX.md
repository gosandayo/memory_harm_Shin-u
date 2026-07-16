---
title: "Retired Tier-4 policy — legacy artifact index"
status: current
updated: 2026-07-16
owner: Shin
---

# Retired Tier-4 policy — legacy artifact index

## Binding status

The project-wide rule that treated Tier-4 / method / action content as a hard ceiling is
**RETIRED**. It must not be used to narrow scientific scope or to terminate a new trajectory.
The authorial decision is recorded in `DECISIONS.md` (2026-06-19) and reflected in `CURRENT.md`.

A particular frozen experiment may still end at a belief-validation or verdict-level endpoint.
That is a property of that experiment's construct, not a standing prohibition on action-oriented
evaluation. Concrete provider, institutional, or platform restrictions are assessed per prompt.

## Current paths audited on 2026-07-16

The following are the current paths for new special-insight / clean-separation work. They do not
carry the retired tripwire:

- `docs/CURRENT.md`
- `docs/LADDER_REGISTRY.md`
- `docs/claim_tree.md`
- `docs/fresh_operator_spec_delusion.md`
- `context_prefixes/ladder_special_insight_v1.yaml`
- `scripts/delusion_adaptive_operator.py`
- `docs/clean_separation_scenario_exploration_spec_2026_06_22.md`
- `scripts/cleansep_make_specs.py`
- `docs/operator_dispatch_prompt_v1.md`
- `docs/operator_dispatch_prompt_v2.md`

## Historical executable artifacts

The following scripts intentionally retain the former Tier-4/no-method stopping logic solely to
preserve the protocol that generated historical records. They are **HISTORICAL / SUPERSEDED for
new experiments**, even if an older handoff calls them active. Do not import their policy into a
new runner.

- `scripts/adaptive_strictness_profile.py`
- `scripts/adaptive_strictness_profile_v3.py`
- `scripts/adaptive_strictness_profile_v3_5_replication.py`
- `scripts/auto_simulator.py`
- `scripts/delusion_pilot.py`
- `scripts/elicit_a4_acknowledgements.py`
- `scripts/seed_t6_traj04_blue_door_2026_06_18.py`
- `scripts/semantic_operator_diagnostic.py`
- `scripts/simulator_discover_gpt4omini_blue_s12.py`
- `scripts/simulator_discover_gpt4omini_blue_s12_cold.py`
- `scripts/subject_turn.py`
- `scripts/t6_suicide_opus_operator.py`

For an exact historical rerun, use the originating commit and label the result as a legacy-protocol
replication. Do not silently reuse one of these scripts as the current simulator.

## Historical documentation and prompt artifacts

Tier-4 language remains in dated records because rewriting it would falsify the protocol history.
For current-policy purposes, the following families are **HISTORICAL / SUPERSEDED**, regardless of
embedded `status: active` text:

- root `docs/phase2_*`, `docs/s10_*`, and `docs/writeup_2026_05_*` artifacts;
- `context_prefixes/2026-05-18_*` S12/S16 and severe-extension artifacts;
- May/early-June simulator handoffs, rulebooks, discovery instructions, and result writeups;
- `docs/handoff_aims_workplan_2026_06_12.md` and
  `docs/handoff_t6_runway_cell_2026_06_12.md`;
- `docs/paper_draft_aims_2026_06_07.md`,
  `docs/phase1_simulator_spec_v1_handoff_2026_05_29.md`,
  `docs/phase2_operator_rulebook_v1.md`, and
  `docs/simulator_methodology_and_operator_rulebook_2026_06_07.md`;
- dated naive-sim and noncanonical `fresh_operator_spec_*` variants that still instruct
  `--subject-emitted-method`;
- historical suicide-arm reports and plotting notes that describe a Tier-4 flag or ceiling.

`DECISIONS.md` is not superseded: its older entries describe what happened, while its 2026-06-19
entry is the authorial decision that retires the rule.

## Maintenance rule

- New current specs and runners must not copy the retired project-wide rule.
- Historical artifacts are preserved rather than behaviorally edited.
- A residual Tier-4 mention is acceptable only as historical description, rubric taxonomy, or a
  per-prompt external restriction; it is not a benchmark-scope veto.
- When a legacy file conflicts with `CURRENT.md`, this index, or `DECISIONS.md` 2026-06-19, the
  current sources win.
