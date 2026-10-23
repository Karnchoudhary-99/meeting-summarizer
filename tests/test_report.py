import json

from meeting_summarizer.cli import main
from meeting_summarizer.report import build_report, render_markdown
from meeting_summarizer.transcript import parse_transcript

TRANSCRIPT = """\
[00:00:05] Priya: Welcome to the launch review.
[00:00:20] Sara: The team agreed the starter plan stays at nine dollars.
[00:00:40] Priya: Priya will update the pricing page by Friday.
[00:01:00] Arjun: Who owns weekend cover for launch week?
"""


def test_build_report_combines_all_sections():
    report = build_report(parse_transcript(TRANSCRIPT))
    assert len(report.decisions) == 1
    assert len(report.actions) == 1
    assert report.actions[0].owner == "Priya"
    assert report.actions[0].due == "friday"
    assert len(report.questions) == 1
    assert report.speakers == ["Priya", "Sara", "Arjun"]
    assert report.turn_count == 4


def test_markdown_report_sections():
    markdown = render_markdown(build_report(parse_transcript(TRANSCRIPT)))
    assert "## Decisions" in markdown
    assert "## Action items" in markdown
    assert "- [ ] update the pricing page — Priya (due: friday)" in markdown
    assert "## Open questions" in markdown


def test_report_cli_markdown_and_json(tmp_path, capsys):
    path = tmp_path / "meeting.txt"
    path.write_text(TRANSCRIPT, encoding="utf-8")
    assert main(["report", str(path), "--format", "markdown"]) == 0
    assert "## Action items" in capsys.readouterr().out
    assert main(["report", str(path), "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["decisions"]) == 1
    assert len(payload["actions"]) == 1
    assert len(payload["questions"]) == 1
