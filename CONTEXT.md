# Ubiquitous Language

## Project

A user-defined label a Work Interval is booked on (a ticket, task, or client
— the user decides the granularity). Projects are configured as a plain name
list; every start/stop event carries the project selected at booking time.
The terms "reason", "ticket", and "time type" are superseded by Project.
"Reason" remains in use only for Time Off (vacation vs. sick etc.).

## Project Switch

Starting work on one project while an interval on another project is open.
The open interval ends at the moment of the new start (see Work Interval).

## Work Interval

The span between a start event and the event that ends it. An interval is
ended by the next stop event — or implicitly by the next start event (a
Project Switch). This boundary is derived during calculation; no stop event
is ever written on the user's behalf. A repeated start on the same project
does not end the interval.

## Booked Time

The raw duration of a project's Work Intervals, with nothing deducted.
Distinct from work time: a Pause belongs to a day, not to a project, so it
reduces the day's work time but never a project's Booked Time.

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
