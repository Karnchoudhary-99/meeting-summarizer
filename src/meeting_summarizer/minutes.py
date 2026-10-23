"""Minutes writer: a shareable Markdown document for one meeting.

Minutes reuse the report (summary, decisions, actions, questions) and
add two things a plain report lacks: action items grouped by owner as
follow-up checklists (sorted by resolved due date when a meeting date
is given), and a speaker-statistics table. Without a meeting date, due
phrases are shown verbatim instead of resolved dates.
"""

from __future__ import annotations

from datetime import date

from .dates import resolve_due
from .followups import group_by_owner, sort_by_due
from .report import MeetingReport
from .stats import speaker_stats
from .transcript import Transcript


def render_minutes(
    report: MeetingReport,
    transcript: Transcript,
    meeting_date: date | None = None,
) -> str:
    """Render full minutes as Markdown."""
    lines = ["# Meeting minutes", ""]
    if meeting_date is not None:
        lines.append(f"Date: {meeting_date.isoformat()}")
    lines.append(f"Attendees: {', '.join(report.speakers) or 'Unknown'}")
    lines.append(f"Turns: {report.turn_count}")
    if report.duration_seconds is not None:
        lines.append(f"Duration: {report.duration_seconds}s")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(report.summary.text() or "_No summary available._")
    lines.append("")
    lines.append("## Decisions")
    lines.append("")
    if report.decisions:
        lines.extend(f"- {d.text} ({d.speaker})" for d in report.decisions)
    else:
        lines.append("_None recorded._")
    lines.append("")
    lines.append("## Follow-ups")
    lines.append("")
    actions = report.actions
    if meeting_date is not None:
        actions = sort_by_due(actions, meeting_date)
    if actions:
        for owner, items in group_by_owner(actions):
            lines.append(f"### {owner}")
            lines.append("")
            for action in items:
                resolved = (
                    resolve_due(action.due, meeting_date)
                    if meeting_date is not None
                    else None
                )
                due = f" (due: {resolved.isoformat()})" if resolved else (
                    f" (due: {action.due})" if action.due else ""
                )
                lines.append(f"- [ ] {action.task}{due}")
            lines.append("")
    else:
        lines.append("_None recorded._")
        lines.append("")
    lines.append("## Open questions")
    lines.append("")
    if report.questions:
        lines.extend(f"- {q.text} ({q.speaker})" for q in report.questions)
    else:
        lines.append("_None recorded._")
    lines.append("")
    lines.append("## Speaker statistics")
    lines.append("")
    lines.append("| Speaker | Turns | Words | Speaking time (s) |")
    lines.append("| --- | ---: | ---: | ---: |")
    for stat in speaker_stats(transcript):
        time = str(stat.speaking_seconds) if stat.speaking_seconds is not None else "—"
        lines.append(f"| {stat.speaker} | {stat.turns} | {stat.words} | {time} |")
    lines.append("")
    return "\n".join(lines)
