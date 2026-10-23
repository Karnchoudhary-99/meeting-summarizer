from meeting_summarizer.questions import extract_open_questions
from meeting_summarizer.transcript import parse_transcript


def test_unanswered_question_is_open():
    transcript = parse_transcript(
        """Priya: Who owns weekend cover for launch week?
Arjun: The migration runbook is ready.
"""
    )
    questions = extract_open_questions(transcript)
    assert len(questions) == 1
    assert questions[0].speaker == "Priya"


def test_answered_question_is_dropped():
    transcript = parse_transcript(
        """Priya: What is the launch date?
Arjun: The launch date is Friday after the migration.
"""
    )
    assert extract_open_questions(transcript) == []


def test_undecided_statement_is_open():
    transcript = parse_transcript(
        "Sara: We still need to decide the annual discount.\n"
    )
    questions = extract_open_questions(transcript)
    assert len(questions) == 1
    assert "annual discount" in questions[0].text
