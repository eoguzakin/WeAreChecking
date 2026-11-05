"""Experimental session-by-session ranking updates from completed observations."""
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import uuid

import numpy as np
import pandas as pd

from .contracts import DataContractError, require_columns, utc_timestamp
from .events import active_events, apply_events, validate_entries
from .modeling import form_features, ranked
from .paths import prepare_dirs


def load_entry_file(file, cutoff):
    document = json.loads(Path(file).read_text(encoding="utf-8"))
    if document.get("mode") != "reconstructed":
        raise DataContractError("This first draft supports reconstructed entry lists only.")
    if utc_timestamp(document["available_at"]) > utc_timestamp(cutoff):
        raise DataContractError("The entry list is later than the requested cutoff.")
    if not document.get("circuit_id"):
        raise DataContractError("The entry file needs the Jolpica circuit_id.")
    return validate_entries(pd.DataFrame(document["entries"])), document


def _observation(snapshot, code, entries, excluded_ids):
    participants = snapshot.table(code, "participants")
    require_columns(participants, ["DriverNumber", "Abbreviation"], "Session participants")
    # A reused car number must not transfer the old driver's observed pace.
    identity = entries.merge(
        participants[["DriverNumber", "Abbreviation"]],
        left_on=["driver_number", "driver"], right_on=["DriverNumber", "Abbreviation"],
        validate="one_to_one")
    identity = identity.loc[~identity.driver_id.isin(excluded_ids)]
    if identity.empty:
        return {}
    info = snapshot.manifest["sessions"][code]
    if info.get("classification_available") and code in ("Q", "S", "SQ"):
        result = snapshot.table(code, "results")
        require_columns(result, ["DriverId", "Position"], f"{code} classification")
        matched = identity.merge(result[["DriverId", "Position"]],
                                 left_on="driver_id", right_on="DriverId", validate="one_to_one")
        score = (pd.to_numeric(matched.Position) - 1) / max(len(result) - 1, 1)
        return dict(zip(matched.driver_id, score))
    laps = snapshot.table(code, "laps").copy()
    require_columns(laps, ["DriverNumber", "LapTime"], f"{code} laps")
    laps["seconds"] = pd.to_timedelta(laps.LapTime).dt.total_seconds()
    keep = laps.seconds.gt(0) & np.isfinite(laps.seconds)
    if "is_pit_out_lap" in laps:
        keep &= ~laps.is_pit_out_lap.fillna(False).astype(bool)
    pace = (laps.loc[keep].sort_values("seconds").groupby("DriverNumber").head(3)
            .groupby("DriverNumber").seconds.median().sort_values())
    # This is an observed timing proxy, not an official SQ/FP classification.
    score = (pace.rank(method="average") - 1) / max(len(pace) - 1, 1)
    return {row.driver_id: float(score[row.driver_number])
            for row in identity.itertuples() if row.driver_number in score.index}


def forecast_weekend(snapshot, history, entries, circuit_id, cutoff, events=None):
    cutoff = utc_timestamp(cutoff)
    entries = validate_entries(entries)
    events = [] if events is None else events
    schedule = snapshot.schedule().sort_values("start_utc")
    upcoming = schedule.loc[pd.to_datetime(schedule.start_utc, utc=True) > cutoff]
    if upcoming.empty:
        raise DataContractError("There are no unstarted sessions after this cutoff.")
    completed = [code for code in schedule.session_code
                 if code in snapshot.manifest["sessions"]
                 and utc_timestamp(snapshot.manifest["sessions"][code]["event_end_bound_utc"]) < cutoff]
    output = []
    for session in upcoming.itertuples():
        roster, applied, notes = apply_events(entries, events, cutoff, session.start_utc, session.session_code)
        form = form_features(history, roster, circuit_id, schedule.iloc[0].start_utc)
        form = roster.merge(form, on=["driver_id", "team_id"], validate="one_to_one")
        base = 0.5 * form.driver_form + 0.3 * form.team_form + 0.2 * form.driver_circuit_form
        total, denominator = base.copy(), pd.Series(1.0, index=form.index)
        used = []
        eligible = active_events(events, cutoff, session.start_utc)
        for code in completed:
            disqualified = {e["driver_id"] for e in eligible
                            if e["kind"] == "disqualification" and e.get("session") == code}
            observation = _observation(snapshot, code, roster, disqualified)
            target = session.session_code
            if code.startswith("FP"):
                weight = 0.8 / max(sum(c.startswith("FP") for c in completed), 1)
            elif code == "Q" and target == "R":
                weight = 2.5
            elif code == "SQ" and target == "S":
                weight = 2.5
            elif code == "S" and target == "R":
                weight = 0.8
            else:
                continue
            observed = form.driver_id.map(observation)
            mask = observed.notna()
            if mask.any():
                total.loc[mask] += weight * observed.loc[mask]
                denominator.loc[mask] += weight
                used.append(code)
        prediction = ranked(form, total / denominator).merge(
            form[["driver_id", "driver", "team", "history_races"]], on="driver_id", validate="one_to_one")
        output.append({
            "session": session.session_code, "start_utc": utc_timestamp(session.start_utc).isoformat(),
            "method": "experimental_history_and_session_blend_v1",
            "observations_used": used, "applied_event_ids": applied, "notes": notes,
            "ranking": prediction.to_dict(orient="records"),
        })
    return {
        "schema_version": 1, "status": "under active development", "mode": "reconstructed",
        "cutoff_utc": cutoff.isoformat(), "snapshot_id": snapshot.path.name,
        "source_observed_at": snapshot.manifest["observed_at"],
        "event_name": snapshot.manifest.get("event_name", "Synthetic test event"),
        "circuit_id": circuit_id, "completed_sessions": completed, "forecasts": output,
        "limitations": [
            "Fixed heuristic weights; these all-session rankings have not been backtested.",
            "FP target is fastest-lap ordering; run plans and fuel loads are unknown.",
            "SQ observations use a fastest-lap proxy when official classification is unavailable.",
            "Only completed sessions are used; no in-session prediction updates.",
            "Weather is downloaded for exploration but not modeled; no forecast weather feed.",
            "Events are manually reviewed records; automatic news ingestion is not implemented.",
            "Injury is annotated without inventing an effect; a withdrawal must be explicit.",
            "Reconstructed source data and roster are not proof of historical availability.",
            "Unknown drivers use team form; no probability or confidence calibration.",
        ],
    }


def save_weekend(report, root=None):
    root = prepare_dirs(root)
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    folder = root / "reports/weekends" / token
    folder.mkdir(parents=True)
    payload = dict(report, created_at=datetime.now(timezone.utc).isoformat())
    text = json.dumps(payload, indent=2, allow_nan=False)
    (folder / "forecast.json").write_text(text, encoding="utf-8")
    labels = {"FP1": "Free practice 1", "FP2": "Free practice 2", "FP3": "Free practice 3",
              "Q": "Qualifying", "SQ": "Sprint qualifying", "S": "Sprint", "R": "Grand Prix"}
    sections = []
    for forecast in report["forecasts"]:
        frame = pd.DataFrame(forecast["ranking"])
        sections.append(f'<section><h2>{escape(labels[forecast["session"]])}</h2>'
                        f'<p>Evidence: {escape(", ".join(forecast["observations_used"]) or "historical form only")}</p>'
                        + frame[["predicted_position", "driver", "team", "history_races"]]
                        .rename(columns={"predicted_position": "Position", "driver": "Driver", "team": "Team",
                                         "history_races": "Prior race entries"}).to_html(index=False, escape=True, border=0) + "</section>")
    html = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WeAreChecking | Weekend forecast</title>
<style>body{font:16px system-ui;background:#0c1420;color:#e7edf5;max-width:1100px;margin:3rem auto;padding:0 24px}
h1{font-size:42px}h2{color:#72dece}.tag{color:#ffca80}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:24px}
section{background:#162233;padding:24px;border-radius:16px;overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}
td,th{text-align:left;padding:9px;border-bottom:1px solid #334158}li{margin:8px 0}footer{color:#a9bad0;margin-top:30px}</style>
<p class="tag">FIRST DRAFT / UNDER ACTIVE DEVELOPMENT</p><h1>WeAreChecking</h1>"""
    html += f'<p>{escape(report["event_name"])} · Cutoff {escape(report["cutoff_utc"])}</p>'
    html += "<p>Experimental reconstructed rankings. Scores are not probabilities.</p><main>"
    html += "".join(sections) + "</main><footer><h2>Interpretation and limits</h2><ul>"
    html += "".join(f"<li>{escape(item)}</li>" for item in report["limitations"]) + "</ul></footer></html>"
    (folder / "forecast.html").write_text(html, encoding="utf-8")
    (folder / "checksums.json").write_text(json.dumps({
        "forecast.json": sha256(text.encode("utf-8")).hexdigest(),
        "forecast.html": sha256(html.encode("utf-8")).hexdigest()}, indent=2), encoding="utf-8")
    return folder
