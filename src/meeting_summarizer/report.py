"""Structured meeting report: summary + decisions + actions + questions.

Combines the extractive summary with the action, decision and
open-question extractors into one object that the CLI can render as
text, Markdown or JSON. Every section is traceable to the transcript:
summary sentences carry speaker and segment, actions carry speaker,
owner and due phrase.
"""

from __future__ import annotations

from dataclasses import dataclass

from .actions import ActionItem, extract_actions
from .decisions import Decision, extract_decisions
from .questions import OpenQuestion, extract_open_questions
from .summarize import Summary, summarize
from .transcript import Transcript


@dataclass
class MeetingReport:
    """Everything a reader needs from a meeting, in one object."""

    summary: Summary
    decisions: list[Decision]
    actions: list[ActionItem]
    questions: list[OpenQuestion]
    speakers: list[str]
    turn_count: int
    duration_seconds: int | None

    def to_dict(self) -> dict:
        return {
            "summary": self.summary.to_dict(),
            "decisions": [d.to_dict() for d in self.decisions],
            "actions": [a.to_dict() for a in self.actions],
            "questions": [q.to_dict() for q in self.questions],
            "speakers": self.speakers,
            "turn_count": self.turn_count,
            "duration_seconds": self.duration_seconds,
        }


def build_report(transcript: Transcript, max_sentences: int = 5) -> MeetingReport:
    """Build a full report from a parsed transcript."""
    return MeetingReport(
        summary=summarize(transcript, max_sentences=max_sentences),
        decisions=extract_decisions(transcript),
        actions=extract_actions(transcript),
        questions=extract_open_questions(transcript),
        speakers=transcript.speakers,
        turn_count=len(transcript.turns),
        duration_seconds=transcript.duration_seconds,
    )
