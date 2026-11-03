"""Weekend snapshots: source JSON, normalized tables and provenance."""
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import uuid

import fastf1
import pandas as pd

from .contracts import DataContractError, require_columns
from .paths import prepare_dirs

SESSION_CODES = {
    "Practice 1": "FP1", "Practice 2": "FP2", "Practice 3": "FP3",
    "Qualifying": "Q", "Race": "R", "Sprint": "S",
    "Sprint Qualifying": "SQ", "Sprint Shootout": "SQ",
}


def _utc(value):
    stamp = pd.Timestamp(value)
    if pd.isna(stamp):
        raise DataContractError("The source session date is missing.")
    # FastF1 *DateUtc fields and t0_date are UTC, even when timezone-naive.
    return stamp.tz_localize("UTC") if stamp.tzinfo is None else stamp.tz_convert("UTC")


def schedule_from_event(event):
    rows = []
    for slot in range(1, 6):
        name = event.get(f"Session{slot}")
        if not isinstance(name, str) or not name.strip():
            continue
        if name not in SESSION_CODES:
            raise DataContractError(f"Unknown session type: {name}; review the session mapping.")
        rows.append({"session_code": SESSION_CODES[name], "session_name": name,
                     "start_utc": _utc(event[f"Session{slot}DateUtc"])})
    frame = pd.DataFrame(rows)
    require_columns(frame, ["session_code", "session_name", "start_utc"], "Schedule")
    if frame.session_code.duplicated().any():
        raise DataContractError("The schedule contains a duplicate session code.")
    return frame.sort_values("start_utc").reset_index(drop=True)


def get_weekend(year, round_number, root=None):
    root = prepare_dirs(root)
    fastf1.Cache.configure(cache_dir=str(root / ".cache/fastf1"))
    event = fastf1.get_event(int(year), int(round_number), backend="fastf1")
    return event, schedule_from_event(event)


@dataclass(frozen=True)
class Snapshot:
    path: Path
    manifest: dict

    def table(self, session_code, name):
        key = f"{session_code}/{name}.parquet"
        if key not in self.manifest["files"]:
            raise DataContractError(f"The snapshot does not contain {key}. Download the session again.")
        return pd.read_parquet(self.path / key)

    def schedule(self):
        return pd.read_parquet(self.path / "schedule.parquet")


def open_snapshot(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "complete" or manifest.get("schema_version") != 1:
        raise DataContractError("The snapshot is incomplete or its schema version is unsupported.")
    for name, info in manifest["files"].items():
        target = (folder / name).resolve()
        if not target.is_relative_to(folder.resolve()):
            raise DataContractError("The snapshot file path is outside the snapshot root.")
        if sha256(target.read_bytes()).hexdigest() != info["sha256"]:
            raise DataContractError(f"Snapshot has changed: {name}")
    return Snapshot(folder, manifest)


def latest_snapshot(year=2024, round_number=1, root=None):
    root = prepare_dirs(root)
    base = root / "data/snapshots" / str(year) / f"{round_number:02d}"
    candidates = sorted(base.glob("*/manifest.json"), reverse=True)
    for manifest_path in candidates:
        metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
        if metadata.get("status") == "complete":
            return open_snapshot(manifest_path.parent)
    raise FileNotFoundError(
        f"No data found. From the project root, run: python -m wearechecking fetch --year {year} --round {round_number}"
    )



def fetch_weekend(year=2024, round_number=1, sessions=None, root=None):
    from .provider import PublicClient, resolve_sessions, jolpica_results, normalize_laps, normalize_drivers
    root = prepare_dirs(root)
    event, schedule = get_weekend(year, round_number, root)
    requested = set(sessions or schedule.session_code)
    unknown = requested - set(schedule.session_code)
    if unknown:
        raise DataContractError(f"Sessions not present in this weekend: {sorted(unknown)}")
    client = PublicClient(root)
    raw_sessions, discovery = resolve_sessions(client, year, schedule)
    session_map = {}
    for row in raw_sessions:
        name = row["session_name"]
        if name not in SESSION_CODES:
            raise DataContractError(f"Unknown OpenF1 session: {name}")
        code = SESSION_CODES[name]
        if code in session_map:
            raise DataContractError(f"Duplicate OpenF1 session: {code}")
        session_map[code] = row
    if set(session_map) != set(schedule.session_code):
        raise DataContractError("The FastF1 calendar and OpenF1 session list differ; review the mapping manually.")
    now = datetime.now(timezone.utc)
    folder = root / "data/snapshots" / str(year) / f"{round_number:02d}" / (
        now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    )
    folder.mkdir(parents=True)
    metadata = {
        "schema_version": 1, "status": "downloading", "year": int(year),
        "round": int(round_number), "event_name": str(event["EventName"]),
        "location": str(event["Location"]), "country": str(event["Country"]),
        "event_format": str(event["EventFormat"]), "observed_at": now.isoformat(),
        "source": "OpenF1 + Jolpica; FastF1 calendar only",
        "source_version": {"fastf1": fastf1.__version__, "openf1": "v1", "jolpica": "ergast-compatible"},
        "provenance_mode": "retrospective_download",
        "limitations": ["Downloaded now, not historical publication-time evidence.",
                       "Later classification corrections may be present.",
                       "Observed weather is not a historical weather forecast.",
                       "FP driver identities are session-scoped; permanent mapping remains a future task."],
        "requested_sessions": sorted(requested), "sessions": {}, "files": {}, "requests": [],
    }

    def write_manifest():
        (folder / "manifest.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    def track(relative, rows):
        metadata["files"][relative] = {
            "rows": rows, "sha256": sha256((folder / relative).read_bytes()).hexdigest()
        }

    def save_raw(relative, payload, url):
        destination = folder / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        track(relative, len(payload) if isinstance(payload, list) else None)
        metadata["requests"].append({"url": url, "file": relative,
                                     "exported_at": datetime.now(timezone.utc).isoformat()})

    def save_table(relative, frame):
        destination = folder / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(frame).to_parquet(destination, index=False)
        track(relative, len(frame))

    write_manifest()
    try:
        save_table("schedule.parquet", schedule)
        for payload, url, name in discovery:
            save_raw(f"raw/{name}.json", payload, url)
        for row in schedule.itertuples(index=False):
            code = row.session_code
            if code not in requested:
                continue
            session = session_map[code]
            if session.get("is_cancelled"):
                raise DataContractError(f"{code} was cancelled; cancellation handling is not implemented yet.")
            print(f"Downloading: {year} / {event['EventName']} / {code}", flush=True)
            tables = {}
            for name in ("drivers", "laps", "weather", "stints"):
                payload, url = client.get(f"https://api.openf1.org/v1/{name}",
                                          {"session_key": session["session_key"]})
                if not isinstance(payload, list):
                    raise DataContractError(f"{name}: unexpected API response.")
                save_raw(f"{code}/raw/{name}.json", payload, url)
                tables[name] = payload
            laps = normalize_laps(tables["laps"])
            participants = normalize_drivers(tables["drivers"])
            results = participants
            if code in ("Q", "R", "S"):
                results, payload, url = jolpica_results(client, year, round_number, code)
                save_raw(f"{code}/raw/classification.json", payload, url)
                if set(results.DriverNumber) != set(participants.DriverNumber):
                    raise DataContractError(f"{code}: the sources have different driver lists; automatic matching was stopped.")
                driver_matches = results.merge(participants, on="DriverNumber", suffixes=("_j", "_o"), validate="one_to_one")
                if not driver_matches.Abbreviation_j.eq(driver_matches.Abbreviation_o).all():
                    raise DataContractError(f"{code}: driver numbers and identities do not match across sources.")
            save_table(f"{code}/results.parquet", results)
            save_table(f"{code}/laps.parquet", laps)
            save_table(f"{code}/weather.parquet", pd.DataFrame(tables["weather"]))
            save_table(f"{code}/stints.parquet", pd.DataFrame(tables["stints"]))
            save_table(f"{code}/participants.parquet", participants)
            # A conservative event-time bound, not a publication/availability timestamp.
            measured_ends = laps.LapStartDate + laps.LapTime
            end_estimate = max(_utc(session["date_end"]), measured_ends.max()) if measured_ends.notna().any() else _utc(session["date_end"])
            metadata["sessions"][code] = {
                "session_key": session["session_key"], "meeting_key": session["meeting_key"],
                "circuit_key": session["circuit_key"], "circuit_short_name": session["circuit_short_name"],
                "scheduled_start_utc": row.start_utc.isoformat(),
                "source_start_utc": session["date_start"],
                "event_end_bound_utc": end_estimate.isoformat(),
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "weather_available": bool(tables["weather"]),
                "stints_available": bool(tables["stints"]),
                "driver_count": int(results.DriverNumber.nunique()),
                "classification_available": code in ("Q", "R", "S"),
            }
            write_manifest()
        metadata["status"] = "complete"
        metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
        write_manifest()
    except Exception as exc:
        metadata["status"] = "failed"
        metadata["error"] = f"{type(exc).__name__}: {exc}"
        write_manifest()
        raise
    return open_snapshot(folder)
