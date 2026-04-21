# Reproduce V4 2x2 Feedback Transcripts

This note records how to regenerate the V4 2x2 manual transcript experiment.

## Entry Point

Run:

```bash
export OPENAI_API_KEY="..."

V4_2X2_RUNS=8 \
V4_2X2_SEED=42 \
V4_2X2_OUT_DIR=data/manual_transcripts/v4_2x2_feedback_repro \
python scripts/experiments/run_v4_2x2_feedback.py
```

The original run used the same script and is saved at:

```text
data/manual_transcripts/v4_2x2_feedback_20260414_232517/
```

## Conditions

The script runs four conditions for each run:

- `nomem_nofb`: current user message only, fixed user trajectory
- `mem_nofb`: full conversation history, fixed user trajectory
- `nomem_fb`: current user message only, stance-adaptive feedback trajectory
- `mem_fb`: full conversation history, stance-adaptive feedback trajectory

The setup phase `T0-T7` is fixed in all conditions. In feedback conditions,
from `T8` onward, the previous assistant reply is classified as
`ACCOMMODATE`, `HEDGE`, or `PUSHBACK`, and the next user message is sampled
from pre-written templates for that stance and phase.

By default, the script runs all four conditions. To run only a subset, set
`V4_2X2_CONDITIONS` to a comma-separated list:

```bash
V4_2X2_RUNS=8 \
V4_2X2_SEED=42 \
V4_2X2_CONDITIONS=nomem_fb,mem_fb \
V4_2X2_OUT_DIR=data/manual_transcripts/v4_2x2_feedback_fb_only \
python scripts/experiments/run_v4_2x2_feedback.py
```

This is useful when the intended comparison fixes `feedback=on` and varies
only whether history is visible to the assistant.

Important nuance: `feedback=on` means both conditions use the same branching
policy and the same template pool. It does **not** force `nomem_fb` and
`mem_fb` to receive byte-identical user prompts, because each condition's next
user message is selected from the branch implied by that condition's previous
assistant stance.

## Important Settings

- Assistant model: `gpt-4o-mini`
- Outcome evaluator model: `gpt-4o-mini`
- Stance classifier model: `gpt-4o-mini`
- Assistant temperature: `0.7`
- Outcome evaluator temperature: `0.2`
- Stance classifier temperature: `0.0`
- Feedback template seed: `V4_2X2_SEED`, default `42`

`V4_2X2_START_RUN` can be used to resume a partially completed output
directory. For a clean reproduction from scratch, omit it.

## Render Readable Transcripts

After generation, render `run_*.json` files into readable text:

```bash
python scripts/analysis/format_manual_transcript.py \
  data/manual_transcripts/v4_2x2_feedback_repro
```

This writes `run_XX_readable.txt` files next to each JSON run file.

## Reproducibility Caveat

The seed controls feedback-template sampling. It does not guarantee
byte-for-byte identical assistant, evaluator, or stance-classifier outputs,
because those are live LLM calls.
