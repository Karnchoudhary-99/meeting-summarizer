"""Speaker statistics: who talked, how much, and for how long.

Talk time is estimated from turn timestamps: a turn is assumed to run
until the next turn starts. The final turn has no successor, so it
contributes no time (documented here and in the README) — with no
timestamps at all, time is None and only turn/word counts are reported.
"""

from __future__ import annotations

from dataclasses import dataclass

from .transcript import Transcript


@dataclass
class SpeakerStats:
    """Per-speaker counts for one meeting."""

    speaker: str
    turns: int
    words: int
    speaking_seconds: int | None

    def to_dict(self) -> dict:
        return {
            "speaker": self.speaker,
            "turns": self.turns,
            "words": self.words,
            "speaking_seconds": self.speaking_seconds,
        }


def speaker_stats(transcript: Transcript) -> list[SpeakerStats]:
    """Compute per-speaker stats, in first-appearance order."""
    turns_by_speaker: dict[str, list] = {}
    for turn in transcript.turns:
        turns_by_speaker.setdefault(turn.speaker, []).append(turn)
    # Speaking time: gap to the next turn, where both timestamps exist.
    time_by_speaker: dict[str, int] = {}
    has_any_time = False
    for current, following in zip(transcript.turns, transcript.turns[1:]):
        if current.start_seconds is not None and following.start_seconds is not None:
            gap = following.start_seconds - current.start_seconds
            if gap >= 0:
                time_by_speaker[current.speaker] = (
                    time_by_speaker.get(current.speaker, 0) + gap
                )
                has_any_time = True
    stats: list[SpeakerStats] = []
    for speaker, turns in turns_by_speaker.items():
        stats.append(
            SpeakerStats(
                speaker=speaker,
                turns=len(turns),
                words=sum(len(t.text.split()) for t in turns),
                speaking_seconds=time_by_speaker.get(speaker) if has_any_time else None,
            )
        )
    return stats
