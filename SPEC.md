# Spec: Escalate Tickets That Miss First-Response SLA

## Why
Support tickets that receive no agent response within the SLA window go unnoticed until a customer complains, damaging trust and violating the SLA commitment. Automatic escalation surfaces these breaches immediately instead of relying on someone to notice manually.

## What
A check that scans all open tickets, identifies any ticket where no first response was sent within 5 calendar days (120 hours) of ticket creation, and escalates each one exactly once by: (1) setting the ticket's `escalated` field to `true`, (2) setting `escalated_at` to the time the check ran, and (3) appending one line to `escalations.log` in the form `<timestamp>,<ticket_id>,<hours_overdue>`. Tickets whose `status` is not `open` are never evaluated for breach or escalation, regardless of age.

## Context
- No existing codebase or ticket system integration exists yet; this is a new, self-contained component.
- A ticket is represented as a record with at least: `id`, `status` (`"open"` or `"closed"`), `created_at` (ISO 8601 timestamp), `first_response_at` (ISO 8601 timestamp or null), `escalated` (bool, default false), `escalated_at` (nullable).
- SLA target: first response must occur within 5 calendar days (120 hours) of `created_at`. Calendar days, not business days — no weekend/holiday exclusion.
- "Missed" means: `status` is `"open"` AND `first_response_at` is null AND current time minus `created_at` is greater than or equal to 120 hours. A ticket that got a late-but-present first response is NOT escalated retroactively — only open tickets still waiting are eligible.

## Constraints
- Escalation must be idempotent: running the check twice must not create duplicate log entries or re-escalate an already-escalated ticket (`escalated == true` tickets are skipped).
- A ticket with `status != "open"` must never be escalated, even if it would otherwise be over 120 hours old with no response.
- The check must not modify any ticket field except `escalated` and `escalated_at`.
- No network calls — tickets are read from and written back to a local JSON file (`tickets.json`).
- Time comparisons use UTC; ambiguous or missing `created_at` values cause that ticket to be skipped and logged as an error, not silently dropped or crashed on.

## Tasks
1. Define the ticket schema and a fixture file (`fixtures/tickets.json`) with real example tickets: one clearly breaching (created 6+ days ago, no response), one clearly compliant (responded within 5 days), one exactly at the 120-hour boundary, one already escalated. Commit.
2. Implement `is_breached(ticket, now)` — pure function, unit-tested against each fixture case with real timestamp values, including the boundary case. Commit.
3. Implement `escalate(ticket, now)` — mutates `escalated`/`escalated_at`, returns a log line; unit-tested for idempotency (calling twice on an already-escalated ticket is a no-op). Commit.
4. Implement the CLI entry point that loads `tickets.json`, applies `is_breached` + `escalate` to each ticket, writes updated `tickets.json`, and appends to `escalations.log`. Commit.
5. Add an end-to-end test that runs the CLI twice against the fixture file and asserts: exactly the breaching and boundary tickets are escalated, the log has exactly those entries, and the second run produces no new log entries or changes. Commit.
6. Add a `status` field to the ticket schema (defaulting existing fixtures to `"open"`, plus one new fixture ticket that is `"closed"`, unresponded, and past 120 hours old) and update `is_breached` to return `false` for any ticket where `status != "open"`, with a unit test covering the closed-but-overdue fixture ticket and an end-to-end test asserting it's never escalated. Schema/fixture data and the filtering logic land together so the commit is never red. Commit.
7. Add a `README.md` documenting the escalation rule, the ticket JSON format, CLI usage (`python3 -m sla_escalation.cli [--tickets PATH] [--log PATH]`), and how to run the tests. Verify the documented commands actually work before committing. Commit.

## Done
- Running the CLI against `fixtures/tickets.json` escalates exactly the open tickets with no first response at 120+ hours old, and no others — closed tickets are never escalated regardless of age.
- Running it a second time changes nothing (no duplicate log lines, no re-escalation).
- Every task above is committed individually, each with passing tests at that commit, and this spec was committed before any implementation code.
