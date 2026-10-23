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

from meeting_summarizer import __version__
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
