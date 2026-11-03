# WeAreChecking 🏁

A Python project for learning how to forecast Formula 1 weekends, one step at a time.

**Start here:** [START_HERE.md](START_HERE.md) → [01 · Weekend data](notebooks/01_weekend_data.ipynb) → [02 · First prediction](notebooks/02_first_prediction.ipynb).

## Current scope

- An isolated Python environment, data download command, cache, and versioned snapshots.
- OpenF1: session participants, laps, tyre stints, and observed weather.
- Jolpica: qualifying, sprint, and race classifications, plus permanent driver IDs.
- FastF1: the calendar only; its timing download API is not used.
- Separate model inputs and actual results, a UTC forecast cutoff, prediction records, and evaluation.
- Two guided notebooks, two learner exercises, and offline infrastructure tests.

**Still to build:** the learner exercises, a trained ML model, predictions for every session, circuit performance features, news/injury/penalty/substitution handling, live updates, and a user interface. See the [roadmap](docs/ROADMAP.md).

The first benchmark uses qualifying order to predict race order. It gives us a starting point for learning and comparing future models.

## Setup and checks

Python 3.12–3.14 is supported; this machine uses 3.13. Run these commands in PowerShell from the project root:

```powershell
py -3.13 bootstrap.py
.\.venv\Scripts\python.exe -m wearechecking doctor
.\.venv\Scripts\python.exe -m pytest
```

Open **this folder** in VS Code. Select **WeAreChecking (.venv)** or this folder's `.venv\Scripts\python.exe` as the notebook kernel. Environment activation is optional.

```powershell
.\.venv\Scripts\python.exe -m wearechecking fetch --year 2024 --round 1
.\.venv\Scripts\python.exe -m wearechecking inspect --year 2024 --round 1
```

The default example is the 2024 Bahrain Grand Prix. The fetch command downloads every session on the weekend schedule. The first download requires internet access; the notebooks read the saved snapshot. Each new download creates a separate snapshot. Detailed car telemetry is outside this initial download.

## How we will learn

We will use **predict what will happen → write a small piece of code → run a check → explain the result**. Your workspace is `src/wearechecking/student.py`. The functions initially return `None`, which the notebooks display as **PENDING**. This means an exercise is waiting for us to complete it. Passing the infrastructure tests does not complete the exercises.

We will use English for explanations, documentation, code comments, and feedback.

## Honest evaluation

Historical data is downloaded today and may contain later classification corrections. The first experiment is therefore explicitly labelled **reconstructed**. It does not establish what information was available at a historical forecast time.

For the first exercise, qualifying participants are treated as provisional race entries. Grid penalties, DNS, and driver substitutions are not modelled yet. Evaluation stops if the participant lists differ. One race's error is not evidence of general performance. Official positions are preserved for classified drivers who did not finish; separate DNS/DSQ handling remains future work.

## Sources

Access conditions were checked on 3 November 2026:

- [OpenF1 documentation](https://openf1.org/docs/) — historical data from 2023 onwards, available without authentication.
- [Jolpica documentation](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md) — results, driver records, and circuits.
- [FastF1 authentication](https://github.com/theOehrly/Fast-F1/blob/main/docs/api_reference/accounts_auth.rst) — timing access requires F1TV; this starter uses the calendar only.

Code and source data have separate licensing terms. Downloaded data and caches are excluded from Git. Respect the source terms; this project is intended for personal learning and portfolio development.
