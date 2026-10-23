"""Demo: parse the bundled meeting, show its segments, print a summary.

Run from the repo root:  PYTHONPATH=src python3 examples/demo.py
"""

from pathlib import Path

from meeting_summarizer.segments import segment_transcript
from meeting_summarizer.summarize import summarize
from meeting_summarizer.transcript import parse_transcript

raw = (Path(__file__).parent / "demo-meeting.txt").read_text(encoding="utf-8")
transcript = parse_transcript(raw)
print(f"Speakers: {', '.join(transcript.speakers)}")
print(f"Turns: {len(transcript.turns)}")
print()
for segment in segment_transcript(transcript.turns):
    print(f"--- Segment {segment.index} ({', '.join(segment.speakers)}) ---")
    print(segment.text())
    print()
summary = summarize(transcript, max_sentences=4)
print("--- Summary ---")
print(summary.text())
