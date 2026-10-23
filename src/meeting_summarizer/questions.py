"""Open-question extraction: questions the meeting leaves unanswered.

A sentence counts as a question if it ends with "?" or states an
undecided point ("we still need to decide", "open question", "to be
decided"). A question is dropped as answered when a later turn shares
at least two content words with it — e.g. "What is the launch date?"
followed by "The launch date is Friday." — so the report lists only
questions the transcript never resolves.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .segments import content_words

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+(?:\s+|$)")
_UNDECIDED_RE = re.compile(
    r"\b(?:open question|still need to decide|need to decide|to be decided"
    r"|unresolved|not yet decided)\b",
    re.IGNORECASE,
)


@dataclass
class OpenQuestion:
    """A question with no resolving answer later in the transcript."""

    text: str
    speaker: str = "Unknown"

    def to_dict(self) -> dict:
        return {"text": self.text, "speaker": self.speaker}


def _is_question(sentence: str) -> bool:
    return sentence.strip().endswith("?") or bool(_UNDECIDED_RE.search(sentence))


def extract_open_questions(transcript) -> list[OpenQuestion]:
    """Extract open questions, in meeting order."""
    # Content words of every later turn, for the answered-check.
    later_words: list[set[str]] = []
    sentences: list[tuple[str, str, int]] = []  # (text, speaker, turn idx)
    for idx, turn in enumerate(transcript.turns):
        later_words.append(content_words(turn.text))
        for sentence in _SENTENCE_RE.findall(turn.text):
            sentence = sentence.strip()
            if sentence and _is_question(sentence):
                sentences.append((sentence, turn.speaker, idx))
    open_questions: list[OpenQuestion] = []
    for text, speaker, idx in sentences:
        words = content_words(text)
        answered = any(
            len(words & later) >= 2 for later in later_words[idx + 1 :]
        )
        if not answered:
            open_questions.append(OpenQuestion(text=text, speaker=speaker))
    return open_questions
