import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from sla_escalation.cli import run

FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "tickets.json"
NOW = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)

EXPECTED_LOG_LINES = [
    "2026-08-24T12:00:00Z,T-1001,48.00",
    "2026-08-24T12:00:00Z,T-1003,0.00",
]


def _by_id(tickets):
    return {t["id"]: t for t in tickets}


def test_running_cli_twice_escalates_once_and_is_idempotent(tmp_path):
    tickets_path = tmp_path / "tickets.json"
    log_path = tmp_path / "escalations.log"
    shutil.copy(FIXTURES_PATH, tickets_path)

    first_run_lines = run(tickets_path, log_path, NOW)

    assert first_run_lines == EXPECTED_LOG_LINES
    assert log_path.read_text().splitlines() == EXPECTED_LOG_LINES

    tickets_after_first = _by_id(json.loads(tickets_path.read_text()))
    assert tickets_after_first["T-1001"]["escalated"] is True
    assert tickets_after_first["T-1001"]["escalated_at"] == "2026-08-24T12:00:00Z"
    assert tickets_after_first["T-1003"]["escalated"] is True
    assert tickets_after_first["T-1003"]["escalated_at"] == "2026-08-24T12:00:00Z"
    assert tickets_after_first["T-1002"]["escalated"] is False
    assert tickets_after_first["T-1002"]["escalated_at"] is None
    # already-escalated before the run: untouched, keeps its original escalated_at
    assert tickets_after_first["T-1004"]["escalated"] is True
    assert tickets_after_first["T-1004"]["escalated_at"] == "2026-08-20T12:00:00Z"
    # closed and overdue: must never be escalated regardless of age
    assert tickets_after_first["T-1005"]["escalated"] is False
    assert tickets_after_first["T-1005"]["escalated_at"] is None

    tickets_snapshot = tickets_path.read_text()

    second_run_lines = run(tickets_path, log_path, NOW)

    assert second_run_lines == []
    assert log_path.read_text().splitlines() == EXPECTED_LOG_LINES  # no new lines appended
    assert tickets_path.read_text() == tickets_snapshot  # no changes at all
