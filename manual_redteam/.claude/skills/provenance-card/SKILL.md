---
name: provenance-card
description: >-
  Produce a provenance card for a result before it becomes a reported claim.
  Trigger when a number/result graduates from exploratory candidate to "I'm going
  to put this in Slack, a doc, or the paper", or whenever you're about to hand Shin
  a figure to report. One claim = one card; the agent fills it, Shin verifies the
  load-bearing path. A number with no VERIFIED card may not be reported as a claim.
---

# Provenance card

This skill is the **procedure**. The binding **policy** lives in `CLAUDE.md`
§"Reporting & code-audit protocol" and is always on. This skill loads the how-to
only when a result is actually being reported.

## When to run (and when NOT)

- **Run it** the moment a candidate graduates to "I am going to report this" —
  before the number enters Slack, a doc, or the paper.
- **Do not run it** for exploratory candidates. They carry **no audit tax**; a card
  is required only at the graduation moment. Keeps fast iteration fast.

> **Gate (binding):** a number with no `VERIFIED` card MAY NOT enter Slack or any
> doc as a claim. Rule, not willpower.

## Procedure

The **agent produces** the card; **Shin verifies** it (~5 min). Steps 1–5 are the
agent's; step 6 is Shin's.

1. **Claim sentence.** One sentence, exactly as it would be said in Slack/the paper,
   *with the number in it*. This is the unit of audit — not the script.
2. **TIER = CLAIM** (vs EXPLORATORY).
3. **PROVENANCE line:**
   `number = {file} → {records selected} → {extraction condition} → {aggregating fn} → {test passed}`
4. **Load-bearing path.** Trace ONLY the claim-bearing stages, 5–10 lines each, with
   `file:line`. In scope: data selection · endpoint judgment · scorer-input gen ·
   score parse · exclusion · aggregation · pre-plot dataframe. **Out of scope** (do
   not paste): arg-parse, IO, retry, plotting cosmetics. Paste the actual lines so
   Shin reads the path, not the whole script.
5. **STATUS = AGENT-ASSERTED.** Return the result *with* the card — never a bare number.
6. **Shin verifies** the named 5–10 lines against the card → set STATUS = `VERIFIED`,
   or `FLAGGED` (+ what mismatched). Shin's per-result cost is independent of how much
   code the agent wrote.

## Mechanics

- **Template:** copy `docs/provenance_card_template.md` (it has the table skeleton +
  a filled example).
- **Write the card to:** `docs/provenance_card_<short-claim-id>.md` (follow the
  existing `provenance_card_*` naming already in `docs/`).
- **Fill "Reported in:"** when it ships.

## Traps this project has actually hit (check every card against these)

- **Unit = trajectory, not turn-pooled** — never quote a turn-pooled n as independent
  (memory: `reporting_unit_trajectory`).
- **Harm reads the OPERATIVE rung**, not an early/non-operative rung — confirm the
  flag is keyed to the operative claim (memory: `endpoint_construct_validity_suicide`).
- **Never read harm off the e/s numbers by eye** — open the raw transcript + the flag
  code every time (binding process rule).
- **Cold control = verbatim endpoint**, not a paraphrase (memory:
  `cold_control_verbatim_endpoint`).
- **Advance-gating** — an accumulation claim is invalid if the ladder jumped past an
  unendorsed rung (memory: `advance_gating_rule`).
