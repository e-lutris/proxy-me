# proxy-me

Most of the time, your agent waits for you: to review, to catch what's off, to say what's next. proxy-me is a skill that does that part as you.

It reads your local Claude Code or Codex history, learns the judgment behind your feedback, and turns it into something your agent can run on its own. Before you look, it has already gone through the project the way you would, flagged what you'd flag, and lined up what you'd want done next.

![proxy-me learns from the feedback you keep repeating, turns it into lenses, and reviews your project before you ask](assets/overview.svg)

## Install

```bash
npx skills add e-lutris/proxy-me
```

The [`skills` CLI](https://github.com/vercel-labs/skills) asks which agents to install into (Claude Code, Codex, Cursor, …) and whether to install for this project or globally. To install globally for Claude Code without prompts:

```bash
npx skills add e-lutris/proxy-me -g -a claude-code -y
```

Or as a Claude Code plugin:

```text
/plugin marketplace add e-lutris/proxy-me
/plugin install proxy-me@proxy-me
```

Installed as a plugin, the command is `/proxy-me:proxy-me`. Use one method, not both, or you'll have two copies of the same skill.

Requires Python 3 (standard library only) to read the transcripts.

## Use

In Claude Code, inside your project:

```text
/proxy-me
```

or just ask: *"review this the way I would before release"*, *"what would I point out here?"*, *"what did I forget to do?"*

- `/proxy-me learn` — only build/update your lenses.
- `/proxy-me review` — only review, using the lenses you already have.

### What happens

**1. Extract.** `scripts/extract.py` streams `~/.claude/projects/**/*.jsonl` (and optionally `~/.codex/sessions`) and keeps only what *you* typed. Tool output, system reminders, task notifications, messages from other sessions or subagents, compaction summaries and one-word acks are dropped. Multi-GB histories take seconds, and nothing leaves your machine.

![Transcripts are filtered on your machine down to only the messages you typed](assets/extract.svg)

**2. Learn.** The agent reads your messages (fanning out to subagents when there are many) and writes `lenses.md`: 8–15 lenses, each with a rule, what to look for and your own words as evidence, plus how you make decisions, rules you keep repeating, the phrases you use when something's off, and threads you never closed.

![An example lenses.md](assets/lenses.svg)

**3. Review.** It takes stock of the project (rules docs, screens, recent commits, TODOs, screenshots), splits the work across subagents by area, checks every finding against the actual file or screen, drops what it can't confirm, and ranks the rest.

![Review pipeline: inventory, fan out, verify, rank](assets/review.svg)

**4. Report.** `review-YYYY-MM-DD.md` with two lists, heaviest first (what you'd stop, and what you'd want done next), plus a short summary in chat.

### Extractor options

```bash
python3 skills/proxy-me/scripts/extract.py --help
```

| Option | Meaning |
|---|---|
| *(none)* | current project and the worktrees Claude Code made inside it |
| `--project <path>` | another project |
| `--all` | every project (your personal habits) |
| `--since 90d` | only recent messages (`30d`, `12w`, `6m` or a date) |
| `--source codex` / `both` | read Codex CLI history (interactive sessions only) |
| `--out <dir>` | output folder (default `~/.claude/proxy-me/<project>/`) |

## Privacy

Everything stays on your machine. Messages, lenses and reports are written to `~/.claude/proxy-me/`, outside your repository, and the skill is instructed never to commit or share them. Nothing is sent anywhere except to the model you are already using.

## Layout

```
skills/proxy-me/
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

