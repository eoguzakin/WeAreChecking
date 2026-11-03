import pandas as pd
import pytest
from wearechecking.contracts import DataContractError, validate_ranking
from wearechecking.features import qualifying_inputs
from wearechecking.evaluation import save_prediction, evaluate_saved

CUTOFF = "2024-03-02T12:00:00Z"


def test_features_only_read_qualifying_and_allowlisted_columns(snapshot):
    before = qualifying_inputs(snapshot, CUTOFF, mode="reconstructed")
    snapshot.race["Position"] = [3, 2, 1]
    after = qualifying_inputs(snapshot, CUTOFF, mode="reconstructed")
    pd.testing.assert_frame_equal(before.frame, after.frame)
    assert snapshot.accesses == [("Q", "results"), ("Q", "results")]
    assert set(before.frame) == {"driver_id", "driver", "team", "qualifying_position"}


@pytest.mark.parametrize("cutoff", ["2024-03-01T16:30:00Z", "2024-03-02T15:00:00Z", "2024-03-02"])
def test_invalid_forecast_times_rejected(snapshot, cutoff):
    with pytest.raises(DataContractError):
        qualifying_inputs(snapshot, cutoff, mode="reconstructed")


def test_live_claim_on_retrospective_source_rejected(snapshot):
    with pytest.raises(DataContractError, match="reconstructed"):
        qualifying_inputs(snapshot, CUTOFF, mode="live")


def test_unknown_driver_identity_rejected(snapshot):
    snapshot.q.loc[0, "DriverId"] = None
    with pytest.raises(DataContractError, match="kimli"):
        qualifying_inputs(snapshot, CUTOFF, mode="reconstructed")


@pytest.mark.parametrize("positions", [[1, 1, 3], [1, 2, 4], [1, 2, None], [1, 2, 2.5]])
def test_rank_must_be_permutation(positions):
    frame = pd.DataFrame({"driver_id": ["a", "b", "c"], "predicted_position": positions})
    with pytest.raises(DataContractError):
        validate_ranking(frame, ["a", "b", "c"])


def test_save_then_evaluate_and_detect_tampering(snapshot, tmp_path):
    inputs = qualifying_inputs(snapshot, CUTOFF, mode="reconstructed")
    prediction = pd.DataFrame({"driver_id": ["a", "b", "c"], "predicted_position": [2, 1, 3]})
    folder = save_prediction(prediction, inputs, root=tmp_path)
    comparison, metrics = evaluate_saved(folder, snapshot)
    assert metrics["position_mae"] == pytest.approx(4 / 3)
    assert len(comparison) == 3
    with (folder / "prediction.csv").open("a") as stream:
        stream.write("\n")
    with pytest.raises(DataContractError, match="değiştirilmiş"):
        evaluate_saved(folder, snapshot)


def test_replacement_driver_requires_entry_resolution(snapshot, tmp_path):
    inputs = qualifying_inputs(snapshot, CUTOFF, mode="reconstructed")
    prediction = pd.DataFrame({"driver_id": ["a", "b", "c"], "predicted_position": [2, 1, 3]})
    folder = save_prediction(prediction, inputs, root=tmp_path)
    snapshot.race.loc[0, "DriverId"] = "substitute"
    with pytest.raises(DataContractError, match="katılımcıları farklı"):
        evaluate_saved(folder, snapshot)
