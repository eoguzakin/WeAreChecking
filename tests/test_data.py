from hashlib import sha256
import json
import pandas as pd
import pytest
from wearechecking.contracts import DataContractError, require_columns
from wearechecking.data import schedule_from_event, open_snapshot
from wearechecking.provider import normalize_laps, normalize_drivers
from wearechecking.learning import check_lap_counts, check_baseline


@pytest.mark.parametrize("names,expected", [
    (["Practice 1","Practice 2","Practice 3","Qualifying","Race"], ["FP1","FP2","FP3","Q","R"]),
    (["Practice 1","Sprint Qualifying","Sprint","Qualifying","Race"], ["FP1","SQ","S","Q","R"]),
    (["Practice 1","Qualifying","Sprint Shootout","Sprint","Race"], ["FP1","Q","SQ","S","R"]),
])
def test_weekend_format_comes_from_schedule(names, expected):
    event = {}
    for slot, name in enumerate(names, 1):
        event[f"Session{slot}"] = name
        event[f"Session{slot}DateUtc"] = pd.Timestamp("2024-01-01") + pd.Timedelta(hours=slot)
    result = schedule_from_event(event)
    assert result.session_code.tolist() == expected
    assert str(result.start_utc.dt.tz) == "UTC"


def test_missing_column_explains_actual_schema():
    with pytest.raises(DataContractError, match="Mevcut kolonlar"):
        require_columns(pd.DataFrame({"wrong": [1]}), ["DriverNumber"], "laps")


def test_snapshot_hash_detects_edit(tmp_path):
    table = tmp_path / "test.parquet"
    pd.DataFrame({"number": [1]}).to_parquet(table)
    metadata = {"schema_version": 1, "status": "complete",
                "files": {"test.parquet": {"sha256": sha256(table.read_bytes()).hexdigest()}}}
    (tmp_path / "manifest.json").write_text(json.dumps(metadata))
    open_snapshot(tmp_path)
    table.write_bytes(b"edited")
    with pytest.raises(DataContractError, match="değişmiş"):
        open_snapshot(tmp_path)


def test_missing_lap_time_stays_missing():
    result = normalize_laps([{"driver_number": 12, "lap_number": 1, "lap_duration": None,
                              "date_start": None}])
    assert pd.isna(result.LapTime.iloc[0])
    assert result.DriverNumber.iloc[0] == "12"


def test_fp_participant_is_not_assigned_race_identity():
    result = normalize_drivers([{"driver_number": 12, "name_acronym": "NEW", "team_name": "Test"}])
    assert result.DriverId.isna().all()


def test_pending_exercise_is_not_a_pass():
    assert check_lap_counts(None, None).startswith("BEKLİYOR")
    assert check_baseline(None, None).startswith("BEKLİYOR")


def test_lap_feedback_ignores_duplicate_invalid_laps():
    laps = pd.DataFrame({"DriverNumber": ["1"] * 5 + ["2"],
                         "LapNumber": [1, 1, 2, 0, None, 1]})
    answer = pd.DataFrame({"driver_number": ["1", "2"], "lap_count": [2, 1]})
    assert check_lap_counts(answer, laps).startswith("TAMAM")
