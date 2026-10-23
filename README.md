# Meeting Summarizer

Turn a meeting transcript into a structured summary: key decisions,
action items (with owners), and open questions — no LLM API required for
the first pass. Pure standard library, so it runs anywhere Python does.

## Roadmap

- [x] Project scaffold (packaging, README, CI)
- [x] Transcript parsing (speaker turns, timestamps, filler cleanup)
- [x] Extractive summarization (topic segments + key sentences)
- [x] Action-item + decision extraction (owners, due phrases)
- [x] Full report (summary, decisions, actions, open questions)
- [x] CLI + export (text / JSON) + demo transcript
- [ ] Self-review checklist, then public

## Quick start

```bash
pip install -e .
python -m meeting_summarizer.cli summarize examples/demo-meeting.txt
```

The demo meeting (a 12-turn launch review) splits into three topic
segments — beta/migration, pricing, hiring — and summarizes to:

> We still need to finish the database migration before the beta launch
> on Friday. The pricing page needs updated copy before the beta launch,
> and the annual discount is twenty percent. The support rota for launch
> week is drafted and weekend cover is still unassigned. So to recap, the
> beta launches Friday after the migration, pricing updates ship with the
> new page copy, and support cover for launch week still needs an owner.

## How it works

- **Parsing** (`transcript.py`): `[HH:MM:SS]`, `MM:SS` and bare
  `Speaker: text` lines; unlabelled lines continue the previous turn.
  Fillers (`um`, `uh`, `you know`, `I mean`) are stripped and the
  initial capital restored.
- **Segmentation** (`segments.py`): TextTiling-style — windowed
  content-word cosine similarity across turn gaps, with a minimum
  segment size, so each topic gets its own block.
- **Summarization** (`summarize.py`): frequency-scored sentences with a
  segment-opener bonus; selection guarantees one sentence per segment
  when the budget allows, then fills by score and restores meeting
  order.

## CLI reference

```bash
# Text summary (default 5 sentences)
python -m meeting_summarizer.cli summarize transcript.txt --max-sentences 3

# JSON: sentences with speaker/segment/score, plus speakers, turn count,
# duration and per-segment metadata
python -m meeting_summarizer.cli summarize transcript.txt --format json

# Read from stdin
cat transcript.txt | python -m meeting_summarizer.cli summarize -
```

## Full report

The `report` command adds what a summary alone cannot: decisions the
meeting settled, action items with owners and due phrases, and questions
left open (a question answered later in the transcript is dropped).

```bash
# Text report: summary + decisions + actions + open questions
python -m meeting_summarizer.cli report transcript.txt

# Markdown minutes, or JSON for tooling
python -m meeting_summarizer.cli report transcript.txt --format markdown
python -m meeting_summarizer.cli report transcript.txt --format json
```

Action owners come from explicit assignment ("Assigned to Priya"),
a named subject ("Priya will update ...") or a first-person
commitment ("I will send ...", owned by the speaker); group
commitments ("We need to ...") stay unassigned. Due phrases such as
"by Friday" or "by end of week" are kept verbatim in the report.
See `examples/report.py` for a worked report over
`examples/actions-meeting.txt`.

## Minutes

The `minutes` command turns a report into a shareable document:
follow-ups grouped by owner, a speaker-statistics table, and — when
you pass the meeting date — due phrases resolved to real dates.

```bash
# Markdown minutes on stdout, or to a file
python -m meeting_summarizer.cli minutes transcript.txt
python -m meeting_summarizer.cli minutes transcript.txt --meeting-date 2026-10-19 --output minutes.md

# JSON minutes (report + speaker stats + grouped follow-ups)
python -m meeting_summarizer.cli minutes transcript.txt --format json
```

Talk time is estimated from turn timestamps (a turn runs until the
next one starts; the final turn contributes no time, and meetings
without timestamps report no time at all). See `examples/minutes.py`.

## Tests

```bash
python -m pytest -q
```

## License

MIT
