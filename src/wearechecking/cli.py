import argparse
from importlib.metadata import version
import json
import sys
from .paths import prepare_dirs
from .data import fetch_weekend, latest_snapshot, get_weekend


def main():
    parser = argparse.ArgumentParser(description="WeAreChecking data and environment tools")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    for command in ("fetch", "inspect", "schedule"):
        entry = sub.add_parser(command)
        entry.add_argument("--year", type=int, default=2024)
        entry.add_argument("--round", type=int, default=1, dest="round_number")
        if command == "fetch":
            entry.add_argument("--session", action="append", dest="sessions",
                               choices=["FP1", "FP2", "FP3", "Q", "SQ", "S", "R"])
    args = parser.parse_args()
    root = prepare_dirs()
    if args.command == "doctor":
        print(f"Python: {sys.version.split()[0]}")
        print(f"Interpreter: {sys.executable}")
        for name in ("wearechecking", "fastf1", "pandas", "pyarrow", "ipykernel"):
            print(f"{name}: {version(name)}")
        print("Environment ready. This check does not test internet access or model performance.")
    elif args.command == "schedule":
        event, schedule = get_weekend(args.year, args.round_number, root)
        print(event["EventName"], "/", event["EventFormat"])
        print(schedule.to_string(index=False))
    else:
        snapshot = (fetch_weekend(args.year, args.round_number, args.sessions, root)
                    if args.command == "fetch" else latest_snapshot(args.year, args.round_number, root))
        print(json.dumps({"path": str(snapshot.path), "event": snapshot.manifest["event_name"],
                          "sessions": snapshot.manifest["sessions"],
                          "status": snapshot.manifest["status"]}, indent=2, ensure_ascii=False))
