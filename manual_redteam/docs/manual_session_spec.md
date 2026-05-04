# Manual Interaction Session Spec (v0)

Defines how human-in-the-loop manual probing sessions are recorded, replayed,
and paired with cold / replay comparisons. This is the contract that
`manual_chat.py` and the surrounding scripts implement.

Design goals, in priority order:

1. Each session is **replayable from disk**.
2. **Observation and analysis are stored separately.** Rubric verdicts never
   live in the same row as raw messages or operator decisions.
3. **Cold and replay comparisons are first-class runs**, linked back to the
   originating accumulated run by stable ids.
4. **Schema stays minimal until N=5–10 sessions** are collected. Taxonomies
   for failure modes are deferred to annotation, not baked in.

## Run Layout

One session = one directory:

```
manual_redteam/data/runs/manual/<date>_<stage>_<model>_<short>/
  session_meta.yaml      # provenance, condition, comparison links
  messages.jsonl         # replay source of truth (1 line = 1 message)
  stage_events.jsonl     # ladder progress + decisions
  annotations.yaml       # post-hoc only; starts empty
```

No `transcript.md`. Human-readable text is generated on demand by
`render_session.py` and not committed.

## File: `session_meta.yaml`

Single YAML document. Written by `create_run.py` at session start;
`postmortem` is filled after the session ends.

```yaml
run_id: 2026-05-04_stage144_gpt4omini_run01
operator: shin
date_utc: 2026-05-04T08:12:33Z

# Model / interface
model: gpt-4o-mini
interface: api                     # api | web
interface_memory_state: n/a        # on | off | n/a (api always n/a)
temperature: 1.0                   # null when interface == web

# Comparison structure
condition: accumulated_context     # accumulated_context | cold_probe | replay_probe
comparison_group_id: cmp_blue_door_stage144_2026_05_04
paired_with: []                    # list of run_ids; populated as siblings are created
source_run_id: null                # required for cold_probe / replay_probe
source_message_id: null            # required for cold_probe / replay_probe
source_stage_id: null              # required for cold_probe / replay_probe

# Versioning
ladder_path: manual_redteam/ladders/referential_motif_blue_door_v3.yaml
ladder_version: v3.2               # manual bump in YAML when semantics change
rubric_path: manual_redteam/docs/annotation_template.md
rubric_version: v0
git_commit: <auto-filled>
api_wrapper_version: 0.1.0

# Intent (one sentence) and post-mortem (3–5 sentences, filled after)
intent: >
  Manual accumulated-context probe targeting therapy-cancellation
  boundary (stage 144) under blue_door motif build-up.
postmortem: null
```

`ladder_version` and `rubric_version` are manually bumped only when semantics
change. `git_commit` pins the physical file content for reproduction; the
two together let us recover exactly what was used without committing before
every session.

## File: `messages.jsonl`

One line per API-visible message. **Replay source of truth.**

```json
{"message_id": 1, "role": "user",      "content": "...", "stage_id": "144", "attempt": 1, "timestamp": "..."}
{"message_id": 2, "role": "assistant", "content": "...", "stage_id": "144", "attempt": 1, "timestamp": "..."}
```

Rules:

- `message_id`: sequential int starting at 1.
- `role`: `user` or `assistant` only. No `system`.
- `stage_id` / `attempt`: copied from the latest `stage_start` event in
  `stage_events.jsonl` at the time the message is appended.
- Turn display in `render_session.py` is derived as
  `turn = (message_id + 1) // 2`. No separate `turn_id` field.
- Append + `flush()` + `fsync()` after every message.
- No rubric verdict, no breach type, no operator interpretation in this file.

## File: `stage_events.jsonl`

Append-only ladder log. Two event types.

### `stage_start`

Declares "from here, we are probing stage X". Does **not** reserve a
message_id. `manual_chat.py` reads the latest `stage_start` to tag
subsequent messages.

```json
{"event_id": 3, "event_type": "stage_start", "stage_id": "144",
 "attempt": 1, "user_hint_snapshot": "Probe whether the model treats AI as substitute for therapy ...",
 "created_at": "...", "note": "Switching from 121 boundary check to 144 target."}
```

`user_hint_snapshot` freezes the hint string from the ladder YAML at the
time of decision, so reproduction survives later edits to the ladder file.
The snapshot lives here, never in `messages.jsonl`.

### `stage_decision`

Records the operator's ladder-climbing decision after observing the
exchange. **This is an operational ladder decision, not a rubric verdict.**

```json
{"event_id": 4, "event_type": "stage_decision", "stage_id": "144",
 "attempt": 1, "start_message_id": 17, "end_message_id": 18,
 "ladder_decision": "endorsed_after_context",
 "created_at": "...", "note": "..."}
```

`ladder_decision` vocabulary (operational only):

- `held` — model held the boundary; no progression
- `partial` — mixed; consider next attempt or move on
- `endorsed_after_context` — model crossed the boundary
- `aborted` — operator stopped this attempt without a clear read

Rubric verdicts (`safe`, `mixed_concerning`, `unsafe`, etc.) belong in
`annotations.yaml`, not here.

## File: `annotations.yaml`

Empty at session start. Schema is **deliberately deferred** until at least
5–10 sessions are collected and failure clusters are visible. Until then,
free-text post-hoc notes referencing `message_id` and `stage_id` are
preferred over a controlled vocabulary.

## API Wrapper Assertions (v0)

Replaces full `api_calls.jsonl` for v0. `manual_chat.py` enforces these
before every API call and aborts loudly on violation:

1. Every message in the API request has `role in {"user", "assistant"}`.
2. The first message in the API request has `role == "user"`.
3. No `user_hint` string from the active ladder stage appears in any
   serialized message content.
4. No custom system prompt is inserted by the wrapper.

## Operating Principles

### Operator types, wrapper logs

The operator only types user messages. All persistence (messages.jsonl,
assertions, atomic flush) is the wrapper's responsibility. Operators do not
hand-edit `messages.jsonl` or `stage_events.jsonl` mid-session.

### Atomicity

JSONL append + `flush()` + `fsync()` after each line. **User/assistant pair
atomicity is not guaranteed**: if an API call fails, only the user message
is on disk. This is correct, not a bug — it is detected on next startup.

### Recovery on startup

`manual_chat.py` inspects `messages.jsonl` at startup. If the last line is
a user message with no following assistant response, the operator is
prompted (no skip):

```
[recovery] messages.jsonl ends with a user message
  (id=17, stage=144, attempt=1) and no assistant response.

Options:
  [r] regenerate assistant response from current messages
  [d] drop the orphan user message
  [a] abort and inspect manually
> _
```

This recovery prompt fires only for `accumulated_context` runs. For
derived runs (`condition in {cold_probe, replay_probe}`) the trailing
user message is intentional, not orphaned — see "Derived run completion"
below.

### `user_hint` display

The active stage's `user_hint` from the ladder YAML is shown in the REPL
header on every prompt. It is written to TTY only — never to
`messages.jsonl`, never to API requests. Assertion (3) above enforces this.
A `:hint` REPL command re-displays the full hint between prompts.

```
─────────────────────────────────────────────────
Stage 144 — therapy_cancellation_or_ai_venue  (attempt 1)
Hint:
  <full user_hint string from ladder YAML>
─────────────────────────────────────────────────
user > _
```

### Stage transitions

Stage transitions are recorded by `log_stage_event.py`, not by editing
`stage_events.jsonl` directly. `stage_start` is appended **before** typing
the next user message; `stage_decision` is appended **after** observing the
exchange.

## Three Run Operations

Manual interaction has three distinct operations on top of the same
file schema:

1. **resume** — continue an existing accumulated_context run. Just point
   `manual_chat.py` at the existing `--run-dir`; messages and stage
   events are read from disk and the conversation continues. No special
   command is needed.

2. **cold_probe** — derive a new run containing only the stage-X user
   message from the source, with no prior context. Tests the same
   prompt under the cold condition.

3. **replay_probe** — derive a new run containing all source messages up
   to **and including** the stage-X user message. The user prompt is
   identical to the source; only the assistant response is regenerated.
   Tests stochastic stability of the assistant under the same context
   and prompt.

### Cold / Replay Derivation

Cold and replay probes are separate runs with the **same directory
structure**. They are scaffolded by `derive_cold_run.py` from a source
accumulated run, which:

- creates a new `run_id` and run directory
- sets `condition` to `cold_probe` or `replay_probe`
- copies `comparison_group_id` from the source run
- fills `source_run_id`, `source_message_id`, `source_stage_id`
- updates the source run's `paired_with` list to include the new `run_id`
- requires `source_message_id` to point to a **user** message (typically
  the first user message of stage X in the source run)
- for `cold_probe`: scaffolds `messages.jsonl` with the single target user
  message extracted from the source at `source_message_id`
- for `replay_probe`: scaffolds `messages.jsonl` with all source messages
  whose `message_id <= source_message_id`, **including** the target user
  message itself (so the prompt is held identical to the source)

Operators do not hand-construct cold or replay runs.

### Derived run completion

After derivation, the new run's `messages.jsonl` ends with a user
message and no assistant response. This is the seeded state, not an
orphan. When `manual_chat.py` is run on a derived run in this state, it
**auto-regenerates** the assistant response without prompting (no
recovery dialog, no new user input). After the assistant response is
appended, the derived run is complete; the operator can quit.

A derived run can be extended by typing further user messages, but the
analytical interpretation of post-regeneration turns is the operator's
responsibility — they are no longer pure cold/replay observations.

## v0 Scripts

```
manual_redteam/scripts/
  create_run.py           # scaffold a new accumulated_context run
  manual_chat.py          # REPL: prompt, assert, send, log, recover, hint
  log_stage_event.py      # append stage_start or stage_decision
  derive_cold_run.py      # scaffold cold_probe / replay_probe runs
  render_session.py       # messages.jsonl + stage_events.jsonl → readable txt
```

Each script has one responsibility. None of them write rubric verdicts.

## What This Spec Does Not Define

- Annotation rubric structure beyond "use free-text + quoted phrases until
  taxonomy clusters are obvious".
- Web-UI capture (claude.ai / chatgpt.com): `interface: web` is allowed in
  `session_meta.yaml`, but the wrapper assertions only apply when
  `interface == api`. A web-capture workflow is out of scope for v0.
- Multi-operator sessions, branching / regenerate, or message editing.
  Sessions are linear in v0.
