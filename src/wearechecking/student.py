"""Completed reference implementations retained for the learning notebooks."""
import pandas as pd
from .contracts import require_columns, validate_ranking


def lap_counts(laps):
    """Count distinct positive lap numbers; missing lap times are still laps."""
    require_columns(laps, ["DriverNumber", "LapNumber"], "Laps")
    frame = laps[["DriverNumber", "LapNumber"]].copy()
    frame["LapNumber"] = pd.to_numeric(frame.LapNumber, errors="coerce")
    frame = frame.loc[frame.DriverNumber.notna() & (frame.LapNumber > 0)]
    frame["DriverNumber"] = frame.DriverNumber.astype(str)
    return (frame.drop_duplicates().groupby("DriverNumber").size()
            .rename("lap_count").rename_axis("driver_number").reset_index())


def qualifying_baseline(features):
    """Preserve qualifying order as an explicit race benchmark."""
    require_columns(features, ["driver_id", "qualifying_position"], "Qualifying inputs")
    prediction = features[["driver_id", "qualifying_position"]].rename(
        columns={"qualifying_position": "predicted_position"}).copy()
    validate_ranking(prediction, features.driver_id)
    return prediction.sort_values("predicted_position").reset_index(drop=True)
