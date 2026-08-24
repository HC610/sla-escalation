# sla-escalation

Escalates support tickets that missed the 5-day (120 hour) first-response SLA.

See [SPEC.md](SPEC.md) for the full spec.

## How it works

A ticket is escalated if all of the following are true:

- `status` is `"open"`
- `first_response_at` is `null`
- `created_at` is 120+ hours before the current time

Escalating a ticket sets `escalated` to `true`, sets `escalated_at` to the
current time, and appends a line to the log file in the form:

```
<timestamp>,<ticket_id>,<hours_overdue>
```

Already-escalated tickets are left untouched — running the check repeatedly
is safe and won't create duplicate log entries or re-escalate anything.

## Ticket format

Tickets are read from and written back to a local JSON file (see
`schema/ticket.schema.json` and `fixtures/tickets.json` for the shape and
example data):

```json
{
  "id": "T-1001",
  "status": "open",
  "created_at": "2026-08-17T12:00:00Z",
  "first_response_at": null,
  "escalated": false,
  "escalated_at": null
}
```

## Usage

Run against a tickets file (defaults to `tickets.json` and `escalations.log`
in the current directory):

```bash
python3 -m sla_escalation.cli
```

Or point it at specific files:

```bash
python3 -m sla_escalation.cli --tickets path/to/tickets.json --log path/to/escalations.log
```

Any newly escalated tickets are printed to stdout as they're logged.
Tickets with a missing or invalid `created_at` are skipped with an error
printed to stderr, rather than aborting the run.

## Tests

```bash
python3 -m pytest tests/
```
