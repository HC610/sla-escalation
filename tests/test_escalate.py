import copy
import json
from datetime import datetime, timezone
from pathlib import Path

from sla_escalation.escalate import escalate

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "tickets.json"
NOW = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)


def load_ticket(ticket_id: str) -> dict:
    tickets = json.loads(FIXTURES_PATH.read_text())
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise KeyError(ticket_id)


def test_escalate_sets_fields_and_returns_log_line():
    ticket = load_ticket("T-1001")  # created 168h before NOW
    log_line = escalate(ticket, NOW)

    assert ticket["escalated"] is True
    assert ticket["escalated_at"] == "2026-08-24T12:00:00Z"
    assert log_line == "2026-08-24T12:00:00Z,T-1001,48.00"


def test_escalate_at_exact_boundary_reports_zero_hours_overdue():
    ticket = load_ticket("T-1003")  # created exactly 120h before NOW
    log_line = escalate(ticket, NOW)

    assert log_line == "2026-08-24T12:00:00Z,T-1003,0.00"


def test_escalate_is_idempotent_on_already_escalated_ticket():
    ticket = load_ticket("T-1004")
    before = copy.deepcopy(ticket)

    log_line = escalate(ticket, NOW)

    assert log_line is None
    assert ticket == before  # untouched: no re-stamping of escalated_at


def test_escalate_twice_only_logs_once():
    ticket = load_ticket("T-1001")

    first_log_line = escalate(ticket, NOW)
    second_log_line = escalate(ticket, NOW)

    assert first_log_line is not None
    assert second_log_line is None
    assert ticket["escalated_at"] == "2026-08-24T12:00:00Z"
