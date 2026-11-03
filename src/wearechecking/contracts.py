"""Small, explicit contracts: friendly failures before pandas KeyErrors."""
import pandas as pd


class DataContractError(ValueError):
    pass


def require_columns(frame, columns, name):
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise DataContractError(
            f"{name}: missing columns {missing}. Available columns: {list(frame.columns)}"
        )
    if frame.empty:
        raise DataContractError(f"{name}: the table is empty.")


def utc_timestamp(value):
    stamp = pd.Timestamp(value)
    if pd.isna(stamp) or stamp.tzinfo is None:
        raise DataContractError("A timezone is required; for example: 2024-03-02T12:00:00Z.")
    return stamp.tz_convert("UTC")


def validate_ranking(prediction, driver_ids):
    require_columns(prediction, ["driver_id", "predicted_position"], "Prediction")
    if prediction.driver_id.isna().any() or prediction.driver_id.duplicated().any():
        raise DataContractError("Exactly one prediction row is required for each driver.")
    if set(prediction.driver_id) != set(driver_ids):
        raise DataContractError("Predicted drivers do not match the input drivers.")
    positions = pd.to_numeric(prediction.predicted_position, errors="coerce")
    if sorted(positions.tolist()) != list(range(1, len(prediction) + 1)):
        raise DataContractError("Predicted positions must be 1..N, with no gaps or duplicates.")
