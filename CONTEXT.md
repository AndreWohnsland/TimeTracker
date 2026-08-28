# Ubiquitous Language

## Work Schedule

The set of settings that determines how much work is expected on a given day:
weekly/daily work hours, the switch between weekly and daily interpretation,
which weekdays are workdays, and optional per-day hours. A Work Schedule is
effective from a date onward; a newer schedule supersedes it from its own
effective date. The newest schedule is the *current* one. User-facing label:
"time settings".

Not part of the Work Schedule: holiday region (country/subdiv), projects,
name, save path — those remain current-only configuration.

## Effective Date

The first day a Work Schedule applies. Target time and overtime for a day are
always calculated against the schedule effective on that day, never against
the current one.

## Target Time

Hours a user is expected to work on a specific day, derived from the Work
Schedule effective on that day (zero on non-workdays and future days).

## Overtime

Worked hours minus Target Time for a day. Total overtime is recomputed from
raw facts (events, pauses, time off, adjustments, schedules); it is never
stored.
