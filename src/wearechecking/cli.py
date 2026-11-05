"""Command-line entry points for the complete first-draft workflow."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
import sys
import uuid

import pandas as pd

from .contracts import DataContractError
from .paths import prepare_dirs
from .data import fetch_weekend, latest_snapshot, get_weekend


def _weekend_options(entry):
    entry.add_argument("--year", type=int, default=2024)
    entry.add_argument("--round", type=int, default=1, dest="round_number")


def _parser():
    parser = argparse.ArgumentParser(description="WeAreChecking — F1 forecasts under active development")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    for command in ("fetch", "inspect", "schedule", "predict", "evaluate", "demo", "forecast"):
        entry = sub.add_parser(command)
        _weekend_options(entry)
        if command == "fetch":
            entry.add_argument("--session", action="append", dest="sessions",
                               choices=["FP1", "FP2", "FP3", "Q", "SQ", "S", "R"])
        if command in ("predict", "demo", "forecast"):
            entry.add_argument("--cutoff", required=command == "forecast",
                               help="Timezone-aware ISO timestamp; forecast sessions must not have started.")
        if command == "evaluate":
            entry.add_argument("folder", type=Path)
        if command == "forecast":
            entry.add_argument("--entries", type=Path, required=True)
            entry.add_argument("--events", type=Path)
            entry.add_argument("--history", type=Path)
    entry = sub.add_parser("history")
    entry.add_argument("--start-year", type=int, default=2022)
    entry.add_argument("--end-year", type=int, default=2025)
    entry = sub.add_parser("benchmark")
    entry.add_argument("--history", type=Path)
    entry.add_argument("--train-end", type=int, default=2023)
    entry.add_argument("--valid-year", type=int, default=2024)
    entry.add_argument("--test-year", type=int, default=2025)
    entry = sub.add_parser("race")
    _weekend_options(entry)
    entry.set_defaults(year=2025)
    entry.add_argument("--model", type=Path, required=True,
                       help="Folder from a local benchmark run. Never load untrusted joblib files.")
    entry.add_argument("--history", type=Path)
    return parser


def _run(args, root):
    if args.command == "doctor":
        print(f"Python: {sys.version.split()[0]}")
        print(f"Interpreter: {sys.executable}")
        for name in ("wearechecking", "fastf1", "pandas", "scikit-learn", "pyarrow", "ipykernel"):
            print(f"{name}: {version(name)}")
        print("Environment ready. Status: under active development.")
        return
    if args.command in ("history", "benchmark", "forecast", "race"):
        from .history import fetch_history, latest_history, load_history
        if args.command == "history":
            print(fetch_history(args.start_year, args.end_year, root))
            return
        history_folder = args.history or latest_history(root)
        if args.command == "benchmark":
            from .modeling import benchmark
            folder, report = benchmark(history_folder, args.train_end, args.valid_year, args.test_year, root)
            print(json.dumps(report, indent=2))
            print(f"Saved benchmark and model: {folder}")
            return
        results, qualifying, provenance = load_history(history_folder)
        if args.command == "race":
            from .modeling import predict_race
            q = qualifying.loc[(qualifying.season == args.year) & (qualifying["round"] == args.round_number)]
            if q.empty:
                raise DataContractError("No qualifying entries found for this event.")
            prediction, features, metadata = predict_race(args.model, results, q)
            folder = root / "reports/races" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
            folder.mkdir(parents=True)
            prediction = prediction.merge(q[["driver_id", "driver", "team"]], on="driver_id", validate="one_to_one")
            prediction.to_csv(folder / "prediction.csv", index=False)
            features.to_csv(folder / "inputs.csv", index=False)
            metadata.update(mode="reconstructed", event_id=str(q.iloc[0].event_id),
                            source_observed_at=provenance["observed_at"],
                            prediction_sha256=sha256((folder / "prediction.csv").read_bytes()).hexdigest(),
                            inputs_sha256=sha256((folder / "inputs.csv").read_bytes()).hexdigest(),
                            created_at=datetime.now(timezone.utc).isoformat())
            (folder / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            print(prediction[["predicted_position", "driver", "team"]].to_string(index=False))
            print(f"Saved reconstructed race prediction: {folder}")
            return
    if args.command == "schedule":
        event, schedule = get_weekend(args.year, args.round_number, root)
        print(event["EventName"], "/", event["EventFormat"])
        print(schedule.to_string(index=False))
        return
    if args.command == "fetch":
        snapshot = fetch_weekend(args.year, args.round_number, args.sessions, root)
    else:
        try:
            snapshot = latest_snapshot(args.year, args.round_number, root)
        except FileNotFoundError:
            if args.command != "demo":
                raise
            snapshot = fetch_weekend(args.year, args.round_number, root=root)
    if args.command in ("fetch", "inspect"):
        print(json.dumps({"path": str(snapshot.path), "event": snapshot.manifest["event_name"],
                          "sessions": snapshot.manifest["sessions"],
                          "status": snapshot.manifest["status"]}, indent=2))
    elif args.command == "forecast":
        from .weekend import load_entry_file, forecast_weekend, save_weekend
        entries, entry_meta = load_entry_file(args.entries, args.cutoff)
        if entry_meta.get("year") != args.year or entry_meta.get("round") != args.round_number:
            raise DataContractError("The entry file belongs to a different weekend.")
        events = json.loads(args.events.read_text(encoding="utf-8")) if args.events else []
        report = forecast_weekend(snapshot, results, entries, entry_meta["circuit_id"], args.cutoff, events)
        report["entry_provenance"] = entry_meta.get("provenance")
        report["entry_file_sha256"] = sha256(args.entries.read_bytes()).hexdigest()
        report["events_file_sha256"] = sha256(args.events.read_bytes()).hexdigest() if args.events else None
        report["history_manifest_sha256"] = sha256((history_folder / "manifest.json").read_bytes()).hexdigest()
        folder = save_weekend(report, root)
        for item in report["forecasts"]:
            print(f'{item["session"]}: evidence {item["observations_used"]}')
            print(pd.DataFrame(item["ranking"])[["predicted_position", "driver", "team"]].head(5).to_string(index=False))
        print(f"Saved JSON and HTML forecasts: {folder}")
    else:
        from .evaluation import evaluate_saved, save_prediction
        if args.command == "evaluate":
            folder = args.folder
        else:
            from .features import qualifying_inputs
            from .student import qualifying_baseline
            schedule = snapshot.schedule()
            cutoff = args.cutoff or (pd.Timestamp(schedule.loc[schedule.session_code.eq("R"), "start_utc"].iloc[0]) - pd.Timedelta(hours=1))
            inputs = qualifying_inputs(snapshot, cutoff, mode="reconstructed")
            prediction = qualifying_baseline(inputs.frame)
            folder = save_prediction(prediction, inputs, root)
            print(prediction.merge(inputs.frame[["driver_id", "driver"]], on="driver_id").to_string(index=False))
            print(f"Saved qualifying baseline: {folder}")
        if args.command in ("evaluate", "demo"):
            comparison, metrics = evaluate_saved(folder, snapshot)
            comparison.to_csv(folder / "evaluation.csv", index=False)
            (folder / "evaluation.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
            print(json.dumps(metrics, indent=2))


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        _run(args, prepare_dirs())
    except (DataContractError, FileNotFoundError) as exc:
        parser.error(str(exc))
