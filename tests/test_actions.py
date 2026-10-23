from meeting_summarizer.actions import extract_due, extract_owner


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
