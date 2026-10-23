"""Demo: build a full report (decisions, actions, questions) from a meeting.

Run from the repo root:  PYTHONPATH=src python3 examples/report.py
"""

from pathlib import Path

from meeting_summarizer.report import build_report, render_markdown
from meeting_summarizer.transcript import parse_transcript

raw = (Path(__file__).parent / "actions-meeting.txt").read_text(encoding="utf-8")
report = build_report(parse_transcript(raw))
print(render_markdown(report))
