# Development roadmap

**Ongoing development.** This roadmap distinguishes implemented software from demonstrated predictive value.

## v0.1 — implemented

- Historical weekend and multi-season ingestion with raw-source provenance.
- Completed reference functions and three executable walkthrough notebooks.
- Saved baseline predictions and separate evaluation.
- Chronological trained race benchmark with honest baseline comparison.
- Experimental remaining-session forecasts for standard and sprint calendars.
- Timestamped reviewed entry changes, replacement-driver cold starts and session observation matching.
- Versioned CLI/JSON/CSV/HTML output and regression tests.
- Repository documentation, reproducible dependencies and CI configuration.

## Next — improve the information boundary

- Verified, session-specific entry lists with actual publication/observation timestamps.
- Grid penalties, pit-lane starts, DNS/DSQ and corrected classifications without complete-case exclusions.
- Provider schema-change tests, source reconciliation and broader historical coverage.
- Append-only event corrections/supersession and explicit source confidence.

## Next — improve forecasting evidence

- Trained FP, qualifying, sprint and Grand Prix models with separate target definitions.
- Tyre compound, stint age, fuel/run-plan uncertainty and robust pace estimates.
- Circuit geometry, elevation, surface, overtaking difficulty and historical degradation.
- Historical forecast weather vintages and forecast revisions.
- Probabilistic rankings, retirement risk, calibration and session-aware backtests.
- New temporal holdout and regime-shift checks; 2025 is already inspected.

## Later — operational updates

- Automated official/team news ingestion with timestamps, deduplication and human review.
- Schedule-driven ingestion and prediction refresh jobs.
- Genuine live data/entry availability, outage handling and monitoring.
- Interactive dashboard and prediction-version comparisons.
- Reproducible model releases and deployment.

A working component is not evidence that it improves accuracy. Changes should include a concrete hypothesis, temporal evaluation and an updated decision note.
