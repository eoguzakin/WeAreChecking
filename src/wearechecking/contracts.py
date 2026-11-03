"""Small, explicit contracts: friendly failures before pandas KeyErrors."""
import pandas as pd


class DataContractError(ValueError):
    pass


def require_columns(frame, columns, name):
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise DataContractError(
            f"{name}: eksik kolonlar {missing}. Mevcut kolonlar: {list(frame.columns)}"
        )
    if frame.empty:
        raise DataContractError(f"{name}: tablo boş.")


def utc_timestamp(value):
    stamp = pd.Timestamp(value)
    if pd.isna(stamp) or stamp.tzinfo is None:
        raise DataContractError("Saat dilimi gerekli; örnek: 2024-03-02T12:00:00Z.")
    return stamp.tz_convert("UTC")


def validate_ranking(prediction, driver_ids):
    require_columns(prediction, ["driver_id", "predicted_position"], "Tahmin")
    if prediction.driver_id.isna().any() or prediction.driver_id.duplicated().any():
        raise DataContractError("Her sürücü için tam bir tahmin satırı gerekli.")
    if set(prediction.driver_id) != set(driver_ids):
        raise DataContractError("Tahmin edilen sürücüler ile girdi sürücüleri eşleşmiyor.")
    positions = pd.to_numeric(prediction.predicted_position, errors="coerce")
    if sorted(positions.tolist()) != list(range(1, len(prediction) + 1)):
        raise DataContractError("Tahmin sırası 1..N olmalı; boşluk veya tekrar olamaz.")
