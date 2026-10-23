from meeting_summarizer.transcript import clean_text, parse_transcript


def test_bracketed_timestamp_and_speaker():
    t = parse_transcript("[00:02:05] Priya: Hello everyone.")
    assert len(t.turns) == 1
    assert t.turns[0].speaker == "Priya"
    assert t.turns[0].start_seconds == 125


def test_plain_and_short_timestamp_forms():
    # Two-part stamps are MM:SS (video-style), so 00:10 is 10 seconds in.
    t = parse_transcript("00:10 Ana: First point.\nBen: Second point.")
    assert [turn.speaker for turn in t.turns] == ["Ana", "Ben"]
    assert t.turns[0].start_seconds == 10
    assert t.turns[1].start_seconds is None


def test_continuation_lines_join_previous_turn():
    t = parse_transcript("Ana: We need to decide\non the launch date today.")
    assert len(t.turns) == 1
    assert t.turns[0].text == "We need to decide on the launch date today."


def test_leading_unlabelled_line_becomes_unknown():
    t = parse_transcript("Welcome, everyone.\nAna: Thanks.")
    assert t.turns[0].speaker == "Unknown"
    assert t.turns[0].text == "Welcome, everyone."


def test_filler_cleanup_removes_interjections_only():
    assert clean_text("Um, we should, uh, ship it.") == "we should, ship it."
    # Real words are untouched: "like" is a verb, "humble" contains no filler.
    assert clean_text("I like this humble plan.") == "I like this humble plan."
    assert clean_text("You know, I mean, let's go.") == "let's go."


def test_speakers_in_first_appearance_order():
    t = parse_transcript("Ana: Hi.\nBen: Hi.\nAna: Again.")
    assert t.speakers == ["Ana", "Ben"]


def test_duration_is_span_of_timestamps():
    t = parse_transcript("[00:00:10] Ana: Hi.\n[00:05:10] Ben: Bye.")
    assert t.duration_seconds == 300


def test_blank_lines_ignored():
    t = parse_transcript("\nAna: Hi.\n\n\nBen: Bye.\n")
    assert len(t.turns) == 2
