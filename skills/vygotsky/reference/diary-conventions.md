# Diary Conventions

## Writing Diary Entries

Call `record_observation(concept, observation, evidence_type)` after the human
demonstrates understanding, struggles with something, or engages meaningfully.

### Evidence Types

| Type | Signal | When |
|------|--------|------|
| `prediction` | Learning | Human predicted behaviour before seeing it |
| `explanation` | Learning | Human explained concept in own words |
| `question` | Learning | Probing question revealing depth |
| `application` | Learning | Applied concept to new context in codebase |
| `transfer` | Learning | Connected to external knowledge or different domain |
| `correction` | Learning | Revised own wrong model after seeing evidence |
| `disagreement` | Mastery | Pushed back on Claude's approach with reasoning |
| `directive` | Mastery | Gave technically grounded instruction |
| `design_decision` | Mastery | Made architectural choice with reasoning |
| `gap` | Gap | Revealed missing prerequisite |
| `acknowledgment` | Low | Acknowledged without demonstrating (DEFAULT) |

### Good Diary Entries

- **Specific**: "Explained JWT vs session tokens clearly. Chose JWT because the API is stateless."
- **Behavioral**: "Asked about error propagation in promise chains"
- **Linked**: "This connects to [[error_handling]] — they struggled with try/catch in async."
- **Contextual**: "During the webhook handler implementation"

### Bad Diary Entries

- Scores: "7/10 understanding" — never.
- Vague: "Did well" — useless.
- Assumptions: "Probably understands X" — if you didn't observe it, don't write it.
