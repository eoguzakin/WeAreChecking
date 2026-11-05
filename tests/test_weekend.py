"""Synthetic timelines exercise session and news availability, not model quality."""
from copy import deepcopy
from pathlib import Path
import pandas as pd
import pytest
from wearechecking.contracts import DataContractError
from wearechecking.events import apply_events, active_events
from wearechecking.weekend import forecast_weekend


@pytest.fixture
def entries():
    return pd.DataFrame({"driver_id": ["a", "b"], "driver": ["AAA", "BBB"],
                         "driver_number": ["1", "2"], "team_id": ["red", "blue"],
                         "team": ["Red", "Blue"]})


@pytest.fixture
def past():
    return pd.DataFrame({"event_id": ["2023-01"] * 2,
                         "start_utc": pd.to_datetime(["2023-03-01T15:00Z"] * 2),
                         "driver_id": ["a", "b"], "team_id": ["red", "blue"],
                         "circuit_id": ["test"] * 2, "actual_position": [1, 2],
                         "status": ["Finished"] * 2})


@pytest.fixture
def weekend(entries):
    class SyntheticWeekend:
        path = Path("synthetic-weekend")
        manifest = {"observed_at": "2026-01-01T00:00:00Z", "sessions": {
            "FP1": {"event_end_bound_utc": "2024-03-01T11:00Z", "classification_available": False},
            "SQ": {"event_end_bound_utc": "2024-03-01T15:00Z", "classification_available": True},
            "S": {"event_end_bound_utc": "2024-03-02T11:00Z", "classification_available": True},
            "Q": {"event_end_bound_utc": "2024-03-02T15:00Z", "classification_available": True},
            "R": {"event_end_bound_utc": "2024-03-03T16:00Z", "classification_available": True}}}
        accesses = []
        def schedule(self):
            return pd.DataFrame({"session_code": ["FP1", "SQ", "S", "Q", "R"],
                                 "start_utc": pd.to_datetime(["2024-03-01T10:00Z", "2024-03-01T14:00Z",
                                                             "2024-03-02T10:00Z", "2024-03-02T14:00Z",
                                                             "2024-03-03T14:00Z"])})
        def table(self, code, name):
            self.accesses.append((code, name))
            if name == "participants":
                return pd.DataFrame({"DriverNumber": ["1", "2"], "Abbreviation": ["AAA", "BBB"]})
            if name == "laps":
                return pd.DataFrame({"DriverNumber": ["1", "2"], "LapTime": pd.to_timedelta([92, 90], unit="s")})
            if name == "results":
                return pd.DataFrame({"DriverId": ["a", "b"], "Position": [2, 1]})
            raise AssertionError(name)
    return SyntheticWeekend()


def event(kind="substitution"):
    return {"event_id": "test-change", "kind": kind, "driver_id": "a",
            "effective_at": "2024-03-01T09:00Z", "published_at": "2024-03-01T08:00Z",
            "observed_at": "2024-03-01T08:05Z", "source_url": "https://example.com/synthetic",
            "confirmed": True, "replacement": {"driver_id": "new", "driver": "NEW", "driver_number": "1"}}


def test_before_weekend_forecasts_all_sessions_without_reading_results(weekend, past, entries):
    report = forecast_weekend(weekend, past, entries, "test", "2024-03-01T09:00Z")
    assert [f["session"] for f in report["forecasts"]] == ["FP1", "SQ", "S", "Q", "R"]
    assert report["completed_sessions"] == []
    assert weekend.accesses == []


def test_updates_use_completed_sessions_only(weekend, past, entries):
    early = forecast_weekend(weekend, past, entries, "test", "2024-03-01T12:00Z")
    assert {code for code, name in weekend.accesses} == {"FP1"}
    weekend.accesses.clear()
    late = forecast_weekend(weekend, past, entries, "test", "2024-03-02T16:00Z")
    assert [f["session"] for f in late["forecasts"]] == ["R"]
    assert ("R", "results") not in weekend.accesses
    assert late["forecasts"][0]["ranking"][0]["driver_id"] == "b"
    assert late["forecasts"][0]["observations_used"] == ["FP1", "S", "Q"]
    assert early["cutoff_utc"] != late["cutoff_utc"]


def test_exact_session_end_not_available_yet(weekend, past, entries):
    report = forecast_weekend(weekend, past, entries, "test", "2024-03-01T11:00Z")
    assert report["completed_sessions"] == []
    assert weekend.accesses == []


def test_news_must_have_been_observed_by_cutoff(entries):
    change = event()
    change["observed_at"] = "2024-03-02T08:00Z"
    roster, applied, _ = apply_events(entries, [change], "2024-03-01T12:00Z", "2024-03-02T10:00Z", "S")
    assert set(roster.driver_id) == {"a", "b"} and applied == []
    change["confirmed"] = False
    assert active_events([change], "2024-03-03T12:00Z", "2024-03-03T14:00Z") == []


def test_substitute_has_own_identity_and_no_old_drivers_pace(weekend, past, entries):
    report = forecast_weekend(weekend, past, entries, "test", "2024-03-01T12:00Z", [event()])
    for forecast in report["forecasts"]:
        ranks = pd.DataFrame(forecast["ranking"]).set_index("driver_id")
        assert set(ranks.index) == {"new", "b"}
        assert ranks.loc["new", "history_races"] == 0
        # Same car number, different participant code: no inherited FP1 observation.
        assert ranks.loc["new", "score"] == 0.0


def test_session_disqualification_does_not_ban_future_entry(entries):
    dq = event("disqualification")
    dq["session"] = "Q"
    roster, applied, notes = apply_events(entries, [dq], "2024-03-02T16:00Z", "2024-03-03T14:00Z", "R")
    assert set(roster.driver_id) == {"a", "b"}
    assert applied == []


def test_injury_is_annotation_but_withdrawal_removes_entry(entries):
    roster, applied, notes = apply_events(entries, [event("injury")],
                                          "2024-03-02T16:00Z", "2024-03-03T14:00Z", "R")
    assert len(roster) == 2 and notes
    roster, _, _ = apply_events(entries, [event("withdrawal")],
                                "2024-03-02T16:00Z", "2024-03-03T14:00Z", "R")
    assert roster.driver_id.tolist() == ["b"]


def test_no_future_session_means_no_forecast(weekend, past, entries):
    with pytest.raises(DataContractError, match="no unstarted"):
        forecast_weekend(weekend, past, entries, "test", "2024-03-03T17:00Z")
