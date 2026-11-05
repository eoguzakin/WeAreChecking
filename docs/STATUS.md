# Project status

**First draft complete. Under active development.**
Last verified: 5 November 2026.

## Delivered

- All required first-draft functions implemented; no learner TODO blocks.
- Real 2024 Bahrain ingestion, saved baseline and evaluation.
- Real 2022–2025 history ingestion and chronological race-model benchmark.
- Remaining-session forecasting with immutable JSON/HTML versions.
- Reviewed substitutions, withdrawals, injury annotations and scoped disqualification handling.
- English documentation, three completed notebooks and offline regression tests.

The initial trained model does not beat the qualifying-order baseline on held-out position MAE. See MODEL_CARD.md for the exact result and exclusions.

## Verification

- 37 local regression tests passed.
- All three notebooks executed and their HTML exports were visually checked.
- Real Bahrain pre-weekend and post-qualifying replays completed.
- Real Austria sprint-qualifying and post-sprint updates completed.
- A reconstructed 2025 Australian GP prediction was saved using the trained model.
- Dependency consistency check passed.

## Open limits

- All workflows are reconstructed historical demonstrations; no live service.
- Multi-session weights are heuristic and not backtested.
- News ingestion is manual; no automatic crawler or unattended refresh.
- Circuit geometry, tyre degradation, forecast weather and calibrated uncertainty remain planned.
- Driver/event behavior has synthetic regression coverage; it is not evidence of performance on rare real-world incidents.
- CI configuration is included. Local checks are reported separately from remote CI.

See ROADMAP.md for the next milestones.
