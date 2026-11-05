# WeAreChecking

**First draft · Under active development · v0.1.0**

F1 weekend forecasting with traceable data, sequential session updates and reproducible evaluation. This is a working research prototype. Its predictions are experimental; the first trained model has **not beaten qualifying order on held-out position error**.

## What works today

| Component | First-draft behavior |
| --- | --- |
| Data ingestion | FastF1 calendar, OpenF1 laps/participants/weather/stints, Jolpica classifications and paginated season history |
| Reproducibility | Immutable snapshots, raw responses, checksums, source URLs and observation timestamps |
| Weekend forecasts | Rankings for remaining FP, qualifying, sprint qualifying, sprint and Grand Prix sessions |
| Session updates | Rerun with a later cutoff; completed sessions update remaining predictions and produce a new saved report |
| Driver events | Reviewed, timestamped substitutions and withdrawals; injury annotations; session-specific disqualification filtering |
| Race model | Ridge and gradient boosting candidates using qualifying, driver, team and circuit history |
| Evaluation | Chronological training/validation/test seasons, baseline comparisons, exclusions and per-event results |
| Learning | Three completed, executable English notebooks |
| Output | CLI tables, CSV/JSON artifacts and a local HTML weekend report |

The weekend engine currently uses **fixed heuristic weights**. The trained race benchmark is a separate experimental path. There is no live service, automated news crawler, calibrated probability model, weather forecast integration or session-specific trained model yet.

## Quick start — Windows / Python 3.13

From the repository root:

```powershell
python bootstrap.py
$wacPython = ".\.venv\Scripts\python.exe"
& $wacPython -m wearechecking doctor
& $wacPython -m wearechecking demo --year 2024 --round 1
```

The demo downloads the historical Bahrain weekend if necessary, saves a qualifying-order prediction, then evaluates it. It needs internet access on the first run. No API key or paid timing-data account is required for this historical workflow.

On macOS/Linux, create a Python 3.13 environment, install with `python -m pip install -e ".[dev]"`, and use `python -m wearechecking`. See [START_HERE.md](START_HERE.md) for kernel setup and commands.

## Train and benchmark

```powershell
& $wacPython -m wearechecking history --start-year 2022 --end-year 2025
& $wacPython -m wearechecking benchmark
```

The protocol is fixed: train on 2022–2023, select on 2024, refit through 2024, and test on 2025. Previous completed test-season races may update historical form, while the model stays frozen.

### Initial held-out result

Across **21 eligible races / 420 driver rows** in 2025:

| Method | Position MAE ↓ | Spearman ↑ | Top-three overlap ↑ |
| --- | ---: | ---: | ---: |
| Qualifying-order baseline | 3.324 | 0.658 | 0.762 |
| Selected trained model: Ridge, alpha 100 | 3.338 | 0.665 | 0.762 |

The model's paired MAE difference is +0.014 positions, with a descriptive event-bootstrap 95% interval of −0.172 to +0.219. This does not establish an improvement. Seven events across the downloaded seasons were excluded for incomplete qualifying classifications or Q/R roster mismatches. [Full model card](docs/MODEL_CARD.md) · [Machine-readable result](docs/evaluation/benchmark_2025.json).

## Update a weekend

After downloading history and running the demo:

```powershell
& $wacPython -m wearechecking forecast --year 2024 --round 1 --entries examples/2024_bahrain_entries.json --events examples/events.json --cutoff 2024-02-29T10:00:00Z
& $wacPython -m wearechecking forecast --year 2024 --round 1 --entries examples/2024_bahrain_entries.json --events examples/events.json --cutoff 2024-03-01T18:00:00Z
```

The first run forecasts all five scheduled sessions from historical form. The second has practice and qualifying evidence and forecasts only the Grand Prix. Each run saves a separate `forecast.html` and `forecast.json` under `reports/weekends/`.

The example roster is **reconstructed from later qualifying data**. Its availability date is an explicit replay assumption, not proof of a genuinely historical forecast. All current workflows are labelled reconstructed.

For a sprint weekend, download that weekend and supply its own entry file. The schedule determines session order; the engine does not assume every weekend follows the same format. See [event handling](docs/EVENTS.md).

## Project map

- [START_HERE.md](START_HERE.md): installation and the complete workflow.
- [notebooks/](notebooks/): data exploration, saved baseline, chronological modeling.
- [src/wearechecking/](src/wearechecking/): ingestion, contracts, features, models, session updates and CLI.
- [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md): temporal and identity boundaries.
- [docs/DECISION_NOTE.md](docs/DECISION_NOTE.md): what the initial results justify.
- [docs/ROADMAP.md](docs/ROADMAP.md): next development milestones.
- [docs/STATUS.md](docs/STATUS.md): verified behavior and open limits.

## Validation

```powershell
& $wacPython -m pytest
& $wacPython scripts/validate_notebooks.py
```

Notebook execution requires the Bahrain snapshot and 2022–2025 history. CI runs offline regression tests and notebook structure checks. Data, environments, caches and trained model binaries are excluded from Git.

Sources: [OpenF1](https://openf1.org/docs) · [Jolpica](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md) · [FastF1](https://docs.fastf1.dev/) · [scikit-learn](https://scikit-learn.org/stable/).

This independent project is not affiliated with Formula 1, the FIA or any team. Source data remain subject to their providers' terms.
