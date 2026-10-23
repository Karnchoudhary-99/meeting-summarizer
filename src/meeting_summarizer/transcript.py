"""Transcript parsing: speaker turns, timestamps, filler cleanup.

Accepted line formats (one turn per line; unlabelled lines continue the
previous turn)::

    [00:12:34] Priya: Let's ship the beta on Friday.
    00:12 Priya: Let's ship the beta on Friday.
    Priya: Let's ship the beta on Friday.
    Let's ship the beta on Friday.          (continuation / unknown speaker)

Timestamps are normalised to seconds since the start of the meeting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Interjections that add no meaning. Matched as whole words only, so
# "humble" is never touched and "like" (a real verb) is left alone.
_FILLERS = ("um", "uh", "erm", "hmm", "mmm", "uh-huh", "mm-hmm")
_FILLER_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(f) for f in _FILLERS) + r")\b[,.]?\s*",
    re.IGNORECASE,
)
_PHRASE_FILLERS = (
    re.compile(r"\byou know[,.]?\s*", re.IGNORECASE),
    re.compile(r"\bi mean[,.]?\s*", re.IGNORECASE),
)
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.!?;:])")
_MULTI_SPACE = re.compile(r"\s+")

_TS_RE = re.compile(
    r"^\s*(?:\[)?(?P<h>\d{1,2}):(?P<m>\d{2})(?::(?P<s>\d{2}))?(?:\])?\s+"
)
_SPEAKER_RE = re.compile(r"^(?P<speaker>[A-Za-z][\w .'-]{0,40}?):\s+(?P<text>.+)$")


@dataclass
class SpeakerTurn:
    """One speaker's uninterrupted contribution."""

    speaker: str
    text: str
    start_seconds: int | None = None

    def __post_init__(self) -> None:
        self.text = clean_text(self.text)


def clean_text(text: str) -> str:
    """Strip filler interjections and normalise whitespace/punctuation."""
    cleaned = _FILLER_RE.sub("", text)
    for pattern in _PHRASE_FILLERS:
        cleaned = pattern.sub("", cleaned)
    cleaned = _SPACE_BEFORE_PUNCT.sub(r"\1", cleaned)
    cleaned = _MULTI_SPACE.sub(" ", cleaned).strip()
    # A leading comma left behind by a removed filler ("um, hello" -> ", hello").
    return cleaned.lstrip(", ").strip()


def _parse_timestamp(token: str) -> int:
    parts = token.strip("[]").split(":")
    if len(parts) == 2:
        hours, minutes, seconds = 0, int(parts[0]), int(parts[1])
    else:
        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
    return hours * 3600 + minutes * 60 + seconds


@dataclass
class Transcript:
    """A parsed meeting transcript."""

    turns: list[SpeakerTurn] = field(default_factory=list)

    @property
    def speakers(self) -> list[str]:
        seen: list[str] = []
        for turn in self.turns:
            if turn.speaker not in seen:
                seen.append(turn.speaker)
        return seen

    @property
    def duration_seconds(self) -> int | None:
        stamps = [t.start_seconds for t in self.turns if t.start_seconds is not None]
        return (max(stamps) - min(stamps)) if stamps else None

    def text(self) -> str:
        """Plain text of the whole meeting, one turn per line."""
        return "\n".join(f"{t.speaker}: {t.text}" for t in self.turns)


def parse_transcript(raw: str) -> Transcript:
    """Parse raw transcript text into speaker turns.

    Blank lines are ignored. A line with no speaker label continues the
    previous turn (or becomes an "Unknown" turn at the start).
    """
    turns: list[SpeakerTurn] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        start: int | None = None
        match = _TS_RE.match(line)
        if match:
            start = _parse_timestamp(match.group(0).strip())
            line = line[match.end():]
        speaker_match = _SPEAKER_RE.match(line)
        if speaker_match:
            turns.append(
                SpeakerTurn(
                    speaker=speaker_match.group("speaker").strip(),
                    text=speaker_match.group("text"),
                    start_seconds=start,
                )
            )
        elif turns:
            turns[-1].text = clean_text(f"{turns[-1].text} {line}")
            if turns[-1].start_seconds is None:
                turns[-1].start_seconds = start
        else:
            turns.append(SpeakerTurn(speaker="Unknown", text=line, start_seconds=start))
    return Transcript(turns)
