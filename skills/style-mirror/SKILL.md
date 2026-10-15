---
name: style-mirror
description: Models the user as a function — input what the AI did or is about to do, output go / stop and why — learned from their own past coding-agent conversations (Claude Code / Codex transcripts on this machine) as "lenses" (experience, instinct, standards). Then reviews the current project through those lenses to list what to fix before they say it and what to do next, ranked by weight. Use when the user asks for a pre-release review "in my style", "what would I point out", "what did I forget", "what should we do next", or says 言われる前に直して / 僕が指摘しそうなこと / 次にやること / リリース前の見直し / 観点を振り返って.
license: MIT
metadata:
  version: "0.1.0"
---

# style-mirror

Treat the user as a function: `user(what the AI did or is about to do) → go / stop, and why`. Their experience, instinct and standards (the details they refuse to let slide) are the function body; their past corrections in the transcripts are its recorded calls. Learn the function from those calls, then run it on the project before they do — and say it first.

Two phases. Run both unless the user asked for only one (`learn` = phase 1 only, `review` = phase 2 with the existing lenses).

```
Phase 1  learn   transcripts ──extract.py──▶ messages ──read──▶ lenses.md
Phase 2  review  lenses.md + code + screens + open threads ──subagents──▶ verify ──▶ ranked report
```

## Ground rules

- **Everything stays local.** Messages, lenses and reports are written under `~/.claude/style-mirror/<project>/` (the extractor's output folder), not inside the repository. Never commit them, paste them into a PR, an issue, or any external service. If the user wants the report in the repo, ask first and leave quotes out.
- **Speak the user's language.** `stats.json` → `share_with_cjk_text` shows the mix; match how the user writes to you now. Quote the user in their original words.
- **Evidence or it didn't happen.** Every lens cites real quotes. Every finding cites a file:line, a screenshot, or a command output you actually saw.
- **Report, don't fix.** This skill produces a ranked list. Fix things only if the user then asks.

## Phase 1 — learn the lenses

1. **Extract.** The script is in `scripts/` next to this file (`${CLAUDE_SKILL_DIR}/scripts/extract.py` in Claude Code). Python 3, standard library only.

   ```bash
   # outside Claude Code, use this skill's folder instead of ${CLAUDE_SKILL_DIR}
   python3 "${CLAUDE_SKILL_DIR}/scripts/extract.py"                 # this project + its worktrees
   python3 "${CLAUDE_SKILL_DIR}/scripts/extract.py" --all --since 180d   # habits across all projects
   python3 "${CLAUDE_SKILL_DIR}/scripts/extract.py" --source both   # also Codex CLI history
   ```

   It keeps only what a person typed: tool results, system reminders, task notifications, messages from other sessions or subagents, compaction summaries and one-word acks are dropped. It prints `stats.json` and writes `messages.jsonl` and `messages-NN.md` chunks (≈80k chars each).

   - Fewer than ~40 messages for this project → run it again with `--all --since 180d` (into a different `--out`) and use both: the project file for project-specific lenses, the global one for personal habits.
   - Zero messages → tell the user what was searched (`scope` in the stats) and offer `--project <path>`, `--all`, or `--source codex`.

2. **Read.** One or two chunks: read them yourself. More: give each chunk to a subagent with the brief in [references/extract-lenses.md](references/extract-lenses.md) (run them in parallel), then merge. More than ~12 chunks: prefer `--since 120d` plus the newest chunks; old habits drift.

3. **Write `lenses.md`** next to the messages, in the shape of [references/lenses-template.md](references/lenses-template.md):
   - **Lenses** — 8 to 15 recurring things the user points out, most frequent / most emphatic first. Each has a one-line rule, *what to look for* (concrete, checkable), and 2–3 short dated quotes.
   - **How they decide** — e.g. wants screenshots before choosing, wants it to match a reference product, wants options with a recommendation, wants it done without being asked.
   - **Standing rules** — things said more than once that should already be rules ("always…", "never…", "from now on…").
   - **Tells** — words or phrasing that signal dissatisfaction (e.g. "again?", "this looks cheap", "why is…"), so you can recognise them early.
   - **Open threads** — things asked for or promised ("later", "after release", "not yet") that the transcripts never show as done. These feed "next to do".

   Merge, don't duplicate: one lens per underlying concern. Drop one-off requests that never recurred unless the user was emphatic.

4. If `lenses.md` already exists and is fresh (newer than the last extracted message, or the user said `review`), skip to phase 2. If it exists but is stale, update it in place and keep lens numbers stable.

## Phase 2 — review the project through the lenses

Follow [references/review-playbook.md](references/review-playbook.md). In short:

1. **Inventory** what can be reviewed: project instructions (`CLAUDE.md`, `AGENTS.md`, design docs), the screens/routes, components, recent `git log` (what changed lately is where regressions hide), TODO/FIXME, open threads from the lenses, and any screenshots the user points to. If the project has a dev server and you have a browser tool, take screenshots of the main screens.
2. **Split** the work into 3–6 areas (e.g. by screen group, by layer, plus one "consistency sweep" across the whole codebase) and give each subagent the full `lenses.md`, its area, and the finding format. Without subagents, do the areas one by one.
3. **Verify** every candidate yourself or with a second pass: open the file:line, reproduce on screen, re-read the rule. Drop anything you can't confirm. Mark "plausible" only when it needs the user's device or data to confirm.
4. **Rank** with the weight rules in the playbook and write the report.

## Report

Write `review-YYYY-MM-DD.md` in the output folder, then give the user a short summary in chat. Two lists, heaviest first:

- **Fix before they say it** — concrete defects the user would point out, each with: lens, where (file:line / screen), what's wrong, why they'd care (quote), suggested fix, size (S/M/L).
- **Next to do** — the open threads and gaps that block the user's goal, each with why now and the first step.

End with what you didn't check (screens you couldn't open, platforms you couldn't run). If the user prefers a visual page and your environment can publish one, offer it in one line.
