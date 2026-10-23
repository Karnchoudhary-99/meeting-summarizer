"""Extractive summarization: pick the sentences that carry the meeting.

Scoring (no model, no API): a sentence scores by the frequency of its
content words across the whole transcript, with a bonus for the opening
sentence of each topic segment and a penalty for very short fragments. Selection
guarantees at least one sentence per topic segment (when the budget
allows), then fills the remaining slots by global score, so every topic
is represented and the output keeps the meeting's original order.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .segments import Segment, content_words, segment_transcript
from .transcript import Transcript

_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+(?:\s+|$)")


@dataclass
class ScoredSentence:
    """A sentence plus where it came from, for traceable summaries."""

    text: str
    speaker: str
    segment_index: int
    score: float


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, keeping trailing punctuation."""
    return [m.group(0).strip() for m in _SENTENCE_RE.finditer(text) if m.group(0).strip()]


def _score_sentences(segments: list[Segment]) -> list[ScoredSentence]:
    sentences: list[ScoredSentence] = []
    for segment in segments:
        for turn in segment.turns:
            for sentence in split_sentences(turn.text):
                sentences.append(
                    ScoredSentence(
                        text=sentence,
                        speaker=turn.speaker,
                        segment_index=segment.index,
                        score=0.0,
                    )
                )
    frequencies = Counter()
    for sentence in sentences:
        frequencies.update(content_words(sentence.text))
    if not frequencies:
        return sentences
    peak = max(frequencies.values())
    # Frequency score + opening-sentence bonus, short-fragment penalty.
    scored: list[ScoredSentence] = []
    per_segment_position: dict[int, int] = {}
    for sentence in sentences:
        words = content_words(sentence.text)
        freq_score = sum(frequencies[w] for w in words) / peak if words else 0.0
        pos_in_segment = per_segment_position.get(sentence.segment_index, 0)
        per_segment_position[sentence.segment_index] = pos_in_segment + 1
        score = freq_score
        if pos_in_segment == 0:
            score += 0.5
        if len(words) < 3:
            score *= 0.5
        scored.append(
            ScoredSentence(
                text=sentence.text,
                speaker=sentence.speaker,
                segment_index=sentence.segment_index,
                score=score,
            )
        )
    return scored


@dataclass
class Summary:
    """An extractive summary: chosen sentences in meeting order."""

    sentences: list[ScoredSentence]
    segment_count: int

    def text(self) -> str:
        return " ".join(s.text for s in self.sentences)

    def to_dict(self) -> dict:
        return {
            "segment_count": self.segment_count,
            "sentences": [
                {
                    "text": s.text,
                    "speaker": s.speaker,
                    "segment": s.segment_index,
                    "score": round(s.score, 3),
                }
                for s in self.sentences
            ],
        }


def summarize(transcript: Transcript, max_sentences: int = 5) -> Summary:
    """Summarize a transcript into at most ``max_sentences`` sentences."""
    segments = segment_transcript(transcript.turns)
    scored = _score_sentences(segments)
    if not scored or max_sentences <= 0:
        return Summary(sentences=[], segment_count=len(segments))
    ranked = sorted(scored, key=lambda s: s.score, reverse=True)
    chosen: list[ScoredSentence] = []
    # One sentence per segment first, so every topic is represented.
    seen_segments: set[int] = set()
    for sentence in ranked:
        if len(chosen) >= max_sentences:
            break
        if sentence.segment_index not in seen_segments:
            chosen.append(sentence)
            seen_segments.add(sentence.segment_index)
    for sentence in ranked:
        if len(chosen) >= max_sentences:
            break
        if sentence not in chosen:
            chosen.append(sentence)
    # Restore meeting order.
    order = {id(s): i for i, s in enumerate(scored)}
    chosen.sort(key=lambda s: order[id(s)])
    return Summary(sentences=chosen, segment_count=len(segments))
