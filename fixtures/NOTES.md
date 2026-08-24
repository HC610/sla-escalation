# Fixture notes

All expected outcomes below are computed against a fixed reference time of
`now = 2026-08-24T12:00:00Z`. Tests must use this exact value as `now` when
evaluating this fixture — do not use the live clock.

| id     | status | age at `now`          | first_response_at   | escalated (in) | expected: is_breached | expected: escalated (out) |
|--------|--------|-------------------------|----------------------|-----------------|------------------------|-----------------------------|
| T-1001 | open   | 168h (7 days)          | null                 | false           | true                   | true                        |
| T-1002 | open   | 96h (4 days), responded at 22h | 2026-08-21T10:00:00Z | false | false                   | false                       |
| T-1003 | open   | 120h (5 days) exactly  | null                 | false           | true (boundary, >=120h) | true                        |
| T-1004 | open   | 216h (9 days)          | null                 | true            | false (already escalated, must be skipped) | true (unchanged) |
| T-1005 | closed | 336h (14 days)         | null                 | false           | false (closed, must never be escalated regardless of age) | false |
