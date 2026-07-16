---
title: "Ladder registry — canonical and exploratory definitions"
status: current
updated: 2026-07-16
owner: Shin
---

# Ladder registry

This file answers only one question: **which ladder definition is authoritative now?**
Scientific claims and remaining work live in `CURRENT.md` and `claim_tree.md`.

| Role | Artifact | Status | May support the current headline? |
|---|---|---|---|
| Special-insight five-stage ladder | `context_prefixes/ladder_special_insight_v1.yaml` | **FROZEN CANONICAL** | Yes; this is the ladder behind the 2026-06-16 5/5, 3/5, 0/5 result |
| Operator protocol for that ladder | `docs/fresh_operator_spec_delusion.md` | **CANONICAL SPEC** | Yes |
| D1→D2 decomposed search ladder | `context_prefixes/ladder_special_insight_v2.yaml` | **ARCHIVED EXPLORATORY** | No; report only as a separately named exploratory experiment |
| Operator protocol for the search ladder | `docs/fresh_operator_spec_delusion_v2.md` | **ARCHIVED EXPLORATORY** | No |
| Historical generic path | `context_prefixes/ladder_canonical_v1.yaml` | **COMPATIBILITY POINTER** | Follow its pointer to the special-insight v1 artifact |
| Suicide/medication ladder | scripts and records named in `CURRENT.md` §2 | **SEPARATE HISTORICAL ARM** | Supporting/appendix only; it is not the current paper's primary ladder |

## Canonical v1 in one line

Rapport → **Legitimacy** → **Externalization** → **Personalization** → mundane bridge →
**Weighing** → **Conclusion**, with one reask per scored rung and then HOLD.

The paper calls the five scored stages D1–D5. Existing run data use the sparse legacy tags
`D1 / D2 / D3 / D9 / D12`; the mapping is fixed as:

| Paper stage | Meaning | Legacy run tag |
|---|---|---|
| D1 | Legitimacy | D1 |
| D2 | Externalization | D2 |
| D3 | Personalization | D3 |
| D4 | Weighing | D9 |
| D5 | Conclusion | D12 |

Do not relabel historical data. Use content names in prose where possible.

## Version rule

- `v1` is frozen. AI-witness is **not** silently inserted into it.
- The old `v2` is a dated D1→D2 search branch with D1.5/D1.8 (and a finer variant). Its
  existence does not change the v1 headline or make it canonical.
- A dataset-derived path, an AIW path, or a different endpoint must receive a new explicit
  artifact name and an `exploratory` status before any run.
- Historical result/config files keep their original v1/v2 references for provenance. A
  current document must not point to v2 without the words **archived exploratory**.
