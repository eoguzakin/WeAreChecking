# WeAreChecking working conventions

The user requested a complete English first draft and authorized pushing it to GitHub. The earlier tutorial-only mode is superseded.

- Implement complete, runnable changes. Do not leave required behavior as learner TODOs unless the user explicitly asks for a guided exercise.
- Keep explanations, docs, notebook text and comments in English.
- Mark the project as under active development. Distinguish validated benchmarks from experimental heuristics.
- Never present synthetic fixtures as real F1 data or a historical reconstruction as a genuine live forecast.
- Exclude target-session outcomes/status/points and future observed weather from inputs.
- Use UTC and distinguish event time, source publication time and observation time.
- Driver numbers are session-scoped. Substitutions require a new permanent identity; FP observations must not transfer by car number alone.
- Read only completed sessions before a forecast cutoff. Save new prediction versions rather than overwriting earlier predictions.
- Keep model selection chronological. Do not tune against the reported 2025 holdout.
- Preserve source provenance, exclusions and checksum validation.
- Keep pyproject and the Windows Python 3.13 lockfile consistent.
- Validate with python -m pytest and python scripts/validate_notebooks.py. The latter needs downloaded example data and history.
- Do not commit raw downloads, environments, cache files, model binaries, credentials or absolute user paths.
- GitHub publishing is authorized for this first-draft task; never force-push over unrelated remote work.
