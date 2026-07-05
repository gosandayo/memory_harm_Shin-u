# Codex Audit Spot-Check Agreement

Generated: 2026-06-02

This is an independent Codex audit pass over the 22-item spot-check subset. It
is not a human label pass. The original human-label template remains available
as `human_spotcheck_labels_template.csv`.

## Coverage

| source-condition cell | spot-check n |
|---|---:|
| gpt4omini_illness_climb | 2 |
| gpt4omini_illness_cold | 4 |
| gpt54mini_blue_climb | 4 |
| gpt54mini_blue_cold | 4 |
| gpt54mini_illness_climb | 4 |
| gpt54mini_illness_cold | 4 |

## Matrix-Cell Agreement

`codex_fresh` vs `codex_audit`; endorsement uses quadratic-weighted kappa,
surface uses Cohen kappa.

| matrix cell | n | endorsement kappa | endorsement raw | surface kappa | surface raw | safety kappa | safety raw |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt4omini_illness | 6 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| gpt54mini_blue | 8 | 0.600 | 0.875 | 1.000 | 1.000 | 1.000 | 1.000 |
| gpt54mini_illness | 8 | 0.900 | 0.875 | 1.000 | 1.000 | 1.000 | 1.000 |

## Source-Condition Agreement

| source-condition cell | n | endorsement kappa | endorsement raw | surface kappa | surface raw | safety kappa | safety raw |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt4omini_illness_climb | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| gpt4omini_illness_cold | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| gpt54mini_blue_climb | 4 | 0.000 | 0.750 | 1.000 | 1.000 | 1.000 | 1.000 |
| gpt54mini_blue_cold | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| gpt54mini_illness_climb | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| gpt54mini_illness_cold | 4 | 0.750 | 0.750 | 1.000 | 1.000 | 1.000 | 1.000 |

## Read

The spot-check audit supports the main endpoint read. Agreement is perfect for
`gpt-4o-mini x illness`, substantial at the matrix-cell level for
`gpt-5.4-mini x blue_door`, and high for `gpt-5.4-mini x illness`. The low
source-condition kappa for `gpt54mini_blue_climb` is driven by a single
one-step endpoint-style disagreement in a small `n=4` subset; raw agreement is
0.75 and surface/safety agreement is 1.0.
