"""OpenF1 timings + Jolpica classifications. No F1TV credentials needed."""
import pandas as pd
from .contracts import DataContractError, require_columns
from .http import PublicClient


def resolve_sessions(client, year, schedule):
    races, races_url = client.get("https://api.openf1.org/v1/sessions",
                                  {"year": year, "session_name": "Race"})
    target_day = pd.Timestamp(schedule.loc[schedule.session_code == "R", "start_utc"].iloc[0]).date()
    matching = [row for row in races if pd.Timestamp(row["date_start"]).date() == target_day]
    if len(matching) != 1:
        raise DataContractError("Could not uniquely match the OpenF1 weekend. Review the date/circuit mapping.")
    sessions, url = client.get("https://api.openf1.org/v1/sessions",
                               {"meeting_key": matching[0]["meeting_key"]})
    return sessions, [(races, races_url, "race_sessions"), (sessions, url, "meeting_sessions")]


def jolpica_results(client, year, round_number, code):
    endpoint, key = {"Q": ("qualifying", "QualifyingResults"),
                     "R": ("results", "Results"),
                     "S": ("sprint", "SprintResults")}[code]
    payload, url = client.get(f"https://api.jolpi.ca/ergast/f1/{year}/{round_number}/{endpoint}/",
                               {"format": "json", "limit": 100})
    races = payload["MRData"]["RaceTable"]["Races"]
    if len(races) != 1 or not races[0].get(key):
        raise DataContractError(f"Jolpica {code} results are missing.")
    raw = races[0][key]
    if int(payload["MRData"]["total"]) != len(raw):
        raise DataContractError("The Jolpica response is incomplete or paginated.")
    records = []
    for row in raw:
        driver = row["Driver"]
        records.append({
            "DriverId": driver["driverId"], "DriverNumber": str(row["number"]),
            "Abbreviation": driver.get("code"), "TeamName": row["Constructor"]["name"],
            "Position": float(row["position"]), "Status": row.get("status"),
            "Q1": row.get("Q1"), "Q2": row.get("Q2"), "Q3": row.get("Q3"),
        })
    return pd.DataFrame(records), payload, url


def normalize_laps(rows):
    frame = pd.DataFrame(rows)
    require_columns(frame, ["driver_number", "lap_number", "lap_duration", "date_start"], "OpenF1 laps")
    # Keep source fields too. DriverNumber is only a session-scoped join key.
    frame["DriverNumber"] = frame.driver_number.astype("Int64").astype("string")
    frame["LapNumber"] = pd.to_numeric(frame.lap_number, errors="coerce")
    frame["LapTime"] = pd.to_timedelta(frame.lap_duration, unit="s")
    frame["LapStartDate"] = pd.to_datetime(frame.date_start, utc=True, format="mixed")
    return frame


def normalize_drivers(rows):
    frame = pd.DataFrame(rows)
    require_columns(frame, ["driver_number", "name_acronym", "team_name"], "OpenF1 drivers")
    return pd.DataFrame({
        "DriverNumber": frame.driver_number.astype("Int64").astype("string"),
        "Abbreviation": frame.name_acronym,
        "TeamName": frame.team_name,
        # FP participants must NOT inherit the race driver's identity at the same seat.
        "DriverId": None, "Position": None, "Status": None,
    })
