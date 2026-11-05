"""Reviewed event records, with publication and observation-time gates."""
from urllib.parse import urlsplit
import pandas as pd
from .contracts import DataContractError, require_columns, utc_timestamp

KINDS = {"injury", "withdrawal", "substitution", "disqualification"}
ENTRY_COLUMNS = ["driver_id", "driver", "team_id", "team", "driver_number"]


def validate_entries(entries):
    require_columns(entries, ENTRY_COLUMNS, "Entry list")
    out = entries[ENTRY_COLUMNS].copy().astype("string")
    if out.isna().any().any() or out.apply(lambda c: c.str.strip().eq("")).any().any():
        raise DataContractError("Entry fields must be nonempty.")
    if out.driver_id.duplicated().any() or out.driver_number.duplicated().any():
        raise DataContractError("Driver identities and numbers must be unique within a target session.")
    return out


def active_events(records, cutoff, target_start):
    cutoff, target_start = utc_timestamp(cutoff), utc_timestamp(target_start)
    if not isinstance(records, list):
        raise DataContractError("Events must be a JSON list.")
    seen, active = set(), []
    for item in records:
        required = {"event_id", "kind", "driver_id", "effective_at", "published_at",
                    "observed_at", "source_url", "confirmed"}
        if not isinstance(item, dict) or required - set(item):
            raise DataContractError("An event record is missing required provenance fields.")
        if item["event_id"] in seen:
            raise DataContractError("Duplicate event_id in the event ledger.")
        seen.add(item["event_id"])
        if item.get("session") not in (None, "FP1", "FP2", "FP3", "Q", "SQ", "S", "R"):
            raise DataContractError("Unknown session in event record.")
        if item["kind"] == "disqualification" and not item.get("session"):
            raise DataContractError("Disqualification requires a session scope.")
        if item["kind"] not in KINDS:
            raise DataContractError(f'Unsupported event kind: {item["kind"]}')
        if urlsplit(item["source_url"]).scheme not in ("https", "http"):
            raise DataContractError("Each event needs a source URL.")
        published, observed, effective = (utc_timestamp(item[k]) for k in
                                           ("published_at", "observed_at", "effective_at"))
        if observed < published:
            raise DataContractError("An event cannot be observed before it was published.")
        if item["confirmed"] is not True:
            continue
        if published <= cutoff and observed <= cutoff and effective <= target_start:
            active.append(item)
    return sorted(active, key=lambda x: (utc_timestamp(x["effective_at"]), x["event_id"]))


def apply_events(entries, records, cutoff, target_start, session):
    out = validate_entries(entries)
    active = active_events(records, cutoff, target_start)
    applied, annotations = [], []
    for event in active:
        if event.get("session") not in (None, session):
            continue
        kind, driver_id = event["kind"], event["driver_id"]
        if kind in ("withdrawal", "substitution"):
            if driver_id not in set(out.driver_id):
                raise DataContractError(f"Event {event['event_id']} refers to an absent driver.")
            old = out.loc[out.driver_id.eq(driver_id)].iloc[0].to_dict()
            out = out.loc[~out.driver_id.eq(driver_id)].copy()
            if kind == "substitution":
                replacement = event.get("replacement", {})
                if not {"driver_id", "driver", "driver_number"} <= set(replacement):
                    raise DataContractError("A substitution needs the replacement's permanent ID, code and number.")
                new = dict(old, **{k: replacement[k] for k in ENTRY_COLUMNS if k in replacement})
                if new["driver_id"] == driver_id:
                    raise DataContractError("A replacement must have a distinct permanent identity.")
                out = pd.concat([out, pd.DataFrame([new])], ignore_index=True)
        else:
            annotations.append(f"{kind}: {driver_id}; no invented pace or injury penalty")
        applied.append(event["event_id"])
    if out.empty:
        raise DataContractError("The event ledger removed every entry.")
    return validate_entries(out), applied, annotations
