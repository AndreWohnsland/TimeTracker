# Project time is derived, never stored

Events carry the project they were booked on, but no project-level state is
materialized anywhere: starting a project while another is running writes
*no* implicit stop event — the switch boundary is derived during calculation
(a start ends any open interval). Likewise the month DataFrame keeps its
day-per-row grain with no project column; per-project hours are a separate
day×project frame computed on demand from the raw events.

## Considered Options

- **Materialize an implicit stop event on project switch** — rejected: data
  mutation magic, misclicks leave extra events to clean up, past-time entries
  get ambiguous. Deriving matches how overtime is already handled (recomputed
  from raw facts, never stored).
- **Add a project column to the month DataFrame** — rejected: it mixes two
  grains. Only work time is a day×project fact; pause, break, target and
  overtime are day-level and would be duplicated across project rows, forcing
  a groupby/dedup into every consumer (plots, table, year resample, overtime
  totals, exporter) or silently double-counting.

## Consequences

- The Project Switch rule must live in exactly one interval-resolution
  function shared by the total and the per-project calculation, or the two
  will drift.
- Per-project data has no cache; it is recomputed per window interaction
  (trivial at this data size).
