# Data and forecast contract

Status: first draft, under active development.

## Sources and persistence

| Source | Current use | Boundary |
| --- | --- | --- |
| FastF1 calendar | Scheduled sessions and event format | Calendar access only; no F1TV timing download |
| OpenF1 | Session participants, laps, weather, stints | Historical public data; missing observations remain missing |
| Jolpica | Qualifying/race/sprint classifications; season history | Pagination counts driver-result rows, including split races |
| Reviewed event file | Confirmed entry changes and annotations | Explicit source URL, publication, observation and effective times |

Weekend and history downloads create immutable folders. Raw responses, normalized tables and a manifest record source URLs, observation time, row counts and SHA-256 checksums. A failed download stays failed and cannot be opened as a complete snapshot. Readers reject changed files and paths outside the snapshot.

A complete weekend snapshot means all **requested** sessions were downloaded. It does not mean every scheduled session was requested. A forecast can use a partial snapshot if it has the calendar and the needed completed sessions.

## Time semantics

- All timestamps must be timezone-aware and are converted to UTC.
- Current workflows are **reconstructed**. Data downloaded today may include later corrections.
- A source session becomes eligible only when its conservative event-end bound is strictly earlier than the cutoff.
- Only sessions whose scheduled start is strictly later than the cutoff are forecast. In-progress sessions are excluded.
- Historical race form uses events before the target weekend's day boundary. No target race's classification enters its own features.
- Model training must end before the event being predicted.
- Reviewed news is eligible only when both published_at and observed_at are no later than the cutoff, and effective_at is no later than the target start.
- Example roster available_at timestamps are declared replay assumptions. They are not verified publication timestamps.

These guards prevent direct future-label access. They do **not** establish point-in-time correctness of retrospectively corrected data or the supplied retrospective roster.

## Identity and roster

Permanent driver_id is the modeling identity. A car number is not an identity. Session evidence matches both driver number and driver code before joining to the explicit target entry list.

A substitution removes the original entry and creates the replacement's own identity. A driver without prior F1 results uses team form and has history_races = 0. Driver/form history is not copied from the displaced driver.

Qualifying-order evaluation requires matching Q/R rosters and complete position permutations. The multi-season benchmark reports and excludes mismatched or incomplete events. A future model must handle these cases without selecting the roster from its labels.

## Features and targets

The trained race model uses normalized qualifying rank, recent driver/team finishing form, shrunk driver/team circuit form, recent finish rate, prior race appearances, circuit identity and constructor identity.

Current-race result, status, points, fastest lap and observed race weather are not predictors. The target is normalized final-classification position, converted back to a complete within-event ranking. Retirements and disqualifications can therefore produce large position errors.

The experimental weekend engine uses historical form plus completed-session observations. FP observations are the median of each driver's three fastest timed non-pit-out laps. This is a timing proxy, not fuel/tyre-adjusted pace. SQ uses a timing proxy when an official classification is unavailable.

Base form = 0.5 × driver form + 0.3 × team form + 0.2 × driver circuit form. It receives weight 1.0. Completed practice sessions share total weight 0.8; Q → R and SQ → S receive 2.5; S → R receives 0.8. Missing driver observations add no weight. These weights are explicit heuristics, not optimized or calibrated coefficients.

## Artifacts and evaluation

- Qualifying baseline: prediction.csv, inputs.csv, metadata.json, optional evaluation files.
- Trained race prediction: ranking, frozen feature table, source observation time, model and input hashes.
- Weekend update: versioned JSON and HTML, cutoff, source snapshot, entry/event/history hashes and applied events.
- Benchmark: train/validation/test protocol, candidate results, selected model, event exclusions, per-event errors and baseline comparison.

Position MAE, Spearman and top-three overlap are averaged across events. The paired bootstrap resamples events, not individual drivers; temporal dependence still limits the interval's interpretation.

No calibrated probabilities, DNF model, tyre-degradation model, forecast weather, automated news extraction or production live service are implemented in v0.1.
