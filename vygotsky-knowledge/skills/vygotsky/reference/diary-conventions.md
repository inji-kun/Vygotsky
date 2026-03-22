# Diary Conventions

## Recording Discipline

**Record whenever you observe something genuinely informative. No fixed quota.**

The diary builds a model of a person across sessions. A reasonable picture emerges
after a handful of sessions — some within-session signals are genuinely strong
(clear demonstration, accurate self-report, revealing mistake), others are noise.
Be wary of overfitting: a single session is a small sample. Hold within-session
observations lightly unless the signal is unusually clear. When uncertain, record
the uncertainty or don't record at all. Let the extant body of diary entries guide
your judgment — if a concept already has rich observations, raise the bar for what's
worth adding.

The diary is Claude's private working memory, not a report card for the thinker.
Write entries directly to `~/.vygotsky/diary/{concept-slug}.md`.
Tag all entries with `(vygotsky-knowledge)`.

## Writing Diary Entries

Append a diary entry after the human demonstrates understanding, struggles with
something, or engages meaningfully. Use the Write tool to append to the concept file.

### Evidence Types

| Type | Signal | When |
|------|--------|------|
| `prediction` | Learning | Human predicted how an argument would land or what a source would say |
| `explanation` | Learning | Human explained a concept or argument in own words |
| `connection` | Learning | Linked concepts together or asked a probing question |
| `extension` | Learning | Applied concept to new context or extended it |
| `transfer` | Learning | Connected to external knowledge or different domain |
| `correction` | Learning | Revised own wrong model after seeing evidence |
| `disagreement` | Mastery | Pushed back on Claude's framing with reasoning |
| `directive` | Mastery | Gave substantively grounded instruction on content or structure |
| `argument_choice` | Mastery | Chose between competing arguments or framings with reasoning |
| `source_integration` | Mastery | Made deliberate choice about how to use a source |
| `structural_decision` | Mastery | Made architectural choice about the piece's structure with reasoning |
| `gap` | Gap | Revealed missing prerequisite concept or knowledge |
| `acknowledgment` | Low | Acknowledged without demonstrating (DEFAULT) |
| `calibration` | Internal | Claude adjusting its own engagement strategy |

### The `calibration` type

Use `calibration` when adjusting engagement strategy mid-session — it's Claude's
private reasoning voice, not an observation about the thinker. Use only when a
genuine strategy shift is happening.

Good calibration entry:
> "Three rubber-stamps on section ordering decisions. Feels like overwhelm not
> disinterest. Shifting SP → Sparring. Will surface the weakest section's argument
> explicitly rather than presenting a structure. If engagement picks up, move back."

### Good Diary Entries

- **Specific**: "Explained the tension between Dunbar's social brain hypothesis and distributed cognition clearly. Chose to frame language as UX paradigm rather than cognitive prerequisite."
- **Behavioral**: "Asked about how the reader would respond to the counterargument in section 3"
- **Linked**: "This connects to [[philosophy-of-mind]] — they struggled with the hard problem framing."
- **Contextual**: "During the grant proposal methodology section"
- **Honest about uncertainty**: "May be navigating by intuition on the theoretical framework — needs more sessions to confirm."

### Bad Diary Entries

- Scores: "7/10 understanding" — never.
- Vague: "Did well" — useless.
- Assumptions: "Probably understands X" — if you didn't observe it, don't write it.
- Overfit: Recording every exchange — the model gets noisier, not richer.
