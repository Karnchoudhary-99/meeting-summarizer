import json
from datetime import date

from meeting_summarizer.cli import main
from meeting_summarizer.minutes import render_minutes
from meeting_summarizer.report import build_report
from meeting_summarizer.transcript import parse_transcript

TRANSCRIPT = """\
[00:00:00] Priya: Priya will update the pricing page by Friday.
[00:00:10] Arjun: I will finish the migration by tomorrow.
[00:00:20] Sara: The team agreed the starter plan stays at nine dollars.
"""


def test_minutes_groups_followups_and_resolves_dates():
    transcript = parse_transcript(TRANSCRIPT)
    minutes = render_minutes(
        build_report(transcript), transcript, meeting_date=date(2026, 10, 19)
    )
    # Grouped by owner, alphabetical: Arjun before Priya.
    assert minutes.index("### Arjun") < minutes.index("### Priya")
    # Tomorrow (Tue 20th) and Friday (23rd) resolved to ISO dates.
    assert "(due: 2026-10-20)" in minutes
    assert "(due: 2026-10-23)" in minutes
    assert "## Speaker statistics" in minutes
    assert "| Priya | 1 |" in minutes


def test_minutes_without_date_keeps_due_phrases():
    transcript = parse_transcript(TRANSCRIPT)
    minutes = render_minutes(build_report(transcript), transcript)
    assert "(due: friday)" in minutes
    assert "Date:" not in minutes


def test_minutes_cli_writes_file_and_json(tmp_path, capsys):
    path = tmp_path / "meeting.txt"
    path.write_text(TRANSCRIPT, encoding="utf-8")
    out_file = tmp_path / "minutes.md"
    assert (
        main(
            [
                "minutes",
                str(path),
                "--meeting-date",
                "2026-10-19",
                "--output",
                str(out_file),
            ]
        )
        == 0
    )
    assert "(due: 2026-10-23)" in out_file.read_text(encoding="utf-8")
    assert main(["minutes", str(path), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["speaker_stats"]
    assert payload["follow_ups"][0]["owner"] == "Arjun"
