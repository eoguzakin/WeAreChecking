"""Chronological race modeling. Target results never enter a feature row."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import uuid

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .contracts import DataContractError, require_columns, utc_timestamp, validate_ranking
from .history import load_history
from .paths import prepare_dirs

NUMERIC = ["qualifying_fraction", "driver_form", "team_form", "driver_circuit_form",
           "team_circuit_form", "driver_finish_rate", "history_races"]
CATEGORICAL = ["circuit_id", "team_id"]
FEATURES = NUMERIC + CATEGORICAL


def past_results(results, before):
    require_columns(results, ["start_utc", "event_id", "driver_id", "team_id",
                              "circuit_id", "actual_position", "status"], "History")
    # The day boundary is deliberately conservative: never use another session
    # from the target day as historical race form.
    cutoff = utc_timestamp(before).normalize()
    past = results.loc[pd.to_datetime(results.start_utc, utc=True) < cutoff].copy()
    if past.empty:
        return past.assign(fraction=pd.Series(dtype=float), finished=pd.Series(dtype=float))
    past = past.sort_values(["start_utc", "event_id", "actual_position", "driver_id"])
    size = past.groupby("event_id").driver_id.transform("size")
    past["fraction"] = (past.actual_position - 1) / (size - 1).clip(lower=1)
    past["finished"] = (past.status.isin(["Finished", "Lapped"]) | past.status.str.match(r"^\+\d+ Laps?$")).astype(float)
    return past


def form_features(results, entries, circuit_id, before):
    require_columns(entries, ["driver_id", "team_id"], "Entry list")
    if entries.driver_id.isna().any() or entries.driver_id.duplicated().any():
        raise DataContractError("Entry identities must be nonempty and unique.")
    past = past_results(results, before)
    rows = []
    for entry in entries.itertuples():
        driver = past.loc[past.driver_id.eq(entry.driver_id)]
        team = past.loc[past.team_id.eq(entry.team_id)]
        team_form = float(team.tail(10).fraction.mean()) if len(team) else 0.5
        driver_form = float(driver.tail(5).fraction.mean()) if len(driver) else team_form
        dc = driver.loc[driver.circuit_id.eq(circuit_id)].tail(3)
        tc = team.loc[team.circuit_id.eq(circuit_id)].tail(6)
        rows.append({"driver_id": entry.driver_id, "team_id": entry.team_id,
                     "circuit_id": circuit_id, "driver_form": driver_form,
                     "team_form": team_form,
                     # Shrink sparse circuit evidence toward general form.
                     "driver_circuit_form": (dc.fraction.sum() + 3 * driver_form) / (len(dc) + 3),
                     "team_circuit_form": (tc.fraction.sum() + 6 * team_form) / (len(tc) + 6),
                     "driver_finish_rate": float(driver.tail(10).finished.mean()) if len(driver) else 0.8,
                     "history_races": len(driver)})
    return pd.DataFrame(rows)


def race_features(results, qualifying):
    require_columns(qualifying, ["driver_id", "team_id", "circuit_id", "start_utc",
                                 "qualifying_position"], "Qualifying entries")
    if qualifying.circuit_id.nunique() != 1 or qualifying.start_utc.nunique() != 1:
        raise DataContractError("Build features for exactly one event.")
    n = len(qualifying)
    if sorted(qualifying.qualifying_position.tolist()) != list(range(1, n + 1)):
        raise DataContractError("Qualifying must be a complete classification.")
    frame = form_features(results, qualifying, qualifying.iloc[0].circuit_id, qualifying.iloc[0].start_utc)
    q = qualifying[["driver_id", "qualifying_position"]]
    frame = frame.merge(q, on="driver_id", validate="one_to_one")
    frame["qualifying_fraction"] = (frame.qualifying_position - 1) / max(n - 1, 1)
    return frame


def training_table(results, qualifying):
    rows, excluded = [], []
    for event_id, q in qualifying.sort_values(["start_utc", "driver_id"]).groupby("event_id", sort=False):
        actual = results.loc[results.event_id.eq(event_id)]
        if set(q.driver_id) != set(actual.driver_id):
            excluded.append({"event_id": event_id, "reason": "Q/R roster mismatch"})
            continue
        if sorted(actual.actual_position.tolist()) != list(range(1, len(actual) + 1)):
            excluded.append({"event_id": event_id, "reason": "incomplete classification"})
            continue
        if sorted(q.qualifying_position.tolist()) != list(range(1, len(q) + 1)):
            excluded.append({"event_id": event_id, "reason": "incomplete qualifying classification"})
            continue
        features = race_features(results, q)
        # Labels are joined only after the feature builder has returned.
        frame = features.merge(actual[["driver_id", "actual_position"]], on="driver_id", validate="one_to_one")
        frame["target"] = (frame.actual_position - 1) / max(len(frame) - 1, 1)
        frame["event_id"], frame["season"] = event_id, int(q.iloc[0].season)
        frame["start_utc"] = q.iloc[0].start_utc
        rows.append(frame)
    if not rows:
        raise DataContractError("No complete matched events are available.")
    return pd.concat(rows, ignore_index=True), excluded


def pipeline(estimator):
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    transform = ColumnTransformer([
        ("numeric", numeric, NUMERIC),
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL)])
    return Pipeline([("features", transform), ("model", estimator)])


def ranked(frame, scores):
    out = frame[["driver_id"]].copy()
    scores = np.asarray(scores, dtype=float)
    if len(scores) != len(out) or not np.isfinite(scores).all():
        raise DataContractError("Prediction scores must be finite and match the entry list.")
    out["score"] = scores
    out = out.sort_values(["score", "driver_id"], kind="stable").reset_index(drop=True)
    out["predicted_position"] = np.arange(1, len(out) + 1)
    validate_ranking(out, frame.driver_id)
    return out


def assess(frame, model=None):
    records, metrics = [], []
    for event_id, group in frame.groupby("event_id", sort=True):
        scores = group.qualifying_position if model is None else model.predict(group[FEATURES])
        prediction = ranked(group, scores).merge(
            group[["driver_id", "actual_position"]], on="driver_id", validate="one_to_one")
        prediction["event_id"] = event_id
        prediction["absolute_error"] = (prediction.predicted_position - prediction.actual_position).abs()
        records.append(prediction)
        k = min(3, len(prediction))
        top = set(prediction.loc[prediction.predicted_position <= k, "driver_id"])
        actual_top = set(prediction.loc[prediction.actual_position <= k, "driver_id"])
        metrics.append({"event_id": event_id,
                        "position_mae": float(prediction.absolute_error.mean()),
                        "spearman": float(prediction.predicted_position.corr(prediction.actual_position, method="spearman")),
                        "top3_overlap": len(top & actual_top) / k})
    detail = pd.DataFrame(metrics)
    summary = {col: float(detail[col].mean()) for col in ("position_mae", "spearman", "top3_overlap")}
    summary.update(events=len(detail), driver_rows=len(frame))
    return summary, pd.concat(records, ignore_index=True), detail


def benchmark(history_folder, train_end=2023, valid_year=2024, test_year=2025, root=None):
    if not train_end < valid_year < test_year:
        raise DataContractError("Training, validation and test seasons must be strictly chronological.")
    results, qualifying, provenance = load_history(history_folder)
    frame, excluded = training_table(results, qualifying)
    train = frame.loc[frame.season <= train_end]
    valid = frame.loc[frame.season.eq(valid_year)]
    test = frame.loc[frame.season.eq(test_year)]
    if any(part.empty for part in (train, valid, test)):
        raise DataContractError("Each chronological split must contain data.")
    candidates = {
        "ridge_10": pipeline(Ridge(alpha=10)),
        "ridge_100": pipeline(Ridge(alpha=100)),
        "hist_gradient_boosting": pipeline(HistGradientBoostingRegressor(
            max_iter=150, learning_rate=0.05, max_leaf_nodes=7,
            l2_regularization=10, early_stopping=False, random_state=42)),
    }
    validation = {}
    for name, model in candidates.items():
        model.fit(train[FEATURES], train.target)
        validation[name] = assess(valid, model)[0]
    selected = min(validation, key=lambda name: (validation[name]["position_mae"], name))
    final_model = clone(candidates[selected])
    development = pd.concat([train, valid])
    final_model.fit(development[FEATURES], development.target)
    model_metrics, predictions, event_metrics = assess(test, final_model)
    baseline_metrics, baseline_predictions, baseline_events = assess(test)
    paired = event_metrics.set_index("event_id").position_mae - baseline_events.set_index("event_id").position_mae
    rng = np.random.default_rng(42)
    samples = rng.choice(paired.to_numpy(), size=(2000, len(paired)), replace=True).mean(axis=1)
    report = {
        "status": "first draft; under active development", "mode": "reconstructed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": provenance["source"], "source_observed_at": provenance["observed_at"],
        "history_manifest_sha256": sha256((Path(history_folder) / "manifest.json").read_bytes()).hexdigest(),
        "splits": {"train_through": train_end, "validation": valid_year, "test": test_year,
                   "train_events": train.event_id.nunique(), "valid_events": valid.event_id.nunique()},
        "selected_model": selected, "validation": validation,
        "validation_qualifying_baseline": assess(valid)[0],
        "test_model": model_metrics, "test_qualifying_baseline": baseline_metrics,
        "paired_mae_difference_model_minus_baseline": float(paired.mean()),
        "paired_bootstrap_95_interval": np.quantile(samples, [0.025, 0.975]).tolist(),
        "excluded_events": excluded,
        "limitations": [
            "Historical classifications downloaded now may include later corrections.",
            "Final-classification target includes retirements and disqualifications.",
            "Q/R roster mismatches are excluded, not silently repaired.",
            "Model frozen before test season; rolling form updates after each previous race.",
            "Circuit identity and past circuit performance are used; geometry and degradation are not.",
            "No weather forecasts, news or grid penalties in the trained benchmark.",
            "Event bootstrap interval is descriptive; successive races are not independent.",
            "A learned score is not a calibrated finishing-position probability.",
        ],
    }
    root = prepare_dirs(root)
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    folder = root / "reports/benchmarks" / token
    folder.mkdir(parents=True)
    predictions.to_csv(folder / "test_predictions.csv", index=False)
    baseline_predictions.to_csv(folder / "baseline_predictions.csv", index=False)
    event_metrics.to_csv(folder / "event_metrics.csv", index=False)
    joblib.dump(final_model, folder / "model.joblib")
    import sklearn
    metadata = {
        "schema_version": 1, "model_name": selected,
        "trained_through_utc": pd.Timestamp(development.start_utc.max()).isoformat(),
        "feature_columns": FEATURES, "sklearn_version": sklearn.__version__,
        "model_sha256": sha256((folder / "model.joblib").read_bytes()).hexdigest(),
        "history_manifest_sha256": report["history_manifest_sha256"],
    }
    for name, payload in (("benchmark.json", report), ("model.json", metadata)):
        (folder / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return folder, report


def predict_race(model_folder, results, qualifying):
    """Load only a model produced locally by this project; joblib is not a safe interchange format."""
    folder = Path(model_folder)
    metadata = json.loads((folder / "model.json").read_text(encoding="utf-8"))
    if metadata.get("schema_version") != 1 or metadata.get("feature_columns") != FEATURES:
        raise DataContractError("Unsupported model feature schema.")
    if sha256((folder / "model.joblib").read_bytes()).hexdigest() != metadata["model_sha256"]:
        raise DataContractError("Model checksum failed.")
    if utc_timestamp(metadata["trained_through_utc"]) >= utc_timestamp(qualifying.iloc[0].start_utc):
        raise DataContractError("The model was trained on this event or later events.")
    features = race_features(results, qualifying)
    model = joblib.load(folder / "model.joblib")
    prediction = ranked(features, model.predict(features[FEATURES]))
    return prediction, features, metadata
