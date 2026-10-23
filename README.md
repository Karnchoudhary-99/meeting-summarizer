# Meeting Summarizer

Turn a meeting transcript into a structured summary: key decisions,
action items (with owners), and open questions — no LLM API required for
the first pass.

## Roadmap

- [x] Project scaffold (packaging, README, CI)
- [ ] Transcript parsing (speaker turns, timestamps, filler cleanup)
- [ ] Extractive summarization (topic segments + key sentences)
- [ ] Action-item + decision extraction (owners, due phrases)
- [ ] CLI + export (Markdown / JSON) + demo transcript
- [ ] Self-review checklist, then public

## Quick start

```bash
pip install -e .
python -m meeting_summarizer.cli --version
```

## License

MIT
