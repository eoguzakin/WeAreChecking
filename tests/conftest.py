"""All fixtures here are SYNTHETIC. No API calls, no real driver results."""
from pathlib import Path
import pandas as pd
import pytest


@pytest.fixture
def snapshot(tmp_path):
    class SyntheticSnapshot:
        path = tmp_path / "synthetic"
        manifest = {
            "observed_at": "2026-01-01T00:00:00Z",
            "sessions": {"Q": {"event_end_bound_utc": "2024-03-01T17:10:00Z"}},
        }
        q = pd.DataFrame({
            "DriverId": ["a", "b", "c"], "Abbreviation": ["AAA", "BBB", "CCC"],
            "TeamName": ["Red", "Blue", "Red"], "Position": [2, 1, 3],
            "Points": [999, 999, 999], "Status": ["SECRET"] * 3,
        })
        race = pd.DataFrame({"DriverId": ["a", "b", "c"],
                             "Position": [1, 3, 2], "Status": ["Finished"] * 3})
        accesses = []

        def schedule(self):
            return pd.DataFrame({"session_code": ["Q", "R"],
                                 "start_utc": pd.to_datetime(["2024-03-01T16:00:00Z", "2024-03-02T15:00:00Z"])})

        def table(self, session, name):
            self.accesses.append((session, name))
            return (self.q if session == "Q" else self.race).copy()
    return SyntheticSnapshot()
