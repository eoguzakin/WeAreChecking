# Start here

## 1. Open the project folder

VS Code → File → Open Folder → **WeAreChecking**.

You should see README.md, bootstrap.py, notebooks, and src.
Select this project's Python environment rather than the earlier Olist environment.

## 2. Check your environment

Open Terminal → New Terminal and use PowerShell:

```powershell
.\.venv\Scripts\python.exe -m wearechecking doctor
```

The environment is already set up on the original machine. On a different machine, or after extracting a fresh ZIP, run:

```powershell
py -3.13 bootstrap.py
```

If `py` is unavailable, run `bootstrap.py` with an installed Python 3.12–3.14 interpreter. If a command fails, share its output so we can resolve the setup issue.

## 3. Our first two milestones

| Milestone | Where | Your task | Completion criteria |
|---|---|---|---|
| 1 · Understand a real weekend | notebooks/01_weekend_data.ipynb | Explain sessions, laps, and drivers; write lap_counts | Data and exercise checks pass; you can explain a lap record |
| 2 · Make the first ranking prediction | notebooks/02_first_prediction.ipynb | Write qualifying_baseline, save a prediction, and interpret its evaluation | The prediction ranks every driver 1..N, uses no race results as inputs, and has a completed decision note |

Start with **steps 1–3 of notebook 01**.
At the top right, choose **Select Kernel → Python Environments → .venv**.

You should see the Bahrain weekend schedule, the data source, and a small lap-table preview.
If data is missing, run the fetch command shown by the notebook in the terminal, then rerun the cell.
The notebook reads saved data; downloading is an explicit command.

## 4. Working together

- Write one small piece at a time.
- Say what you expect before running it.
- If something fails, share the cell and the error message.
- Each exercise cell reloads changes to `student.py`.
- If the kernel state gets confusing, use **Restart Kernel → Run All**.
- **PENDING** marks an exercise we have yet to implement.

First discussion question: **Does one row in `laps` represent a driver or a lap?**
Explain your answer using the DriverNumber and LapNumber values you can see.

## Troubleshooting

- `ModuleNotFoundError`: select the correct .venv kernel; run bootstrap if needed.
- `KeyError`: inspect `df.columns.tolist()`. The project checks explain which columns are missing.
- Interrupted download: run fetch again. Failed snapshots are retained but are not selected by the notebooks.
- GitHub sign-in is needed to publish the repository. Local notebooks work without it.
- Passing `pytest` does not complete the learner exercises.
