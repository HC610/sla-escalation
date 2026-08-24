import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sla_escalation.breach import is_breached

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "tickets.json"
NOW = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)


def load_ticket(ticket_id: str) -> dict:
    tickets = json.loads(FIXTURES_PATH.read_text())
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise KeyError(ticket_id)


def test_breach_clearly_overdue():
    assert is_breached(load_ticket("T-1001"), NOW) is True


def test_no_breach_when_responded_within_sla():
    assert is_breached(load_ticket("T-1002"), NOW) is False


def test_breach_at_exact_120_hour_boundary():
    assert is_breached(load_ticket("T-1003"), NOW) is True


def test_no_breach_when_already_escalated():
    assert is_breached(load_ticket("T-1004"), NOW) is False


def test_no_breach_when_ticket_closed():
    assert is_breached(load_ticket("T-1005"), NOW) is False


def test_breach_raises_on_missing_created_at():
    ticket = {
        "id": "T-9999",
        "status": "open",
        "created_at": None,
        "first_response_at": None,
        "escalated": False,
        "escalated_at": None,
    }
    with pytest.raises(ValueError):
        is_breached(ticket, NOW)
