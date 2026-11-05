# First race model card

**v0.1 — under active development. Evaluation run: 5 November 2026.**

## Intended use and decision

A reproducible research baseline for reconstructing a post-qualifying Grand Prix ranking. It is not a production forecast, a calibrated probability model or a recommendation system.

**Decision: keep qualifying order as the default benchmark.** The selected trained model has not demonstrated lower held-out position error.

## Data and split

Jolpica qualifying and race classifications from 2022–2025, downloaded on 5 November 2026. Current classifications can contain later corrections.

- Training: 2022–2023, 43 eligible events.
- Validation/model selection: 2024, 21 eligible events.
- Final fit: training plus validation.
- Test: 2025, 21 eligible events / 420 driver rows.
- Seven events excluded across all four seasons. Each exclusion and its reason is retained in the JSON report.

Excluded events: 2023-10, 2024-08, 2024-15, 2024-17 and 2025-07 have incomplete qualifying permutations. 2025-09 and 2025-21 have Q/R roster mismatches. This complete-case policy can bias evaluation away from difficult entry/classification changes.

The model stays frozen through the test season; previous completed races update rolling driver/team form. This simulates sequential feature availability, not historical source publication availability.

## Target and inputs

Target: normalized final-classification position. Predictions are sorted into unique places 1..N, with deterministic driver-ID tie breaking.

Inputs: normalized qualifying position, last-five driver form, last-ten team driver-result form, shrunk circuit-specific form, last-ten driver finish rate, historical race appearances, constructor and circuit identity.

Circuit identity and prior circuit performance are supported. Geometry, elevation, surface, tyre degradation, weather forecasts, injuries, grid penalties and in-weekend practice features are not part of this trained model.

New drivers fall back to team form; unknown team/circuit categories are accepted. Prior appearances include classification rows, so they are not a strict count of race starts.

## Selection and results

Candidates fixed before test inspection: Ridge alpha 10, Ridge alpha 100, and histogram gradient boosting (150 iterations, learning rate 0.05, 7 leaf nodes, L2 10, no random early-stopping split).

Ridge alpha 100 had the lowest validation MAE among trained candidates: 2.940. The validation qualifying baseline was already slightly better at 2.848.

| Held-out 2025 method | Position MAE ↓ | Spearman ↑ | Top-three overlap ↑ |
| --- | ---: | ---: | ---: |
| Qualifying order | 3.323810 | 0.657573 | 0.761905 |
| Ridge alpha 100 | 3.338095 | 0.665163 | 0.761905 |

Metrics are averaged across events. Paired model-minus-baseline MAE: +0.014286. Descriptive 95% event-bootstrap interval: [−0.171548, +0.219048], 2,000 resamples, seed 42. Successive events are dependent, so this interval is not a strong statistical guarantee.

The Bahrain single-weekend demo (MAE 2.3) is separate from this test and is not used as evidence of model superiority.

## Reproduction and limits

Run history for 2022–2025, then benchmark with train-end 2023, valid-year 2024 and test-year 2025. The saved model has a schema, dependency version, training boundary and checksum. Only load trusted local joblib artifacts.

[Exact report](evaluation/benchmark_2025.json). Raw source snapshots and trained binaries are not committed. Downloaded source corrections and dependency changes can change a future rerun; the stored provenance identifies this run.

Next experiments need a new holdout. Do not repeatedly tune against the already inspected 2025 season. The all-session heuristic engine is a separate, unvalidated prototype and must not inherit this model's benchmark claims.

Implementation correction before publication: the provider uses both Lapped and +N Laps for classified finishers. The finish-rate feature now recognizes both. The published result above was rerun after this contract fix; no hyperparameters were changed.
