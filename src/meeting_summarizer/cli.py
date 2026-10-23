"""Command line interface.

    python -m meeting_summarizer.cli summarize transcript.txt
    python -m meeting_summarizer.cli summarize transcript.txt --max-sentences 3
    python -m meeting_summarizer.cli summarize transcript.txt --format json
    cat transcript.txt | python -m meeting_summarizer.cli summarize -
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date as _meeting_date

from meeting_summarizer import __version__
from meeting_summarizer.followups import group_by_owner
from meeting_summarizer.minutes import render_minutes
from meeting_summarizer.report import build_report, render_markdown
from meeting_summarizer.stats import speaker_stats
from meeting_summarizer.segments import segment_transcript
from meeting_summarizer.summarize import summarize
from meeting_summarizer.transcript import parse_transcript


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _cmd_summarize(args: argparse.Namespace) -> int:
    transcript = parse_transcript(_read_input(args.input))
    summary = summarize(transcript, max_sentences=args.max_sentences)
    if args.format == "json":
        payload = summary.to_dict()
        payload["speakers"] = transcript.speakers
        payload["turn_count"] = len(transcript.turns)
        payload["duration_seconds"] = transcript.duration_seconds
        payload["segments"] = [
            {"index": s.index, "speakers": s.speakers, "turns": len(s.turns)}
            for s in segment_transcript(transcript.turns)
        ]
        print(json.dumps(payload, indent=2))
    else:
        print(summary.text())
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    transcript = parse_transcript(_read_input(args.input))
    report = build_report(transcript, max_sentences=args.max_sentences)
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    elif args.format == "markdown":
        print(render_markdown(report))
    else:
        print(report.summary.text())
        if report.decisions:
            print("\nDecisions:")
            for decision in report.decisions:
                print(f"- {decision.text} ({decision.speaker})")
        if report.actions:
            print("\nAction items:")
            for action in report.actions:
                owner = action.owner or "Unassigned"
                due = f" (due: {action.due})" if action.due else ""
                print(f"- [ ] {action.task} — {owner}{due}")
        if report.questions:
            print("\nOpen questions:")
            for question in report.questions:
                print(f"- {question.text} ({question.speaker})")
    return 0


def _cmd_minutes(args: argparse.Namespace) -> int:
    transcript = parse_transcript(_read_input(args.input))
    report = build_report(transcript, max_sentences=args.max_sentences)
    meeting_date = (
        _meeting_date.fromisoformat(args.meeting_date)
        if args.meeting_date
        else None
    )
    if args.format == "json":
        payload = report.to_dict()
        payload["meeting_date"] = (
            meeting_date.isoformat() if meeting_date else None
        )
        payload["speaker_stats"] = [
            s.to_dict() for s in speaker_stats(transcript)
        ]
        payload["follow_ups"] = [
            {"owner": owner, "actions": [a.to_dict() for a in items]}
            for owner, items in group_by_owner(report.actions)
        ]
        output = json.dumps(payload, indent=2)
    else:
        output = render_minutes(report, transcript, meeting_date=meeting_date)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(output if output.endswith("\n") else output + "\n")
    else:
        print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="meeting-summarizer")
    parser.add_argument("--version", action="store_true")
    sub = parser.add_subparsers(dest="command")
    summarize_parser = sub.add_parser(
        "summarize", help="summarize a transcript file (or - for stdin)"
    )
    summarize_parser.add_argument("input", help="transcript file, or - for stdin")
    summarize_parser.add_argument(
        "--max-sentences", type=int, default=5, help="max summary sentences (default 5)"
    )
    summarize_parser.add_argument(
        "--format", choices=("text", "json"), default="text"
    )
    summarize_parser.set_defaults(func=_cmd_summarize)
    report_parser = sub.add_parser(
        "report", help="full report: summary, decisions, actions, questions"
    )
    report_parser.add_argument("input", help="transcript file, or - for stdin")
    report_parser.add_argument(
        "--max-sentences", type=int, default=5, help="max summary sentences (default 5)"
    )
    report_parser.add_argument(
        "--format", choices=("text", "markdown", "json"), default="text"
    )
    report_parser.set_defaults(func=_cmd_report)
    minutes_parser = sub.add_parser(
        "minutes", help="shareable Markdown minutes for a transcript"
    )
    minutes_parser.add_argument("input", help="transcript file, or - for stdin")
    minutes_parser.add_argument(
        "--max-sentences", type=int, default=5, help="max summary sentences (default 5)"
    )
    minutes_parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown"
    )
    minutes_parser.add_argument(
        "--meeting-date",
        default=None,
        help="meeting date as YYYY-MM-DD, for resolving due phrases",
    )
    minutes_parser.add_argument(
        "--output", default=None, help="write minutes to this file instead of stdout"
    )
    minutes_parser.set_defaults(func=_cmd_minutes)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
