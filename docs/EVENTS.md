# Driver events and session updates

The first draft consumes a **manually reviewed JSON event ledger**. It does not crawl news or automatically trust headlines. The empty examples/events.json is a valid input.

Each record requires event_id, kind, driver_id, effective_at, published_at, observed_at, source_url and confirmed. All timestamps need a timezone. An unconfirmed record or a record observed after the forecast cutoff has no effect.

## Supported behavior

| Kind | Effect |
| --- | --- |
| substitution | Replace the entry with a distinct permanent driver identity; optional session limits scope |
| withdrawal | Remove that driver from applicable upcoming sessions |
| injury | Annotate the forecast; no invented numerical pace penalty |
| disqualification | When scoped to a completed session, exclude that driver's observation from that session; do not ban future participation |

An injury should become a withdrawal only after a source explicitly confirms non-participation. A disqualification from qualifying is not automatically a race withdrawal.

### Schema example — synthetic drivers only

```json
[
  {
    "event_id": "synthetic-replacement-01",
    "kind": "substitution",
    "driver_id": "example_driver",
    "effective_at": "2024-06-28T08:00:00Z",
    "published_at": "2024-06-28T07:00:00Z",
    "observed_at": "2024-06-28T07:05:00Z",
    "source_url": "https://example.com/synthetic-announcement",
    "confirmed": true,
    "replacement": {
      "driver_id": "example_reserve",
      "driver": "RSV",
      "driver_number": "40"
    }
  }
]
```

This example is not real news and does not belong in the real Bahrain roster. Replace it with verified facts and the correct identities before running a real scenario. The replacement inherits the constructor fields unless explicitly supplied, but never the original driver's history.

Add `"session": "S"` to scope an entry change to the sprint. Omit session for a change affecting all applicable future sessions. Disqualification records need a session code to filter that session's observations.

## Entry files

Entry JSON contains mode = reconstructed, year, round, circuit_id, available_at, provenance and entries. Each entry has driver_id, driver, driver_number, team_id and team.

The supplied Bahrain and Austria files are real retrospective rosters derived from Jolpica qualifying. Their available_at values are declared replay assumptions. They support software demonstrations, not point-in-time roster backtests.

## Update workflow

1. Download a new weekend snapshot when more data are available.
2. Update reviewed event records without backdating observed_at.
3. Run forecast with the new cutoff and that weekend's entry file.
4. Compare the separately saved JSON/HTML versions.

The command is manually invoked. An unattended scheduler, news ingestion, source conflict resolution, forecast weather and alerts remain planned. Historical snapshots cannot be advertised as live predictions.
