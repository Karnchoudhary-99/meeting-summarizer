"""Decision extraction: sentences where the meeting settles something.

A decision is a sentence carrying an agreement marker — "agreed",
"decided", "approved", "confirmed", "let's go with", "we will go with"
— as opposed to a mere statement of fact. The sentence itself is kept
verbatim (minus trailing whitespace) so the report can quote it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+(?:\s+|$)")
_DECISION_RE = re.compile(
    r"\b(?:"
    r"agreed|decided|decision\s*:|approved|confirmed"
    r"|let'?s\s+go\s+with|we\s+will\s+go\s+with"
    r"|it\s+was\s+agreed|we\s+agreed|the\s+team\s+agreed"
    r")\b",
    re.IGNORECASE,
)


@dataclass
class Decision:
    """One settled point, quoted from the transcript."""

    text: str
    speaker: str = "Unknown"

    def to_dict(self) -> dict:
        return {"text": self.text, "speaker": self.speaker}


def is_decision_sentence(sentence: str) -> bool:
    return bool(_DECISION_RE.search(sentence))


def extract_decisions(transcript) -> list[Decision]:
    """Extract decision sentences from every turn, in meeting order."""
    decisions: list[Decision] = []
    for turn in transcript.turns:
        for sentence in _SENTENCE_RE.findall(turn.text):
            sentence = sentence.strip()
            if sentence and is_decision_sentence(sentence):
                decisions.append(Decision(text=sentence, speaker=turn.speaker))
    return decisions
