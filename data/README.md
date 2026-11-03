# Data

Real data is versioned under `snapshots/` and excluded from Git.

- OpenF1: participants, laps, stints, and observed weather, saved as source JSON and normalized Parquet.
- Jolpica: qualifying/sprint/race classifications and permanent driver IDs.
- FastF1: the weekend calendar; the F1TV timing API is not used.

Each snapshot records source URLs, UTC observation times, coverage, and SHA-256 hashes. A new fetch creates a new folder; existing snapshots remain unchanged. Interrupted downloads retain a `failed` status. HTTP and calendar caches live in `.cache/` at the project root. Cached data is also labelled as a historical reconstruction, not evidence of publication-time availability.
