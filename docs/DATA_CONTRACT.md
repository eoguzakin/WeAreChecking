# Data contract v1

- **Weekend:** season and official round, with circuit/location and the source meeting_key.
- **Session:** source session_key, type, UTC schedule, and an event-time end bound.
- **Entry:** session-specific DriverNumber and source name; Jolpica DriverId for Q/R/S. Do not assign an FP participant an identity from the race roster automatically.
- **Lap:** one driver's lap record. Missing, duplicate, and pit-out records are possible. Missing LapTime is not zero.
- **Weather:** observed weather, not a pre-race weather forecast.
- **Snapshot:** schema_version, observed_at, source URLs, raw JSON, normalized Parquet, and SHA-256 hashes. A failed download has status=failed.
- **Forecast:** source snapshot ID, target_session, cutoff_utc, mode, model version, and prediction CSV hash.
- **Label:** R/results, read only when evaluating a saved prediction.

## What the timestamps mean

`cutoff_utc` is the time at which we assume the prediction is made.
`observed_at` records when we actually obtain the data.
`event_end_bound_utc` is the later of the source's session end and the last measured lap end. It is not a publication timestamp.

The initial experiment supports reconstructed mode only. The cutoff must be after qualifying ends and before the race starts. These sources cannot fully eliminate leakage from later qualifying-classification corrections. We do not claim live or historical point-in-time validity.

## Snapshot coverage

`status=complete` means that the requested sessions were downloaded. `requested_sessions` defines that scope: downloading only Q does not constitute a full weekend. Notebook 01 separately checks that all scheduled sessions are present.

## Forecast v0

The input allowlist is: driver_id, driver, team, qualifying_position.
Qualifying participants are provisional race entries. Evaluation raises an error if entries differ or a classification is incomplete; it does not automatically assign missing drivers last place.
