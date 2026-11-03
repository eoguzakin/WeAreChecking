"""Feedback helpers. A pending exercise never counts as completed."""
import pandas as pd
from .contracts import DataContractError, require_columns, validate_ranking


def check_lap_counts(answer, laps):
    if answer is None:
        return "BEKLİYOR: student.lap_counts fonksiyonunu birlikte yazacağız."
    require_columns(answer, ["driver_number", "lap_count"], "Alıştırma 1")
    if answer.driver_number.duplicated().any() or answer.driver_number.isna().any():
        raise DataContractError("Her sürücü numarası yalnız bir kez bulunmalı.")
    valid = laps.loc[laps.DriverNumber.notna() & (pd.to_numeric(laps.LapNumber, errors="coerce") > 0)]
    expected = valid.drop_duplicates(["DriverNumber", "LapNumber"]).groupby("DriverNumber").size()
    actual = answer.set_index("driver_number")["lap_count"].sort_index()
    expected.index = expected.index.astype(str)
    actual.index = actual.index.astype(str)
    pd.testing.assert_series_equal(actual.sort_index(), expected.sort_index(),
                                   check_dtype=False, check_names=False)
    return "TAMAM: tur sayıları eşleşiyor. Şimdi bu sayının hız ölçüsü olmadığını açıkla."


def check_baseline(answer, features):
    if answer is None:
        return "BEKLİYOR: student.qualifying_baseline fonksiyonunu birlikte yazacağız."
    validate_ranking(answer, features.driver_id)
    joined = answer.merge(features[["driver_id", "qualifying_position"]],
                          on="driver_id", validate="one_to_one")
    if not joined.predicted_position.eq(joined.qualifying_position).all():
        raise DataContractError("Bu ilk benchmark Q sırasını aynen kullanmalı.")
    return "TAMAM: ilk sıralama üretildi. Şimdi kaydedip yarış sonucuyla karşılaştırabilirsin."
