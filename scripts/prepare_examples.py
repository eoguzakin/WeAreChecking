"""Regenerate the real, reconstructed entry example from downloaded history."""
import json
import argparse
import pandas as pd
from pathlib import Path
from wearechecking.history import latest_history, load_history
from wearechecking.paths import project_root

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, default=2024)
parser.add_argument("--round", type=int, default=1, dest="round_number")
args = parser.parse_args()
root = project_root()
_, qualifying, provenance = load_history(latest_history(root))
q = qualifying.loc[(qualifying.season == args.year) & (qualifying["round"] == args.round_number)]
document = {
    "mode": "reconstructed", "year": args.year, "round": args.round_number, "circuit_id": str(q.iloc[0].circuit_id),
    "available_at": (pd.Timestamp(q.iloc[0].start_utc).normalize() - pd.Timedelta(days=3)).isoformat(),
    "provenance": "Retrospective roster from this event's Jolpica qualifying. available_at is a replay assumption, not verified historical publication evidence. Do not use this roster to claim a live or point-in-time backtest.",
    "source_url": f"https://api.jolpi.ca/ergast/f1/{args.year}/{args.round_number}/qualifying/",
    "source_observed_at": provenance["observed_at"],
    "entries": q[["driver_id", "driver", "team_id", "team", "driver_number"]].to_dict(orient="records"),
}
(root / "examples").mkdir(exist_ok=True)
(root / f"examples/{args.year}_{q.iloc[0].circuit_id}_entries.json").write_text(json.dumps(document, indent=2), encoding="utf-8")
