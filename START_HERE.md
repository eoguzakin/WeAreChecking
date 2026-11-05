# Start here

**Working first draft — under active development.** The original exercises are complete. You can now run the whole workflow, read the implementations and change one component at a time.

## 1. Install

Use Python 3.13. From the project root on Windows:

```powershell
python bootstrap.py
$wacPython = ".\.venv\Scripts\python.exe"
& $wacPython -m wearechecking doctor
```

Activation is optional. Using the environment's interpreter directly avoids PowerShell activation-policy issues. In VS Code, select the interpreter under this project's .venv and the Python (WeAreChecking) notebook kernel.

On macOS/Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m ipykernel install --prefix .venv --name wearechecking --display-name "Python (WeAreChecking)"
```

Python 3.13 on Windows is the tested setup. The Windows lockfile freezes its dependencies; the other-platform install uses pyproject constraints.

## 2. Run a real baseline

```powershell
& $wacPython -m wearechecking demo --year 2024 --round 1
```

The first run fetches historical data. Repeated runs reuse an existing complete snapshot. To deliberately obtain a new snapshot, run `fetch`. The demo saves a prediction before reading race labels for evaluation.

Open notebooks 01 and 02. Both now run end to end. For this Bahrain snapshot, the qualifying-order baseline has MAE 2.3 and Spearman approximately 0.886.

## 3. Train on historical seasons

```powershell
& $wacPython -m wearechecking history --start-year 2022 --end-year 2025
& $wacPython -m wearechecking benchmark
```

The terminal prints the model folder. It contains the trained model, feature schema, checksums, held-out predictions, per-event metrics and benchmark report. Notebook 03 explains the same experiment and can reproduce it.

To create one reconstructed race prediction using the latest local model:

```powershell
$modelRun = (Get-ChildItem .\reports\benchmarks -Directory | Sort-Object Name | Select-Object -Last 1).FullName
& $wacPython -m wearechecking race --year 2025 --round 1 --model $modelRun
```

Only load joblib models you generated locally or otherwise trust. The race command rejects a model trained on the target event or a later event. This command is a historical, post-qualifying reconstruction; it is not a live forecast API.

## 4. Replay session updates

```powershell
& $wacPython -m wearechecking forecast --entries examples/2024_bahrain_entries.json --events examples/events.json --cutoff 2024-02-29T10:00:00Z
& $wacPython -m wearechecking forecast --entries examples/2024_bahrain_entries.json --events examples/events.json --cutoff 2024-03-01T18:00:00Z
```

Open the printed folder's forecast.html. The later cutoff admits more completed observations; it never reads the target session's results. Reports retain their cutoff, source snapshot, model method, roster provenance and input hashes.

The all-session engine is experimental. Before FP1, all session predictions share the same historical-form ordering. They diverge only as relevant evidence becomes available. No probabilities or confidence intervals are claimed for those rankings.

For the supplied Austrian sprint example:

```powershell
& $wacPython -m wearechecking fetch --year 2024 --round 11
& $wacPython -m wearechecking forecast --year 2024 --round 11 --entries examples/2024_red_bull_ring_entries.json --cutoff 2024-06-28T16:00:00Z
```

## 5. Check and explore

```powershell
& $wacPython -m pytest
& $wacPython scripts/validate_notebooks.py
```

Executed notebook copies and HTML previews go to reports/executed/. Source notebooks stay output-free so personal paths and downloaded data do not enter Git.

Useful reading order: history.py → modeling.py → events.py → weekend.py. Change one idea at a time, record the hypothesis, and compare against the existing baseline. The 2025 holdout has already been inspected; use a new evaluation window for later model-selection decisions.
