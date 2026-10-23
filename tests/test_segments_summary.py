from meeting_summarizer.segments import segment_transcript
from meeting_summarizer.summarize import split_sentences, summarize
from meeting_summarizer.transcript import parse_transcript

TWO_TOPICS = """\
Ana: The database migration is complete and the indexes are rebuilt.
Ben: Query latency dropped after the migration finished and caching improved.
Ana: The marketing campaign launches next week with new branding.
Ben: Social media ads and email newsletters drive the campaign launch.
"""

ONE_TOPIC = """\
Ana: The database migration is complete and the indexes are rebuilt.
Ben: Query latency dropped after the migration finished and caching improved.
Ana: The migration rollback plan stays ready in case latency returns.
"""


def test_segmentation_splits_disjoint_topics():
    segments = segment_transcript(parse_transcript(TWO_TOPICS).turns)
    assert len(segments) == 2
    assert segments[0].speakers == ["Ana", "Ben"]
    assert "migration" in segments[0].text()
    assert "campaign" in segments[1].text()


def test_segmentation_keeps_one_coherent_topic_together():
    segments = segment_transcript(parse_transcript(ONE_TOPIC).turns)
    assert len(segments) == 1


def test_segmentation_empty_transcript():
    assert segment_transcript([]) == []


def test_split_sentences_keeps_punctuation():
    assert split_sentences("Hello world. How are you? Fine!") == [
        "Hello world.",
        "How are you?",
        "Fine!",
    ]


def test_summary_covers_each_segment_within_budget():
    summary = summarize(parse_transcript(TWO_TOPICS), max_sentences=2)
    assert summary.segment_count == 2
    assert len(summary.sentences) == 2
    assert {s.segment_index for s in summary.sentences} == {0, 1}


def test_summary_keeps_meeting_order_and_respects_budget():
    summary = summarize(parse_transcript(ONE_TOPIC), max_sentences=2)
    assert len(summary.sentences) == 2
    text = summary.text()
    assert text.index(summary.sentences[0].text) < text.index(summary.sentences[1].text)


def test_summary_empty_transcript_is_empty():
    summary = summarize(parse_transcript(""), max_sentences=3)
    assert summary.sentences == []
    assert summary.segment_count == 0


def test_summary_scores_include_speaker_and_segment():
    summary = summarize(parse_transcript(TWO_TOPICS), max_sentences=4)
    entry = summary.to_dict()["sentences"][0]
    assert entry["speaker"] in ("Ana", "Ben")
    assert entry["segment"] in (0, 1)
    assert entry["score"] > 0
