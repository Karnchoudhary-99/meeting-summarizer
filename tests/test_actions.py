from meeting_summarizer.actions import extract_actions, extract_due, extract_owner
from meeting_summarizer.transcript import parse_transcript


def test_owner_from_assignment():
    assert extract_owner("Assigned to Priya: fix the flaky test.", "Sara") == "Priya"
    assert extract_owner("Please assign it to Arjun.", "Priya") == "Arjun"


def test_owner_from_named_subject():
    assert extract_owner("Priya will update the pricing page.", "Sara") == "Priya"
    assert extract_owner("Arjun to review the migration runbook.", "Priya") == "Arjun"


def test_owner_from_first_person_is_speaker():
    assert extract_owner("I will send the notes tonight.", "Sara") == "Sara"


def test_owner_none_for_group_commitment():
    assert extract_owner("We need to finish the migration.", "Arjun") is None


def test_due_weekday_and_relative_phrases():
    assert extract_due("Priya will update the page by Friday.") == "friday"
    assert extract_due("Send it before next Monday.") == "next monday"
    assert extract_due("Finish by end of week.") == "end of week"
    assert extract_due("The launch is on Friday.") == "friday"


def test_due_none_without_phrase():
    assert extract_due("Priya will update the page soon.") is None


def test_extract_actions_from_transcript():
    transcript = parse_transcript(
        """Priya: Priya will update the pricing page by Friday.
Arjun: We still need to finish the database migration before the beta launch on Friday.
Sara: The pricing page needs updated copy.
"""
    )
    items = extract_actions(transcript)
    assert len(items) == 2
    assert items[0].task == "update the pricing page"
    assert items[0].owner == "Priya"
    assert items[0].due == "friday"
    assert items[1].task == "finish the database migration"
    assert items[1].owner is None
    assert items[1].due == "friday"
    # A plain statement with no commitment verb is not an action.
    assert all("updated copy" not in item.task for item in items)
