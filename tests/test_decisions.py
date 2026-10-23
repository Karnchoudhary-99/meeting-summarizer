from meeting_summarizer.decisions import extract_decisions
from meeting_summarizer.transcript import parse_transcript


def test_decisions_from_agreement_markers():
    transcript = parse_transcript(
        """Sara: The team agreed the starter plan stays at nine dollars.
Priya: The beta launch is scheduled for Friday.
Arjun: We decided to ship the migration on Thursday.
"""
    )
    decisions = extract_decisions(transcript)
    assert len(decisions) == 2
    assert decisions[0].speaker == "Sara"
    assert "nine dollars" in decisions[0].text
    assert decisions[1].speaker == "Arjun"


def test_plain_statements_are_not_decisions():
    transcript = parse_transcript("Priya: The migration risk is low.\n")
    assert extract_decisions(transcript) == []
