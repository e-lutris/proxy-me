# style-mirror

**Teach your agent to judge its work the way you would.**

```
judge(what the agent did, or is about to do)  →  go / stop, and why
```

When you review an agent's work, you're running a judgment you never wrote down. It comes from experience, from instinct, and from the details you care about more than anyone else on the project. You've been exercising it for months, and every correction you typed left a trace in your local transcripts: *"it jumps when it loads"*, *"you fixed it here but not there"*, *"this copy is wrong for paying users"*.

`style-mirror` is an [Agent Skill](https://agentskills.io) that learns that judgment from those traces: your recurring criteria (**lenses**, each backed by your own quotes), how you make decisions, and the threads you left open. Then it applies it to the current project before you look, and hands you a ranked list of **what you would stop** and **what you would push next**.

## Install

```bash
npx skills add mkitsugi/style-mirror
```

The [`skills` CLI](https://github.com/vercel-labs/skills) asks which agents to install into (Claude Code, Codex, Cursor, …) and whether to install for this project or globally. To install globally for Claude Code without prompts:

```bash
npx skills add mkitsugi/style-mirror -g -a claude-code -y
```

Or as a Claude Code plugin:

```text
/plugin marketplace add mkitsugi/style-mirror
/plugin install style-mirror@style-mirror
```

Installed as a plugin, the command is `/style-mirror:style-mirror`. Use one method, not both, or you'll have two copies of the same skill.

Requires Python 3 (standard library only) to read the transcripts.

## Use

In Claude Code, inside your project:

```text
/style-mirror
```

or just ask: *"review this the way I would before release"*, *"what would I point out here?"*, *"what did I forget to do?"*

- `/style-mirror learn` — only build/update your lenses.
- `/style-mirror review` — only review, using the lenses you already have.

### What happens

1. **Extract** — `scripts/extract.py` streams `~/.claude/projects/**/*.jsonl` (and optionally `~/.codex/sessions`) and keeps only what *you* typed. Tool output, system reminders, task notifications, messages from other sessions/subagents, compaction summaries and one-word "ok"s are dropped. Multi-GB histories take seconds.
2. **Learn** — the agent reads your messages (fanning out to subagents if there are many) and writes `lenses.md`: 8–15 lenses with quotes, how you make decisions, standing rules you've repeated, the phrases you use when you're unhappy, and open threads you never closed.
3. **Review** — it inventories the project (rules docs, screens, recent commits, TODOs, screenshots), splits the work across subagents, **verifies every finding against the actual file or screen**, and ranks them.
4. **Report** — `review-YYYY-MM-DD.md` with two lists, heaviest first, plus a short summary in chat.

An example lens (fictional):

```markdown
### 2. Nothing jumps while loading
- Rule: no layout shift, flicker or late-appearing text on first paint or on back-navigation.
- Look for: async content without a placeholder; images without size; text that swaps after hydration.
- Quotes: "the header jumps every time I come back" (03-20) · "it flashes the default avatar first" (05-01)
```

### Extractor options

```bash
python3 skills/style-mirror/scripts/extract.py --help
```

| Option | Meaning |
|---|---|
| *(none)* | current project and the worktrees Claude Code made inside it |
| `--project <path>` | another project |
| `--all` | every project (your personal habits) |
| `--since 90d` | only recent messages (`30d`, `12w`, `6m` or a date) |
| `--source codex` / `both` | read Codex CLI history (interactive sessions only) |
| `--out <dir>` | output folder (default `~/.claude/style-mirror/<project>/`) |

## Privacy

Everything stays on your machine. Messages, lenses and reports are written to `~/.claude/style-mirror/`, outside your repository, and the skill is instructed never to commit or share them. Nothing is sent anywhere except to the model you are already using.

## Layout

```
skills/style-mirror/
├── SKILL.md                      # the workflow
├── scripts/extract.py            # transcript → your messages
└── references/
    ├── extract-lenses.md         # brief for subagents reading message chunks
    ├── lenses-template.md        # shape of lenses.md (fictional example)
    └── review-playbook.md        # inventory → fan out → verify → rank
.claude-plugin/                   # Claude Code plugin + marketplace manifests
```

## License

MIT

