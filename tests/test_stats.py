from meeting_summarizer.stats import speaker_stats
from meeting_summarizer.transcript import parse_transcript


def test_speaker_stats_counts_and_time():
    transcript = parse_transcript(
        """[00:00:00] Priya: Hello everyone welcome.
[00:00:10] Arjun: The migration is ready now.
[00:00:30] Priya: Great news indeed.
"""
    )
    stats = {s.speaker: s for s in speaker_stats(transcript)}
    assert stats["Priya"].turns == 2
    assert stats["Priya"].words == 3 + 3
    # Priya's first turn runs 0->10s; her last turn has no successor.
    assert stats["Priya"].speaking_seconds == 10
    assert stats["Arjun"].speaking_seconds == 20


def test_speaker_stats_without_timestamps_have_no_time():
    transcript = parse_transcript("Priya: Hello.\nArjun: Hi there friend.\n")
    stats = {s.speaker: s for s in speaker_stats(transcript)}
    assert stats["Priya"].speaking_seconds is None
    assert stats["Arjun"].words == 3
