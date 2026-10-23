"""Demo: render shareable Markdown minutes for the action-rich meeting.

Run from the repo root:  PYTHONPATH=src python3 examples/minutes.py
"""

from datetime import date
from pathlib import Path

from meeting_summarizer.minutes import render_minutes
from meeting_summarizer.report import build_report
from meeting_summarizer.transcript import parse_transcript

raw = (Path(__file__).parent / "actions-meeting.txt").read_text(encoding="utf-8")
transcript = parse_transcript(raw)
# The demo meeting is undated in the file; use a Monday so "by Friday"
# and "by end of week" resolve to a concrete week.
print(
    render_minutes(
        build_report(transcript), transcript, meeting_date=date(2026, 10, 19)
    )
)
