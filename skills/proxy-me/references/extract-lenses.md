# Brief: extract lenses from one chunk of messages

Give this to a subagent together with the path of one `messages-NN.md` chunk.

---

You are reading messages one person typed to their coding agent, oldest first. Each line is `- [date · project] text`. Your job is to learn **what this person keeps caring about**, so someone can later review their work the way they would.

Read the whole chunk. Then return, in the person's own language:

1. **Candidate lenses** — recurring concerns, complaints, corrections or quality bars. For each:
   - `name`: 3–6 words
   - `rule`: one line, phrased as a check ("X must match across every screen", "no long explanatory text on screens")
   - `look_for`: concrete, checkable signs in code or on screen
   - `count`: how many messages in this chunk express it
   - `quotes`: up to 3 short quotes (≤ 120 chars each) with their date, verbatim
2. **How they decide** — patterns in how they choose or approve (wants to see screenshots, compares with a reference product, asks for a recommendation, delegates fully, changes their mind after seeing it…). Quote 1–2 examples.
3. **Standing rules** — instructions given as "always / never / from now on / every time".
4. **Tells** — phrases that signal they are unhappy or about to correct something.
5. **Open threads** — things asked for, postponed or promised ("later", "after X", "remind me", "not now") with the date. Note if a later message in this chunk shows it was done.

Rules:
- Corrections and complaints are worth more than plain task requests. "Make a login page" is a task; "the login page jumps when it loads, fix it" is a lens (no layout shift).
- Generalise one level: "the drawer corner looks wrong" + "the card corner is off" → *corners/radius consistent with the platform*. Don't generalise into mush ("quality matters").
- Ignore pasted logs, code and error dumps except for what the person said about them.
- Do not invent. If a concern appears once and mildly, leave it out.
- Keep quotes verbatim and short. Do not include secrets, tokens, emails or personal data in quotes — skip that part of the quote.
