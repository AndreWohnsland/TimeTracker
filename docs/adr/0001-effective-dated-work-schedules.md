# 1. Effective-dated work schedules in the database

Date: 2026-08-27

## Status

Accepted

## Context

All derived numbers (target time, overtime) are recomputed from raw facts in
the SQLite database. The work schedule (weekly/daily hours, workdays, per-day
hours) lived as current-only values in the JSON config file, so changing it
silently recomputed *all* history with the new values — changing Friday from
6h to 8h rewrote every past Friday's overtime (issue #56).

Alternatives considered:

- **Snapshot/freeze computed overtime** at the moment of a settings change.
  Rejected: breaks the recompute-from-raw model the moment past raw data is
  edited, and the frozen number can never be corrected.
- **Keep current values in the JSON config, past periods in the DB.**
  Rejected: two sources of truth that must be updated atomically; drift is
  guaranteed once a config file is hand-edited or restored from a backup next
  to a newer database.

## Decision

The work schedule becomes a dated fact in the database: a `WorkSchedule` table
with one row per change and a unique `ValidFrom` date. The schedule for day
*d* is the row with the greatest `ValidFrom <= d`; there is no `ValidTo` — the
next row implicitly supersedes. A baseline row with `ValidFrom = date.min` is
seeded once from the legacy config values, so resolution can never fail. The
five schedule fields are removed from the JSON config entirely; the DB is the
single source of truth. Changing time settings in the config window inserts a
row effective today (same-day changes collapse into one row); effective dates
are adjusted in a dedicated management window.

## Consequences

- Past target time and overtime stay stable across settings changes; editing
  raw past data still recomputes correctly under the schedule of that time.
- Whether a holiday counts as a free day now depends on the workdays of the
  schedule effective on that date, not the current one.
- Copying only the JSON config file to another machine no longer carries the
  work schedule; it travels with the database.
- The baseline row must always exist: it can be edited but not deleted.
