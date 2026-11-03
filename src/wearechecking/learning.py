"""Feedback helpers. A pending exercise never counts as completed."""
import pandas as pd
from .contracts import DataContractError, require_columns, validate_ranking


def check_lap_counts(answer, laps):
    if answer is None:
        return "PENDING: we will implement student.lap_counts together."
    require_columns(answer, ["driver_number", "lap_count"], "Exercise 1")
    if answer.driver_number.duplicated().any() or answer.driver_number.isna().any():
        raise DataContractError("Each driver number must appear exactly once.")
    valid = laps.loc[laps.DriverNumber.notna() & (pd.to_numeric(laps.LapNumber, errors="coerce") > 0)]
    expected = valid.drop_duplicates(["DriverNumber", "LapNumber"]).groupby("DriverNumber").size()
    actual = answer.set_index("driver_number")["lap_count"].sort_index()
    expected.index = expected.index.astype(str)
    actual.index = actual.index.astype(str)
    pd.testing.assert_series_equal(actual.sort_index(), expected.sort_index(),
                                   check_dtype=False, check_names=False)
    return "PASSED: the lap counts match. Now explain why lap count is not a measure of pace."


def check_baseline(answer, features):
    if answer is None:
        return "PENDING: we will implement student.qualifying_baseline together."
    validate_ranking(answer, features.driver_id)
    joined = answer.merge(features[["driver_id", "qualifying_position"]],
                          on="driver_id", validate="one_to_one")
    if not joined.predicted_position.eq(joined.qualifying_position).all():
        raise DataContractError("This first benchmark must preserve the qualifying order.")
    return "PASSED: your first ranking is ready. Save it, then compare it with the race result."
