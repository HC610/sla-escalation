from datetime import datetime, timedelta, timezone

SLA_HOURS = 120


def _parse_utc(timestamp: str) -> datetime:
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"timestamp {timestamp!r} is missing timezone info")
    return dt.astimezone(timezone.utc)


def is_breached(ticket: dict, now: datetime) -> bool:
    """True if `ticket` has missed the first-response SLA as of `now`.

    Raises ValueError if `created_at` is missing or not a valid ISO 8601
    timestamp with timezone info — callers must treat that as a per-ticket
    error to skip and log, not a reason to fail the whole run.
    """
    if ticket.get("escalated"):
        return False

    if ticket.get("first_response_at"):
        return False

    created_at_raw = ticket.get("created_at")
    if not created_at_raw:
        raise ValueError(f"ticket {ticket.get('id')!r} has no created_at")

    created_at = _parse_utc(created_at_raw)
    age = now - created_at
    return age >= timedelta(hours=SLA_HOURS)
