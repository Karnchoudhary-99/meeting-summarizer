"""Action-item extraction: who owns what, and by when.

Heuristic, standard-library only — no model, no API. An action item is a
sentence that commits someone to a task: an explicit owner ("Priya will
update the page"), a first-person commitment ("I will send the notes"),
or an assignment ("Assigned to Arjun: fix the flaky test"). Due phrases
("by Friday", "before the launch", "by end of week") are captured as the
raw phrase here; :mod:`meeting_summarizer.dates` resolves them to dates
when a meeting date is known.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
_WEEKDAY_ALT = "|".join(_WEEKDAYS)

# "Assigned to Priya", "assign it to Arjun", "for Sara to draft".
_ASSIGN_RE = re.compile(
    r"\bassign(?:ed|ing)?(?:\s+it)?\s+to\s+([A-Z][a-z]+)\b", re.IGNORECASE
)
_PRONOUNS = frozenset({"We", "You", "He", "She", "They", "It"})
# "Priya will update ...", "Arjun to review ...", "Sara should send ...".
_NAMED_OWNER_RE = re.compile(
    r"\b([A-Z][a-z]+)\s+(?:will|to|should|needs?\s+to|has\s+to)\b"
)
# Due phrases: "by Friday", "before Friday", "by end of week",
# "on Monday", "by tomorrow", "by the end of the month".
_DUE_RE = re.compile(
    r"\b(?:by|before|on)\s+"
    r"((?:next\s+)?(?:" + _WEEKDAY_ALT + r")"
    r"|tomorrow"
    r"|end of (?:the\s+)?(?:week|month)"
    r"|the end of (?:the\s+)?(?:week|month)"
    r"|end of (?:next\s+)?week)\b",
    re.IGNORECASE,
)


@dataclass
class ActionItem:
    """One committed task, with its owner and due phrase if stated."""

    task: str
    owner: str | None = None
    due: str | None = None
    speaker: str = "Unknown"

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "owner": self.owner,
            "due": self.due,
            "speaker": self.speaker,
        }


def extract_owner(sentence: str, speaker: str) -> str | None:
    """Find an action's owner, or None if no owner is named.

    Explicit assignment wins ("assigned to Priya"), then a named subject
    ("Priya will ..."), then a first-person commitment ("I will ...",
    owned by the speaker). A bare "we" commitment has no single owner.
    """
    assigned = _ASSIGN_RE.search(sentence)
    if assigned:
        return assigned.group(1)
    named = _NAMED_OWNER_RE.search(sentence)
    if named and named.group(1) not in _PRONOUNS:
        # A named subject ("Priya will ...") is the owner whether Priya
        # says it herself or someone else assigns it in passing. "We
        # need to ..." names no single owner, so pronouns are skipped.
        return named.group(1)
    if re.search(r"\bI\s+(?:will|need to|should|have to)\b", sentence):
        return speaker
    return None


def extract_due(sentence: str) -> str | None:
    """Return the due phrase ("Friday", "end of week") or None."""
    match = _DUE_RE.search(sentence)
    if not match:
        return None
    phrase = match.group(1).strip().lower()
    # Normalise "the end of the week" -> "end of week".
    phrase = re.sub(r"^the end of (?:the )?", "end of ", phrase)
    return phrase
