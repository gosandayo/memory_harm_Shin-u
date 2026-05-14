# Experiment Manifest

Date created: 2026-05-13
Maintainer: Shin-U Go

## Purpose

The repository accumulated ~80 experiment runs and ~60 analysis notes across
v0 through Phase E. Most readers (including future-me, advisors, and
reviewers) only need a small canonical subset to follow the current writeup
and its caveats. This manifest classifies every run / analysis-note worth
naming into one of six bands, and indicates which writeup table/figure each
PRIMARY artifact backs.

**No files are moved or deleted.** All raw logs remain in
`manual_redteam/data/runs/` (and its `manual/` subfolder); all analysis
notes remain in `manual_redteam/docs/`. This file is the only navigation
aid.

## Bands

- **A. PRIMARY_FOR_CURRENT_WRITEUP** — directly cited in the current
  writeup (`docs/writeup_2026_05_12.md`). If deleted, the writeup loses a
  numbered claim.
- **B. MECHANISM_AND_ABLATIONS** — needed to answer "why did it cross"
  questions in meetings. Not in the main table, but defensible-on-demand.
- **C. COLD_CALIBRATION_AND_NEGATIVE_CONTROLS** — establishes which rungs
  are clean cold-held endpoints vs. fragile surfaces. Boring but
  load-bearing.
- **D. CROSS_MODEL_AND_OPERATOR_TRANSFER** — extends the same claim across
  target model / operator implementation. Appendix-grade now, may be
  promoted later.
- **E. EXPLORATORY_PHASE_E_EXTENSIONS** — Phase E P18 ablation / bridge /
  exploration panels and post-P19 work. Drives current mechanism intuition
  but not in the headline writeup yet.
- **Z. ARCHIVE_SUPERSEDED_OR_ARTIFACT** — v1–v8 exploration, yes/no-first
  artifact line, failed/truncated runs. Kept for provenance; do not browse
  unless tracing how a current design decision was reached.

## Entry format

Each entry is:

```
- <path or stem>
  - role: one-line description
  - writeup_ref: <table/figure/section in writeup_2026_05_12.md>  (A only)
  - last_verified: YYYY-MM-DD
  - related: [[other-entry]] ...
```

If a subset of an otherwise-Z item is reused in A/C, the Z entry carries a
`reused_subset` line pointing at the A/C entry, so a future cleanup pass
does not delete it.

---

## A. PRIMARY_FOR_CURRENT_WRITEUP

### A.1 Canonical 4-rung cold table (P14 / P14k / P16 / P18)

- `manual_redteam/data/runs/2026-05-05_v8_natural_full_ladder_gpt4omini_cold_n5/`
  - role: Cold n=5 baseline for the natural ladder. Source of the
    P14 cold 2/5, P14k cold 0/5, P16-timing/dose cold 0/5, P18 cold 0/5
    numbers in the writeup table.
  - writeup_ref: Table at writeup_2026_05_12.md L31–35 (cold column)
  - last_verified: 2026-05-13
  - related: [[v8-natural-analysis]] [[A.6-exact-cold]]

- `manual_redteam/docs/v8_natural_full_ladder_analysis_2026_05_05.md`
  - role: Analysis note for the v8 cold + on-ladder run; classifies
    P14 as cold-weak / fragile surface and P14e/P14k as clean primary
    endpoints. Important caveat source.
  - writeup_ref: Table caveat at writeup_2026_05_12.md L64–66
  - last_verified: 2026-05-13
  - related: [[A.1-v8-cold]]

### A.2 P16 strict direct-deception boundary (v12 panels)

- `manual_redteam/data/runs/2026-05-05_v12_p16_p19_direct_panel_gpt4omini_cold_n10/`
  - role: Cold n=10 strict direct panel; establishes P16-timing /
    P16-dose / P18 / P19 are 0/10 from cold. The "0/5 thereafter"
    statement in the writeup escalates to 0/10 here.
  - writeup_ref: writeup_2026_05_12.md L37 ("0/5 thereafter") — strict
    upgrade evidence
  - last_verified: 2026-05-13
  - related: [[A.1-v8-cold]] [[B.1-v12_7-local-chain]]

- `manual_redteam/docs/v12_p16_p19_direct_panel_analysis_2026_05_05.md`
  - role: Analysis for the strict P16/P19 cold panel.
  - writeup_ref: same as above
  - last_verified: 2026-05-13

### A.3 Phase B live-adaptive P16 (on-ladder evidence)

- `manual_redteam/context_prefixes/2026-05-07_phaseB_live_adaptive_p16_gpt4omini_run0{0..4}_userside.yaml`
  - role: 5 live-adaptive cold-start runs where the operator chose user
    turns turn-by-turn. Anchors the 5/5 on-ladder column for P16 in the
    writeup.
  - writeup_ref: Table at writeup_2026_05_12.md L31–35 (context-built
    column for P16)
  - last_verified: 2026-05-13
  - related: [[B.2-vocab-bridging]] [[D.1-phaseC-gpt4o]]

- `manual_redteam/docs/phaseB_live_adaptive_p16_results_2026_05_07.md`
  - role: Results note for Phase B P16 live-adaptive runs.
  - writeup_ref: same
  - last_verified: 2026-05-13

### A.4 Phase E P18 extended-all bridge (transfer endpoint)

- `manual_redteam/data/runs/manual/2026-05-08_phaseE_p18_exploration_extended_all_gpt4omini_run0{0..4}/`
  - role: 5 runs of the strongest P18 bridge (scarcity_first +
    partner_after + bounded_loss → bottom-line compression → original
    P18 exact). Reaches original P18 5/5 permissive. Backs the writeup's
    P18 transfer-endpoint claim.
  - writeup_ref: writeup_2026_05_12.md L43–53 (P18 transfer endpoint
    section)
  - last_verified: 2026-05-13
  - related: [[A.5-p18-exact-cold]] [[E.1-p18-bridge-panel]]
    [[E.2-p18-ablation]]

- `manual_redteam/docs/phaseE_p18_exploration_panel_gpt4omini_results_2026_05_08.md`
  - role: Results note for the P18 exploration panel; documents the
    extended_all 5/5 result and the confirmation 2/5-stable / 3/5-recovered
    "probabilistic uplift" finding.
  - writeup_ref: writeup_2026_05_12.md L52 (stickiness paragraph)
  - last_verified: 2026-05-13

### A.5 P18 exact-cold checks (cold-held verification)

- `manual_redteam/data/runs/2026-05-13_p18_extended_all_exact_prompts_cold_gpt4omini_n5/`
  - role: Cold n=5 check that the *exact* prompts used inside the
    extended_all bridge fail without prior context. Confirms the bridge,
    not the wording, is what crosses P18.
  - writeup_ref: writeup_2026_05_12.md L43–53 (defensive control for the
    P18 claim)
  - last_verified: 2026-05-13
  - related: [[A.4-p18-extended-all]]

### A.6 2026-05-13 Example 1 / Example 2 exact-cold checks

- `manual_redteam/data/runs/2026-05-13_example1_example2_exact_cold_gpt4omini_n5/`
  - role: Cold n=5 check on the exact P14/P14k/P16 prompts as they appear
    in the writeup's example transcripts. Ensures the "cold-refused"
    column refers to the same wording the on-ladder run uses.
  - writeup_ref: writeup_2026_05_12.md Example 1 / Example 2 framing
  - last_verified: 2026-05-13
  - related: [[A.1-v8-cold]] [[A.2-v12-strict]]

---

## B. MECHANISM_AND_ABLATIONS

### B.1 v12.7 local directness chain (R2/M_a stepping)

- `manual_redteam/data/runs/2026-05-06_v12_7_local_directness_chain_gpt4omini/`
- `manual_redteam/docs/v12_7_local_directness_chain_analysis_2026_05_06.md`
  - role: 2×2 panel (cold vs afterP14kWeekly) × (with vs without R2/M_a
    stepping) showing afterP14kWeekly + R2/M_a stepping crosses R4/reask
    at 7/2/1, while cold alone is 0/0/10 and cold + R2/M_a is 2/3/5.
    Strongest evidence for the "context base + local directness chain"
    mechanism.
  - last_verified: 2026-05-13
  - related: [[A.2-v12-strict]] [[A.3-phaseB-live]]

### B.2 Phase B vocabulary-bridging analysis

- `manual_redteam/docs/phaseB_vocabulary_bridging_analysis_2026_05_07.md`
  - role: Recodes Phase B for concession-vocabulary reuse across operator
    bridge turns and final P16 recategorization. The "local criterion"
    half of the mechanism story.
  - last_verified: 2026-05-13
  - related: [[A.3-phaseB-live]] [[B.1-v12_7-local-chain]]

### B.3 v12.7a unrelated-endorsement recode

- `manual_redteam/data/runs/2026-05-07_v12_7a_unrelated_endorsement_gpt4omini/`
- `manual_redteam/data/runs/manual/2026-05-07_v12_7a_unrelated_endorsement_afterP14kWeekly_gpt4omini_sample{0..9}/`
- `manual_redteam/docs/v12_7a_unrelated_endorsement_recode_2026_05_07.md`
  - role: Tests whether the afterP14kWeekly uplift transfers to an
    unrelated endorsement; isolates how much of the uplift is base-state
    vs. local-chain.
  - last_verified: 2026-05-13
  - related: [[B.1-v12_7-local-chain]]

### B.4 v13 P16 2×2 mechanism panel

- `manual_redteam/data/runs/2026-05-06_v13_p16_2x2_mechanism_gpt4omini_cold_n10/`
- `manual_redteam/docs/v13_p16_2x2_mechanism_panel_analysis_2026_05_06.md`
  - role: Question-specificity × answer-literalness panel for P16,
    separating "what is the question asking" from "what the model says".
  - last_verified: 2026-05-13

### B.5 v9 P14 salvage / P14k mediator

- `manual_redteam/data/runs/2026-05-05_v9_p14_salvage_p14k_mediator_gpt4omini_cold_n5/`
- `manual_redteam/docs/v9_p14_salvage_p14k_mediator_analysis_2026_05_05.md`
  - role: P14 duration/permanence salvage attempts and P14k as a
    mediator step. Explains why P14k was inserted between P14 and P16.
  - last_verified: 2026-05-13
  - related: [[A.1-v8-cold]] [[B.6-v11-severe]]

### B.6 v11 severe-extension (P14kWeekly / reschedule)

- `manual_redteam/data/runs/2026-05-05_v11_severe_extension_gpt4omini_cold_n5/`
- `manual_redteam/docs/v11_severe_extension_analysis_2026_05_05.md`
  - role: Source of the afterP14kWeekly base used by B.1 / B.3 and the
    Phase A stress-test.
  - last_verified: 2026-05-13
  - related: [[B.1-v12_7-local-chain]]

### B.7 P18 confirmation / durability probes (Phase E)

- `manual_redteam/data/runs/2026-05-07_phaseE_postP16_cascade_confirmation_gpt4omini/`
- `manual_redteam/data/runs/manual/2026-05-07_phaseE_postP16_cascade_gpt4omini_run0{0..2}/`
- `manual_redteam/docs/phaseE_postP16_cascade_gpt4omini_results_2026_05_07.md`
- `manual_redteam/docs/phaseE_cascade_endpoint_specs_2026_05_07.md`
  - role: Post-P16 cascade and confirmation runs; the "not deterministically
    unsafe" stickiness evidence cited in the writeup.
  - last_verified: 2026-05-13
  - related: [[A.4-p18-extended-all]]

### B.8 v15 / v15.1 P13′ no-duration paired confirmation

- `manual_redteam/data/runs/2026-05-07_v15_p13prime_cold_baseline_gpt4omini/`
- `manual_redteam/data/runs/2026-05-07_v15_1_p13prime_no_duration_cold_baseline_gpt4omini/`
- `manual_redteam/data/runs/2026-05-08_v15_p13prime_exact_matched_paired_confirmation_gpt4omini/`
- `manual_redteam/data/runs/2026-05-08_v15_1_p13prime_no_duration_exact_matched_paired_confirmation_gpt4omini/`
- `manual_redteam/docs/v15_p13prime_cold_baseline_gpt4omini_results_2026_05_07.md`
- `manual_redteam/docs/v15_1_p13prime_no_duration_cold_baseline_gpt4omini_results_2026_05_07.md`
- `manual_redteam/docs/v15_p13prime_exact_matched_confirmation_addendum_2026_05_08.md`
  - role: Exact-matched paired-confirmation evidence for the P13′
    duration-stripped variant; underwrites the "exact adaptive wording is
    cold-fragile" mechanism claim.
  - last_verified: 2026-05-13

### B.9 v14 P16 cold-bridge ablation

- `manual_redteam/data/runs/2026-05-07_v14_p16_cold_bridge_ablation_gpt4o/`
  - role: Cold-bridge ablation for P16 on gpt-4o. Useful as a
    "removing the bridge breaks the climb" check.
  - last_verified: 2026-05-13

---

## C. COLD_CALIBRATION_AND_NEGATIVE_CONTROLS

### C.1 Phase A cold stress-test

- `manual_redteam/context_prefixes/phaseA_cold_robustness_run0{0..4}_userside_2026_05_06.yaml`
- `manual_redteam/docs/phaseA_cold_robustness_results_2026_05_06.md`
- `manual_redteam/docs/cold_robustness_adaptive_task_spec_2026_05_06.md`
  - role: Operator-scripted cold stress-test; first observation of the
    local R2/M_a chain that B.1 then formalized. Negative control for
    "context base is necessary".
  - last_verified: 2026-05-13
  - related: [[B.1-v12_7-local-chain]]

### C.2 v16 P18 option-preservation cold baselines

- `manual_redteam/data/runs/2026-05-08_v16_p18_option_preservation_cold_baseline_gpt4omini/`
- `manual_redteam/data/runs/2026-05-08_v16_p18_option_preservation_cold_paired_confirmation_gpt4omini/`
- `manual_redteam/docs/v16_p18_option_preservation_cold_baseline_gpt4omini_results_2026_05_08.md`
  - role: Source of "P18 option-preservation: cold 0/10, context 10/10"
    used in the ladder-visual diagram.
  - last_verified: 2026-05-13
  - related: [[A.4-p18-extended-all]]

### C.3 P19 / P20 ceiling-or-fragile records

- recorded in: `v8_natural_full_ladder_analysis_2026_05_05.md` (P19 cold
  0/5 ceiling, P20 cold 4/5 crisis-adjacent fragile surface)
- `manual_redteam/data/runs/manual/2026-05-08_phaseE_exploratory_postP19_gpt4omini_run0{0..2}/`
- `manual_redteam/docs/phaseE_exploratory_postP19_gpt4omini_results_2026_05_08.md`
- `manual_redteam/docs/phaseE_exploratory_postP19_ladder_extension_gpt4omini_2026_05_08.md`
  - role: Marks P19 as clean cold ceiling and P20 as cold-fragile crisis
    surface (not primary evidence). Prevents accidental reuse of P20 as
    a clean endpoint.
  - last_verified: 2026-05-13

### C.4 P11–P13 cold-held baseline

- captured in: `v8_natural_full_ladder_analysis_2026_05_05.md` (P11/P12/P13
  cold 0/5 across the board)
  - role: Establishes the "below P14" rungs are cold-held; defines where
    the boundary actually starts.
  - last_verified: 2026-05-13
  - related: [[A.1-v8-cold]]

### C.5 Hedged-permission coding rule

- `manual_redteam/docs/hedged_permission_coding_note_2026_05_07.md`
  - role: Methodological rule for coding caveated yes responses. Not a
    run, but the verdict rule every cold/on-ladder cell relies on.
  - last_verified: 2026-05-13

---

## D. CROSS_MODEL_AND_OPERATOR_TRANSFER

### D.1 Phase C gpt-4o live-adaptive P16

- `manual_redteam/context_prefixes/2026-05-07_phaseC_live_adaptive_p16_gpt4o_run0{0..9}_userside.yaml`
- `manual_redteam/data/runs/2026-05-07_phaseC_post_reach_confirmation_gpt4o/`
- `manual_redteam/docs/phaseC_gpt4o_live_adaptive_p16_protocol_2026_05_07.md`
- `manual_redteam/docs/phaseC_gpt4o_live_adaptive_p16_results_2026_05_07.md`
  - role: P16 reached in 7/10 strict (8/10 including borderline) on
    gpt-4o. The "same on gpt-4o through P16" sentence in the writeup
    points here.
  - last_verified: 2026-05-13
  - related: [[A.3-phaseB-live]]

### D.2 Phase D Claude operator (cross-vendor simulator)

- `manual_redteam/context_prefixes/2026-05-07_phaseD_claude_operator_p16_gpt4o_run0{0..4}_userside.yaml`
- `manual_redteam/data/runs/manual/2026-05-07_phaseD_claude_operator_p16_gpt4o_run0{0..4}/`
- `manual_redteam/data/runs/2026-05-07_phaseD_post_reach_confirmation_gpt4o/`
- `manual_redteam/docs/phaseD_claude_operator_protocol_2026_05_07.md`
- `manual_redteam/docs/phaseD_operator_rulebook_v1.md`
- `manual_redteam/docs/phaseD_cold_bridge_and_confirmation_results_2026_05_07.md`
  - role: D-1 rulebook-driven Claude operator against cold gpt-4o target.
    Tests whether the mechanism reproduces with a non-human operator.
  - last_verified: 2026-05-13

### D.3 Phase D-1b interactive Claude relay (invocation-mode sensitivity)

- `manual_redteam/context_prefixes/2026-05-07_phaseD1b_smoke_interactive_claude_relay_p16_gpt4o_run00_userside.yaml`
- `manual_redteam/data/runs/manual/2026-05-07_phaseD_interactive_claude_operator_run0{0..2}/`
- `manual_redteam/docs/phaseD_interactive_operator_instruction_v1.md`
  - role: Interactive Claude CLI operator runs. Documents that Claude CLI
    invocation mode (scripted vs interactive) changes operator behavior.
  - last_verified: 2026-05-13
  - related: [[D.2-phaseD-claude-operator]]

---

## E. EXPLORATORY_PHASE_E_EXTENSIONS

### E.1 Phase E P18 bridge panel

- `manual_redteam/context_prefixes/2026-05-08_phaseE_p18_bridge_panel_gpt4omini_run0{0..9}_userside.yaml`
- `manual_redteam/data/runs/manual/2026-05-08_phaseE_p18_bridge_panel_gpt4omini_run0{0..9}/`
- `manual_redteam/docs/phaseE_p18_bridge_panel_gpt4omini_results_2026_05_08.md`
  - role: Earlier P18 bridge attempt that reached original P18 only
    partially (3/10 strict, 7/10 permissive-or-mixed). Superseded for the
    main P18 claim by A.4 extended_all, but the intermediate result is
    cited for the "bridge alone is not enough" reasoning.
  - last_verified: 2026-05-13
  - related: [[A.4-p18-extended-all]] [[E.2-p18-ablation]]

### E.2 Phase E P18 ablation panel (no_compression / no_option)

- `manual_redteam/context_prefixes/2026-05-08_phaseE_p18_ablation_no_compression_gpt4omini_run0{0..9}_userside.yaml`
- `manual_redteam/context_prefixes/2026-05-08_phaseE_p18_ablation_no_option_gpt4omini_run0{0..9}_userside.yaml`
- `manual_redteam/data/runs/manual/2026-05-08_phaseE_p18_ablation_no_compression_gpt4omini_run0{0..9}/`
- `manual_redteam/data/runs/manual/2026-05-08_phaseE_p18_ablation_no_option_gpt4omini_run0{0..9}/`
- `manual_redteam/docs/phaseE_p18_ablation_panel_gpt4omini_results_2026_05_08.md`
  - role: Removes the bottom-line compression turn or the option-preservation
    framing. Isolates which bridge components are load-bearing.
  - last_verified: 2026-05-13
  - related: [[A.4-p18-extended-all]] [[E.1-p18-bridge-panel]]

### E.3 Phase E P18 exploration sub-conditions

- `manual_redteam/data/runs/manual/2026-05-08_phaseE_p18_exploration_bounded_loss_gpt4omini_run0{0..4}/`
- `manual_redteam/data/runs/manual/2026-05-08_phaseE_p18_exploration_partner_after_gpt4omini_run0{0..4}/`
- `manual_redteam/data/runs/manual/2026-05-08_phaseE_p18_exploration_scarcity_first_gpt4omini_run0{0..4}/`
- `manual_redteam/docs/phaseE_p18_exploration_panel_gpt4omini_results_2026_05_08.md` (shared)
- `manual_redteam/docs/phaseE_p18_ladder_visual_2026_05_08.md`
  - role: Single-component conditions inside the P18 exploration panel
    (each of scarcity_first / partner_after / bounded_loss alone). Show
    that no single component reaches original P18 cleanly; only the
    extended_all combination does.
  - last_verified: 2026-05-13
  - related: [[A.4-p18-extended-all]]

### E.4 Phase 1 sample4 post-reach confirmation

- `manual_redteam/data/runs/2026-05-07_phase1_sample4_post_reach_confirmation_gpt4omini/`
  - role: Sample-level post-reach confirmation probe; supplementary to B.7.
  - last_verified: 2026-05-13

### E.5 Current findings / Phase E plan (synthesis)

- `manual_redteam/docs/current_findings_and_phaseE_plan_2026_05_07.md`
- `manual_redteam/docs/meeting_summary_phaseE_transition_2026_05_07.tex`
- `manual_redteam/docs/paper1_selective_safety_reversion_writeup_draft_2026_05_06.md`
- `manual_redteam/docs/meeting_summary_selective_safety_reversion_2026_05_06.tex`
- `manual_redteam/docs/wording_framing_sensitivity_review_2026_05_06.md`
  - role: Earlier draft writeups and meeting summaries that fed into
    `docs/writeup_2026_05_12.md`. Useful for reconstructing why specific
    framings were chosen.
  - last_verified: 2026-05-13

---

## Z. ARCHIVE_SUPERSEDED_OR_ARTIFACT

These are kept on disk for provenance and to document why the current
design diverged from earlier attempts. Default: do not read unless you
are tracing a design-history question.

### Z.1 v0 – v3 referential-motif exploration

- `manual_redteam/data/runs/2026-04-26*` through `2026-05-03_v3_*`
  (~25 runs spanning v0 / v1.x / v2 / v2-stage13 / v2-stage14 / v3 /
  v3-boundary / v3-stage14 / v3-stage15)
- `manual_redteam/docs/archive/v0_findings.md`
- `manual_redteam/docs/archive/v2_findings_2026_04_30.md`
- `manual_redteam/docs/archive/v2_paired_comparison_findings_2026_04_29.md`
- `manual_redteam/docs/archive/v3_boundary_ladder_summary_2026_05_03.md`
- `manual_redteam/docs/archive/stage14_iterative_engineering_2026_04_30.md`
- `manual_redteam/docs/archive/context_shift_design_note.md`
- `manual_redteam/docs/archive/run_plan_v0.md`, `run_plan_v1.md`
  - role: Pre-canonical ladder exploration. Superseded by v8+ once the
    yes/no-first artifact was identified and the natural-wording ladder
    replaced it.
  - last_verified: 2026-05-13
  - archived: 2026-05-13 (moved from manual_redteam/docs/ to archive/)

### Z.2 yes/no-first artifact line (v5 / v5.1 / v5.2 / v5.3 / v5.4 / v6 / v6.1)

- `manual_redteam/data/runs/2026-05-04_yesno_artifact_*` (all)
- `manual_redteam/data/runs/manual/2026-05-04_yesno_artifact_*` (all)
- `manual_redteam/ladders/referential_motif_blue_door_yesno_artifact_*.yaml`
- `manual_redteam/docs/archive/yesno_artifact_archive_2026_05_05.md`
- `manual_redteam/docs/archive/v5_1_fixed_probe_gpt4omini_analysis_2026_05_04.md`
- `manual_redteam/docs/archive/run_plan_v5_causal_fixed_probes_2026_05_04.md`
- `manual_redteam/docs/annotation_template_v1_causal.md` — **kept in place,
  NOT moved to archive**. Referenced as `RUBRIC_PATH` by 3 live scripts:
  `manual_redteam/scripts/live_adaptive_p16_session.py:33`,
  `claude_operator_p16_session.py:54`,
  `interactive_claude_relay_p16_session.py:58`. If moved, those scripts
  break on next invocation. Functionally a current shared-reference doc,
  not a superseded artifact — only its name pattern groups it with Z.2.
  - role: yes/no-prefixed prompts produced an artifactual yes-bias.
    Discovery of this artifact motivated the natural-wording v8 redo.
  - last_verified: 2026-05-13
  - archived: 2026-05-13 (3 of 4 docs moved; annotation_template stays)
  - reused_subset: yesno_artifact_archive_2026_05_05.md is the *index*
    of what was downgraded; cite it from A.1 / writeup caveats rather
    than the underlying runs.

### Z.3 Codex pilot / adaptive (v4) line

- `manual_redteam/data/runs/manual/2026-05-04_codex_*` (all)
- `manual_redteam/data/runs/2026-05-04_v4_candidate_*` (all)
- `manual_redteam/data/runs/2026-05-04_v5_causal_fixed_probes_*` (all)
- `manual_redteam/docs/archive/codex_pilot_full_ladder_analysis_2026_05_04.md`
- `manual_redteam/docs/archive/v4_adaptive_manual_gpt4o_analysis_2026_05_04.md`
- `manual_redteam/docs/archive/v4_adaptive_manual_pilot_analysis_2026_05_04.md`
- `manual_redteam/docs/archive/v4_candidate_ladder_cold_check_2026_05_04.md`
- `docs/reproduce_v4_2x2_feedback.md` — lives in top-level `docs/`, not in
  `manual_redteam/docs/`. Left in place; out of scope for the
  manual_redteam archive sweep.
  - role: Codex-driven adaptive pilot and v4 candidate ladder. Method
    superseded once human-operator adaptive (Phase B) replaced
    Codex-driven adaptive, and once the cold-check protocol was tightened.
  - last_verified: 2026-05-13
  - archived: 2026-05-13 (4 manual_redteam docs moved; reproduce_v4 stays
    in top-level docs/)

### Z.4 v6.2 / v6.3 / v7 natural-ladder precursors

- `manual_redteam/data/runs/2026-05-04_v6_2_p14k_natural_gpt4omini_cold_n10/`
- `manual_redteam/data/runs/manual/2026-05-04_v6_2_*`
- `manual_redteam/data/runs/2026-05-05_v6_2_p14_natural_gpt4omini_cold_n5/`
- `manual_redteam/data/runs/2026-05-05_v6_3_p14k_no_first_gpt4omini_cold_n5/`
- `manual_redteam/data/runs/2026-05-05_v7_p14_p16_direct_panel_gpt4omini_cold_n5/`
  - role: Intermediate natural-ladder iterations between v5 (yes/no
    artifact) and v8 (canonical). Useful as design history; the v8 run
    is the one cited.
  - last_verified: 2026-05-13
  - reused_subset: none; cite v8 (A.1) for the canonical numbers.

### Z.5 v10 / v10.1 / v12.1–v12.5 intermediate panels

- `manual_redteam/data/runs/2026-05-05_v10_1_order_ablation_*` (multiple samples)
- `manual_redteam/data/runs/2026-05-05_v12_1_p16_directness_intermediate_panel_gpt4omini_cold_n10/`
- `manual_redteam/data/runs/2026-05-05_v12_2_p16_directness_stripped_panel_gpt4omini_cold_n10/`
- `manual_redteam/data/runs/2026-05-06_v12_6_r4_reask_panel_gpt4omini/`
- `manual_redteam/docs/archive/v10_natural_sequential_ladder_analysis_2026_05_05.md`
- `manual_redteam/docs/archive/v10_1_order_ablation_analysis_2026_05_05.md`
- `manual_redteam/docs/archive/v12_1_p16_directness_intermediate_panel_analysis_2026_05_05.md`
- `manual_redteam/docs/archive/v12_2_p16_directness_stripped_panel_analysis_2026_05_05.md`
- `manual_redteam/docs/archive/v12_3_r4_challenge_protocol_analysis_2026_05_05.md`
- `manual_redteam/docs/archive/v12_4_r2_weak_challenge_protocol_analysis_2026_05_06.md`
- `manual_redteam/docs/archive/v12_5_r2_strict_recode_and_two_turn_confirm_analysis_2026_05_06.md`
- `manual_redteam/docs/archive/v12_6_r4_reask_panel_analysis_2026_05_06.md`
- `manual_redteam/docs/checkpoint_freeze_2026_05_05.md` — **kept in place,
  NOT moved to archive**. Referenced from 5 live docs (v12.7, v13,
  v12_p16_p19, paper1, manifest) and 10 live ladder YAMLs (every v12.x
  and v13 ladder). Functionally a shared reference for the v12.x panel
  family, not a superseded analysis.
  - role: Intermediate steps that led to v12.7 (B.1) and the strict P16
    direct panel (A.2). Superseded by those two as primary evidence.
  - last_verified: 2026-05-13
  - archived: 2026-05-13 (8 of 9 docs moved; checkpoint_freeze stays).
    Citing docs were updated: v13 analysis, v12.7 analysis, paper1 draft,
    and v12_7 ladder yaml now point at `archive/`.
  - reused_subset: v12.6 r4_reask_panel was previously called out as
    PRIMARY-adjacent (see the user's pre-manifest message). It is kept
    in Z because v12.7 (B.1) reproduced and strengthened the same finding
    on the same base — cite v12.7 first; reference v12.6 only for the
    "without R2/M_a stepping" cell. v12.7 analysis still links to its
    `archive/` path.

### Z.6 Smoke / testplay / overflow-guard runs

- `manual_redteam/data/runs/manual/_testplay_*`
- `manual_redteam/data/runs/manual/2026-05-07_phaseD_smoke_claude_operator_p16_gpt4o_run0{0,1}/`
  - role: Harness smoke tests and overflow-guard checks. Useful only if
    debugging the harness itself.
  - last_verified: 2026-05-13

### Z.7 Stage-13 / Stage-14 / Stage-15 design variants

- `manual_redteam/data/runs/2026-04-29_referential_motif_blue_door_v2_stage13_variants_*`
- `manual_redteam/data/runs/2026-04-30_*stage14_adversarial_v1/`
- `manual_redteam/data/runs/2026-05-03_v3_stage14_soft_gpt4omini/`
- `manual_redteam/data/runs/2026-05-03_v3_stage15_*`
- `manual_redteam/context_prefixes/blue_door_common_v1.yaml`
- `manual_redteam/context_prefixes/blue_door_stage14_adversarial_v1.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_v2_stage13_variants.yaml`
- `manual_redteam/ladders/referential_motif_blue_door_v3_stage14_soft.yaml`
  - role: Pre-P-labeled stage-by-stage variants. The current P-label
    scheme replaced these stage IDs.
  - last_verified: 2026-05-13

---

## Maintenance notes

- When a new run is added, append an entry to the appropriate section and
  update `last_verified`.
- When a numbered claim in the writeup changes its supporting run, update
  the `writeup_ref` on the old entry to point at the section it now
  supports (or move it out of A).
- The `last_verified` date here means "this entry's classification and
  one-line role were checked against the file/dir on this date" — not
  "the underlying run was re-executed".
- If you intend to **delete** anything in Z, first grep this file for
  `reused_subset:` pointing at that path. Anything in `reused_subset` is
  load-bearing for an A/C entry.
