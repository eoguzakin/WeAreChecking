"""Evaluation is separate and only accepts a saved prediction artifact."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import uuid
import pandas as pd

from .contracts import DataContractError, require_columns, validate_ranking
from .paths import prepare_dirs


def save_prediction(prediction, inputs, root=None):
    validate_ranking(prediction, inputs.frame.driver_id)
    root = prepare_dirs(root)
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    folder = root / "reports/predictions" / token
    folder.mkdir(parents=True, exist_ok=False)
    table = prediction[["driver_id", "predicted_position"]].sort_values("predicted_position")
    table.to_csv(folder / "prediction.csv", index=False)
    meta = dict(inputs.metadata, created_at=datetime.now(timezone.utc).isoformat(),
                prediction_sha256=sha256((folder / "prediction.csv").read_bytes()).hexdigest(),
                model="student_qualifying_baseline_v0")
    (folder / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return folder


def evaluate_saved(folder, snapshot):
    folder = Path(folder)
    meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    if meta["snapshot_id"] != snapshot.path.name:
        raise DataContractError("The prediction was created from a different snapshot.")
    if sha256((folder / "prediction.csv").read_bytes()).hexdigest() != meta["prediction_sha256"]:
        raise DataContractError("The saved prediction was modified; create a new prediction record.")
    prediction = pd.read_csv(folder / "prediction.csv")
    results = snapshot.table("R", "results")
    require_columns(results, ["DriverId", "Position", "Status"], "Race results")
    actual = results[["DriverId", "Position", "Status"]].rename(
        columns={"DriverId": "driver_id", "Position": "actual_position", "Status": "status"})
    if actual.driver_id.isna().any() or actual.driver_id.duplicated().any():
        raise DataContractError("A race driver identity is missing or duplicated.")
    if set(prediction.driver_id) != set(actual.driver_id):
        raise DataContractError("Q and R have different participants: resolve substitutions/DNS before evaluation.")
    actual["actual_position"] = pd.to_numeric(actual.actual_position, errors="coerce")
    if sorted(actual.actual_position.tolist()) != list(range(1, len(actual) + 1)):
        raise DataContractError("The race classification is incomplete; review the DNF/DNS/DSQ status.")
    comparison = prediction.merge(actual, on="driver_id", validate="one_to_one")
    comparison["absolute_error"] = (comparison.predicted_position - comparison.actual_position).abs()
    metrics = {
        "n_drivers": len(comparison),
        "position_mae": float(comparison.absolute_error.mean()),
        "spearman": float(comparison.predicted_position.corr(comparison.actual_position, method="spearman")),
        "interpretation": "Single historical weekend; final classification includes classified retirements. Not generalization evidence.",
    }
    return comparison.sort_values("predicted_position"), metrics
