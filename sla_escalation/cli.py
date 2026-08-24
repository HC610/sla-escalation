import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from sla_escalation.breach import is_breached
from sla_escalation.escalate import escalate


def run(tickets_path: Path, log_path: Path, now: datetime | None = None) -> list[str]:
    """Load tickets from `tickets_path`, escalate any that miss the
    first-response SLA, write the updated tickets back, and append any new
    escalation log lines to `log_path`.

    Tickets with a missing/invalid `created_at` are skipped with an error
    printed to stderr, rather than aborting the whole run.

    Returns the list of log lines appended (empty if none).
    """
    if now is None:
        now = datetime.now(timezone.utc)

    tickets = json.loads(Path(tickets_path).read_text())

    log_lines = []
    for ticket in tickets:
        try:
            breached = is_breached(ticket, now)
        except ValueError as exc:
            print(f"error: skipping ticket {ticket.get('id')!r}: {exc}", file=sys.stderr)
            continue

        if breached:
            log_line = escalate(ticket, now)
            if log_line is not None:
                log_lines.append(log_line)

    Path(tickets_path).write_text(json.dumps(tickets, indent=2) + "\n")

    if log_lines:
        with open(log_path, "a") as f:
            for line in log_lines:
                f.write(line + "\n")

    return log_lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Escalate tickets that missed the first-response SLA."
    )
    parser.add_argument(
        "--tickets", default="tickets.json", help="Path to the tickets JSON file (default: tickets.json)"
    )
    parser.add_argument(
        "--log", default="escalations.log", help="Path to the escalation log file (default: escalations.log)"
    )
    args = parser.parse_args(argv)

    log_lines = run(Path(args.tickets), Path(args.log))
    for line in log_lines:
        print(line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
