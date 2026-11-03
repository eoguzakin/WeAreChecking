# Milestones and completion criteria

## Now: the first two milestones

1. **A real weekend:** session schedule, laps, stints, weather, participants, provenance, and data-quality checks. Learner task: count each driver's unique laps.
2. **The first prediction:** use qualifying order as a race-order benchmark, save the prediction before opening the outcome, evaluate MAE and rank correlation, and write a decision note.

The infrastructure supports both milestones. We will complete the learning tasks interactively.

## Next stages

3. **Multiple-race experiments:** split historical seasons chronologically into training, validation, and test sets. Select models before examining the final test races. Compare qualifying and driver/team-history benchmarks, with uncertainty.
4. **The first trained model:** event/driver rows, rolling historical features, and team/circuit effects. Begin with an interpretable model, then try a ranking model. Exclude information from the future target session.
5. **Circuit and pace features:** circuit length/type/corner profile, FP long-run pace, tyre age, track evolution, traffic, and yellow/red-flag filtering. Do not claim exact fuel correction when fuel loads are unknown.
6. **Separate session targets:** distinguish FP lap-time ranking from race classification. Evaluate Q, SQ, Sprint, and GP separately. Read sprint formats from the calendar instead of fixing session counts or order.
7. **News and entry records:** record sourced FIA/team announcements, publication time, effective time, revisions, and penalties/DSQ/DNS/substitutions. For injury reports, use confirmed participation effects without making medical inferences. A rookie FP appearance does not establish a race entry.
8. **Sequential updates:** after a session, save a new snapshot, forecast the remaining sessions, preserve earlier predictions, and explain what changed. Handle postponed/cancelled sessions and new-driver scenarios explicitly.
9. **True replay:** use available_at/observed_at records captured at the time, the original publication version of news, and the issued_at time of weather forecasts. Report this separately from retrospective corrected data.
10. **Presentation:** calibrated rank distributions, podium/top-10/finish probabilities, data freshness, a model card, and a demo.

## Evidence of success

One race is insufficient. Evaluate across multiple forward-moving time windows against strong simple benchmarks, with uncertainty estimates, regulation changes, and new-driver cases. Model DNF/DNS/DSQ as separate outcomes or states. Only claim to handle news that the system actually ingested.

## Current implementation boundary

The existing code provides the learning infrastructure for the first two milestones. News ingestion, a live scheduler, continual learning, paid data accounts, and a deployed server remain future work.
