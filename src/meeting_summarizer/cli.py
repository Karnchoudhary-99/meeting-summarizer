"""CLI stub — transcript parsing and summarization land in the next chunk."""

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(prog="meeting-summarizer")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args(argv)
    if args.version:
        from meeting_summarizer import __version__

        print(__version__)
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
