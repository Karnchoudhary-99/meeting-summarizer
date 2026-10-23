# Meeting Summarizer

Turn a meeting transcript into a structured summary: key decisions,
action items (with owners), and open questions — no LLM API required for
the first pass. Pure standard library, so it runs anywhere Python does.

## Roadmap

- [x] Project scaffold (packaging, README, CI)
- [x] Transcript parsing (speaker turns, timestamps, filler cleanup)
- [x] Extractive summarization (topic segments + key sentences)
- [ ] Action-item + decision extraction (owners, due phrases)
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

## Tests

```bash
python -m pytest -q
```

## License

MIT
