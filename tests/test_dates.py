from datetime import date

from meeting_summarizer.dates import resolve_due

# 2026-10-23 is a Friday (matches this burst's meeting-week context).
FRIDAY = date(2026, 10, 23)
MONDAY = date(2026, 10, 19)


def test_weekday_on_or_after_reference():
    assert resolve_due("friday", FRIDAY) == FRIDAY
    assert resolve_due("friday", MONDAY) == FRIDAY


def test_next_weekday_is_strictly_after():
    assert resolve_due("next monday", MONDAY) == date(2026, 10, 26)
    assert resolve_due("next friday", FRIDAY) == date(2026, 10, 30)


def test_relative_phrases():
    assert resolve_due("tomorrow", FRIDAY) == date(2026, 10, 24)
    assert resolve_due("end of week", MONDAY) == FRIDAY
    assert resolve_due("end of month", MONDAY) == date(2026, 10, 31)


def test_unknown_phrase_and_none():
    assert resolve_due("sometime soon", MONDAY) is None
    assert resolve_due(None, MONDAY) is None
