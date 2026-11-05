"""Synthetic contract tests; real benchmark results are documented separately."""
import json
import pandas as pd
import pytest
from wearechecking.contracts import DataContractError
from wearechecking.history import _pages
from wearechecking.modeling import form_features, race_features, training_table, ranked, predict_race
from wearechecking.student import lap_counts, qualifying_baseline


@pytest.fixture
def history():
    rows = []
    for year, order in [(2022, ["a", "b", "c"]), (2023, ["b", "c", "a"]), (2024, ["c", "a", "b"])]:
        for position, driver in enumerate(order, 1):
            rows.append(dict(season=year, event_id=f"{year}-01", start_utc=pd.Timestamp(f"{year}-03-01T15:00Z"),
                             driver_id=driver, team_id="red" if driver in ("a", "b") else "blue",
                             circuit_id="test", actual_position=position, status="Finished"))
    return pd.DataFrame(rows)


@pytest.fixture
def qualifying():
    return pd.DataFrame({"driver_id": ["a", "b", "c"], "team_id": ["red", "red", "blue"],
                         "qualifying_position": [3, 1, 2], "circuit_id": ["test"] * 3,
                         "start_utc": [pd.Timestamp("2024-03-01T15:00Z")] * 3,
                         "season": [2024] * 3, "event_id": ["2024-01"] * 3})


def test_future_and_target_results_cannot_change_features(history, qualifying):
    before = race_features(history, qualifying)
    history.loc[history.season >= 2024, "actual_position"] = [99, 0, -1]
    history.loc[history.season >= 2024, "status"] = "Changed future status"
    after = race_features(history, qualifying)
    pd.testing.assert_frame_equal(before, after)
    assert "actual_position" not in after and "status" not in after
    assert after.history_races.tolist() == [2, 2, 2]


def test_new_driver_uses_team_prior_without_borrowing_identity(history):
    entry = pd.DataFrame({"driver_id": ["new"], "team_id": ["red"]})
    feature = form_features(history, entry, "unseen_circuit", "2024-03-01T15:00Z").iloc[0]
    assert feature.history_races == 0
    assert feature.driver_form == feature.team_form
    assert feature.driver_circuit_form == feature.driver_form


def test_labels_join_after_features_and_roster_mismatch_is_reported(history, qualifying):
    table, excluded = training_table(history, qualifying)
    assert excluded == []
    assert table.set_index("driver_id").loc["a", "actual_position"] == 2
    assert table.set_index("driver_id").loc["a", "history_races"] == 2
    bad = qualifying.copy()
    bad.loc[0, "driver_id"] = "replacement"
    with pytest.raises(DataContractError, match="No complete"):
        training_table(history, bad)


def test_ranks_are_deterministic_and_reject_nan():
    frame = pd.DataFrame({"driver_id": ["b", "a"]})
    assert ranked(frame, [0.5, 0.5]).driver_id.tolist() == ["a", "b"]
    with pytest.raises(DataContractError, match="finite"):
        ranked(frame, [float("nan"), 0.5])


def test_model_cutoff_rejects_training_on_target(tmp_path, qualifying, history):
    from hashlib import sha256
    from wearechecking.modeling import FEATURES
    raw = b"not a pickle; cutoff should reject before loading"
    (tmp_path / "model.joblib").write_bytes(raw)
    (tmp_path / "model.json").write_text(json.dumps({
        "schema_version": 1, "feature_columns": FEATURES,
        "model_sha256": sha256(raw).hexdigest(), "trained_through_utc": "2024-03-01T15:00Z"}))
    with pytest.raises(DataContractError, match="trained on"):
        predict_race(tmp_path, history, qualifying)


def test_jolpica_pagination_counts_result_rows_in_split_races():
    class Client:
        offsets = []
        def get(self, url, params):
            self.offsets.append(params["offset"])
            n = 2 if params["offset"] == 0 else 1
            return {"MRData": {"total": "3", "RaceTable": {
                "Races": [{"Results": [{}] * n}]}}}, url
    client = Client()
    pages = list(_pages(client, 2024, "results"))
    assert len(pages) == 2 and client.offsets == [0, 2]


def test_completed_reference_functions_do_not_mutate_inputs(qualifying):
    old = qualifying.copy(deep=True)
    result = qualifying_baseline(qualifying)
    assert result.driver_id.tolist() == ["b", "c", "a"]
    pd.testing.assert_frame_equal(qualifying, old)
    laps = pd.DataFrame({"DriverNumber": ["1", "1", "1", "2", None],
                         "LapNumber": [1, "1", 0, 2, 3]})
    assert lap_counts(laps).set_index("driver_number").lap_count.to_dict() == {"1": 1, "2": 1}


def test_lapped_finish_counts_as_completed_race(history):
    history.loc[(history.driver_id == "a") & (history.season == 2022), "status"] = "Lapped"
    history.loc[(history.driver_id == "a") & (history.season == 2023), "status"] = "Collision"
    entry = pd.DataFrame({"driver_id": ["a"], "team_id": ["red"]})
    feature = form_features(history, entry, "test", "2024-03-01T15:00Z").iloc[0]
    assert feature.driver_finish_rate == 0.5
