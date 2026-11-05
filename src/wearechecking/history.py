"""Immutable Jolpica history for chronological, reconstructed race benchmarks."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import uuid

import pandas as pd

from .contracts import DataContractError, require_columns
from .http import PublicClient
from .paths import prepare_dirs


def _pages(client, year, endpoint):
    offset, expected = 0, None
    key = "QualifyingResults" if endpoint == "qualifying" else "Results"
    while True:
        payload, url = client.get(
            f"https://api.jolpi.ca/ergast/f1/{year}/{endpoint}/",
            {"format": "json", "limit": 100, "offset": offset})
        data = payload["MRData"]
        total = int(data["total"])
        if expected is not None and total != expected:
            raise DataContractError("The source changed during pagination. Retry the download.")
        expected = total
        races = data["RaceTable"]["Races"]
        count = sum(len(r.get(key, [])) for r in races)
        if not count:
            raise DataContractError(f"No {endpoint} rows at offset {offset} for {year}.")
        yield payload, url, races, key
        offset += count
        if offset >= total:
            if offset != total:
                raise DataContractError("Pagination returned more records than declared.")
            break


def fetch_history(start_year=2022, end_year=2025, root=None):
    if start_year > end_year or start_year < 2003:
        raise DataContractError("Choose an ordered year range from 2003 onward.")
    root = prepare_dirs(root)
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    folder = root / "data/history" / token
    folder.mkdir(parents=True)
    manifest = {"schema_version": 1, "status": "downloading",
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "mode": "reconstructed", "years": [start_year, end_year],
                "source": "Jolpica", "files": {}, "requests": []}

    def record(name, count=None):
        manifest["files"][name] = {"sha256": sha256((folder / name).read_bytes()).hexdigest(),
                                   "rows": count}

    def write_manifest():
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    write_manifest()
    race_rows, qualifying_rows = [], []
    try:
        client = PublicClient(root)
        for year in range(start_year, end_year + 1):
            for endpoint in ("results", "qualifying"):
                print(f"History: {year} {endpoint}", flush=True)
                for page, (payload, url, races, key) in enumerate(_pages(client, year, endpoint)):
                    name = f"{year}_{endpoint}_{page}.json"
                    (folder / name).write_text(json.dumps(payload), encoding="utf-8")
                    record(name)
                    manifest["requests"].append({"url": url, "file": name})
                    for race in races:
                        common = {
                            "season": int(race["season"]), "round": int(race["round"]),
                            "event_id": f'{race["season"]}-{int(race["round"]):02d}',
                            "start_utc": race["date"] + "T" + race.get("time", "00:00:00Z"),
                            "circuit_id": race["Circuit"]["circuitId"],
                            "circuit_name": race["Circuit"]["circuitName"],
                            "event_name": race["raceName"],
                        }
                        for item in race[key]:
                            row = dict(common, driver_id=item["Driver"]["driverId"],
                                       driver=item["Driver"].get("code", item["Driver"]["driverId"]),
                                       driver_number=str(item.get("number", "")),
                                       team_id=item["Constructor"]["constructorId"],
                                       team=item["Constructor"]["name"])
                            if endpoint == "results":
                                row.update(actual_position=int(item["position"]), status=item["status"])
                                race_rows.append(row)
                            else:
                                row["qualifying_position"] = int(item["position"])
                                qualifying_rows.append(row)
        for name, rows in (("results", race_rows), ("qualifying", qualifying_rows)):
            table = pd.DataFrame(rows)
            require_columns(table, ["event_id", "driver_id", "start_utc"], name)
            if table.duplicated(["event_id", "driver_id"]).any():
                raise DataContractError(f"Duplicate history identities in {name}.")
            table["start_utc"] = pd.to_datetime(table.start_utc, utc=True)
            table.to_parquet(folder / f"{name}.parquet", index=False)
            record(f"{name}.parquet", len(table))
        manifest["status"] = "complete"
        write_manifest()
        return folder
    except Exception as exc:
        manifest.update(status="failed", error=str(exc))
        write_manifest()
        raise


def load_history(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("status") != "complete":
        raise DataContractError("The history snapshot is incomplete or unsupported.")
    for name, item in manifest["files"].items():
        target = (folder / name).resolve()
        if not target.is_relative_to(folder.resolve()):
            raise DataContractError("History path is outside the snapshot.")
        if sha256(target.read_bytes()).hexdigest() != item["sha256"]:
            raise DataContractError(f"History checksum failed: {name}")
    return (pd.read_parquet(folder / "results.parquet"),
            pd.read_parquet(folder / "qualifying.parquet"), manifest)


def latest_history(root=None):
    root = prepare_dirs(root)
    for file in sorted((root / "data/history").glob("*/manifest.json"), reverse=True):
        if json.loads(file.read_text(encoding="utf-8")).get("status") == "complete":
            return file.parent
    raise FileNotFoundError("No history found. Run: wac history --start-year 2022 --end-year 2025")
