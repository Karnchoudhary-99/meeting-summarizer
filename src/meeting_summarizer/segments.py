"""Topic segmentation: split a transcript into coherent topic blocks.

A lightweight TextTiling-style approach: for each gap between turns,
compare the vocabulary of a small window of turns on either side. A gap
with low word overlap, with enough turns on both sides, marks a topic
boundary. With no clear boundary the whole meeting is one segment.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .transcript import SpeakerTurn

_WORD_RE = re.compile(r"[a-z0-9']+")

_STOPWORDS = frozenset(
    """
    a an the and or but if then else when while of to in on at for with by
    from is are was were be been being have has had do does did will would
    can could should shall may might must i you he she it we they this that
    these those there here what who whom which how why when where not no yes
    so very just really quite also only even still already yet more most
    other others some any all each every both into over under about up down
    out off as per via ok okay hi hello thanks thank please well now today
    """.split()
)


def content_words(text: str) -> set[str]:
    """Lowercased word set with stopwords removed."""
    return {w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS}


def _cosine(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    shared = len(left & right)
    return shared / math.sqrt(len(left) * len(right))


@dataclass
class Segment:
    """A run of consecutive turns about one topic."""

    index: int
    turns: list[SpeakerTurn]

    def text(self) -> str:
        return " ".join(t.text for t in self.turns)

    @property
    def speakers(self) -> list[str]:
        seen: list[str] = []
        for turn in self.turns:
            if turn.speaker not in seen:
                seen.append(turn.speaker)
        return seen


def segment_transcript(
    turns: list[SpeakerTurn],
    window: int = 2,
    threshold: float = 0.12,
    min_turns: int = 2,
) -> list[Segment]:
    """Split turns into topic segments.

    ``window`` turns on each side of a gap are compared; gaps scoring
    below ``threshold`` become boundaries, provided each side keeps at
    least ``min_turns`` turns (boundaries too close to the edges are
    skipped). Segments are returned in order.
    """
    if not turns:
        return []
    word_sets = [content_words(t.text) for t in turns]
    boundaries = [0]
    for gap in range(1, len(turns)):
        if gap < min_turns or len(turns) - gap < min_turns:
            continue
        left: set[str] = set()
        for ws in word_sets[max(0, gap - window) : gap]:
            left |= ws
        right: set[str] = set()
        for ws in word_sets[gap : gap + window]:
            right |= ws
        if _cosine(left, right) < threshold:
            boundaries.append(gap)
    boundaries.append(len(turns))
    return [
        Segment(index=i, turns=turns[boundaries[i] : boundaries[i + 1]])
        for i in range(len(boundaries) - 1)
    ]
