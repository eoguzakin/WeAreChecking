"""Milestone 2: explicitly reconstructed, post-qualifying baseline inputs."""
from dataclasses import dataclass
import pandas as pd

from .contracts import DataContractError, require_columns, utc_timestamp
from .data import Snapshot


@dataclass(frozen=True)
class ForecastInputs:
    frame: pd.DataFrame
    metadata: dict


def qualifying_inputs(snapshot: Snapshot, cutoff, *, mode):
    if mode != "reconstructed":
        raise DataContractError(
            "This is a retrospective download. Specify mode='reconstructed' explicitly. "
            "Live point-in-time forecasting is not supported yet."
        )
    cutoff = utc_timestamp(cutoff)
    info = snapshot.manifest["sessions"].get("Q")
    if info is None:
        raise DataContractError("Download the qualifying session first.")
    if cutoff <= utc_timestamp(info["event_end_bound_utc"]):
        raise DataContractError("The cutoff must be after qualifying has finished.")
    schedule = snapshot.schedule()
    race = schedule.loc[schedule.session_code == "R"]
    if len(race) != 1 or cutoff >= utc_timestamp(race.iloc[0].start_utc):
        raise DataContractError("The cutoff must be before the race starts.")
    # Explicit allowlist. Never access R/results, points, status or race grid here.
    source = snapshot.table("Q", "results")
    require_columns(source, ["DriverId", "Abbreviation", "TeamName", "Position"], "Qualifying results")
    frame = source[["DriverId", "Abbreviation", "TeamName", "Position"]].rename(
        columns={"DriverId": "driver_id", "Abbreviation": "driver",
                 "TeamName": "team", "Position": "qualifying_position"}
    ).copy()
    if frame.driver_id.isna().any() or frame.driver_id.eq("").any() or frame.driver_id.duplicated().any():
        raise DataContractError("A permanent driver identity is missing or duplicated; do not replace it with a driver number.")
    rank = pd.to_numeric(frame.qualifying_position, errors="coerce")
    if sorted(rank.tolist()) != list(range(1, len(frame) + 1)):
        raise DataContractError("The qualifying classification is incomplete or duplicated; it is unsuitable for this starter exercise.")
    frame["qualifying_position"] = rank.astype(int)
    return ForecastInputs(frame.reset_index(drop=True), {
        "cutoff_utc": cutoff.isoformat(), "target_session": "R",
        "source_session": "Q", "mode": mode, "snapshot_id": snapshot.path.name,
        "source_observed_at": snapshot.manifest["observed_at"],
        "entry_policy": "Q participants are provisional R entries; not a confirmed race entry list",
        "limitations": [
            "Later Q classification corrections may be included.",
            "Grid penalties, substitutions, injury and DNS are not modeled yet.",
            "This is a benchmark, not a trained model or a validated live forecast.",
        ],
    })
