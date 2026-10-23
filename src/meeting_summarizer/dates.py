"""Due-phrase resolution: turn "by Friday" into a calendar date.

The transcript carries no calendar date (timestamps are seconds since
the meeting started), so resolution needs a reference date — the
meeting date, passed by the caller. Rules, all relative to it:

- a weekday ("friday"): the next occurrence on or after the reference
  date (a Friday meeting due "Friday" is due that day);
- "next <weekday>": the occurrence strictly after the reference date
  (a Monday meeting due "next Monday" is due in seven days);
- "tomorrow": the next day;
- "end of week": the Friday of the reference week (or the next Friday
  if the reference is already past Friday);
- "end of month": the last day of the reference month.

Unknown phrases resolve to None rather than guessing.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def resolve_due(phrase: str | None, reference: date) -> date | None:
    """Resolve a due phrase against ``reference``, or None if unknown."""
    if not phrase:
        return None
    phrase = phrase.strip().lower()
    if phrase == "tomorrow":
        return reference + timedelta(days=1)
    if phrase == "end of week":
        delta = (4 - reference.weekday()) % 7
        return reference + timedelta(days=delta)
    if phrase == "end of month":
        last_day = calendar.monthrange(reference.year, reference.month)[1]
        return date(reference.year, reference.month, last_day)
    match = re.fullmatch(r"(?:next\s+)?([a-z]+)", phrase)
    if not match or match.group(1) not in _WEEKDAYS:
        return None
    target = _WEEKDAYS[match.group(1)]
    if phrase.startswith("next "):
        delta = (target - reference.weekday()) % 7 or 7
    else:
        delta = (target - reference.weekday()) % 7
    return reference + timedelta(days=delta)
