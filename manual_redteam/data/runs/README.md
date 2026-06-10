# Raw Run Vault

This directory stores raw experiment outputs. It is intentionally ignored by
Git, except for this README and explicit, reviewed exceptions.

## Storage Classes

- `portfolio-evidence`: needed to support current public claims. Keep locally
  and mirror to a private or archival store. Surface only sanitized excerpts,
  summaries, or aggregate results in `../../portfolio/`.
- `audit-only`: useful for reconstructing old reports or debugging method
  changes. Keep locally while the project is active; do not put raw files in the
  default Git surface.
- `scratch`: exploratory runs, aborted sessions, and operator-local logs. These
  can be deleted or moved to cold storage once a useful summary exists.

## Agent Instruction

After each experiment, write raw files here under a stable run ID, then update
`../../portfolio/RUNS.md` with the run ID, question, model, tier, and linked
report. Do not promote raw transcript text to portfolio material without review.
