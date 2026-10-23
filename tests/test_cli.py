import json

import pytest

from meeting_summarizer.cli import main

TRANSCRIPT = """\
[00:00:05] Priya: The beta launch is scheduled for Friday.
[00:00:20] Arjun: The database migration must finish before the beta launch.
[00:00:40] Sara: The pricing page needs updated copy before the beta launch.
"""


@pytest.fixture
def transcript_file(tmp_path):
    path = tmp_path / "meeting.txt"
    path.write_text(TRANSCRIPT, encoding="utf-8")
    return path


def test_cli_version(capsys):
    assert main(["--version"]) == 0
    assert capsys.readouterr().out.strip() == "0.1.0"


def test_cli_summarize_text(transcript_file, capsys):
    assert main(["summarize", str(transcript_file), "--max-sentences", "2"]) == 0
    out = capsys.readouterr().out.strip()
    assert out
    assert out.count(".") <= 2


def test_cli_summarize_json(transcript_file, capsys):
    assert main(["summarize", str(transcript_file), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["speakers"] == ["Priya", "Arjun", "Sara"]
    assert payload["turn_count"] == 3
    assert payload["duration_seconds"] == 35
    assert payload["sentences"]
    assert payload["segments"]


def test_cli_summarize_stdin(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin.read", lambda: TRANSCRIPT)
    assert main(["summarize", "-", "--max-sentences", "1"]) == 0
    assert capsys.readouterr().out.strip()
