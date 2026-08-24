from datetime import datetime

from sla_escalation.breach import SLA_HOURS, _parse_utc


def escalate(ticket: dict, now: datetime) -> str | None:
    """Mark `ticket` as escalated and return a log line, or None if it was
    already escalated (idempotent no-op — `ticket` is left unchanged).

    Mutates only `escalated` and `escalated_at` on `ticket`.
    """
    if ticket.get("escalated"):
        return None

    created_at = _parse_utc(ticket["created_at"])
    hours_overdue = (now - created_at).total_seconds() / 3600 - SLA_HOURS

    escalated_at = now.isoformat().replace("+00:00", "Z")
    ticket["escalated"] = True
    ticket["escalated_at"] = escalated_at

    return f"{escalated_at},{ticket['id']},{hours_overdue:.2f}"
