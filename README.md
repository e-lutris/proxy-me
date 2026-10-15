# style-mirror

**Your agent learns what you keep pointing out — then says it before you do.**

You've corrected your coding agent hundreds of times: *"it jumps when it loads"*, *"you fixed it here but not there"*, *"this copy is wrong for paying users"*. Those corrections are sitting in your local transcripts. `style-mirror` is an [Agent Skill](https://agentskills.io) that reads them, distills them into a handful of **lenses** (your recurring review criteria, with your own quotes), and then reviews the current project through those lenses — producing a ranked list of **what to fix before you'd have to say it** and **what to do next**.

[日本語は下にあります ↓](#日本語)

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

Use one method, not both, or you'll have two copies of the same skill.

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

---

## 日本語

**あなたがいつも言っていることを覚えて、言われる前に直すための skill。**

コーディングエージェントに何度も同じ指摘をしていませんか？「読み込みでガタつく」「ここは直ったけどあっちが古いまま」「課金した人にこの文言はおかしい」。そうした指摘は手元の会話ログに残っています。`style-mirror` はそれを読んで、あなたの「観点（レンズ）」を本人の言葉の引用つきでまとめ、その観点で今のプロジェクトを見直します。出てくるのは、重さ順の **「言われる前に直すこと」** と **「次にやること」** です。

### 入れ方

```bash
npx skills add mkitsugi/style-mirror
```

入れるエージェント（Claude Code・Codex・Cursor など）と、プロジェクトだけか全体か（`-g`）を聞かれます。Claude Code のプラグインとして入れる場合は:

```text
/plugin marketplace add mkitsugi/style-mirror
/plugin install style-mirror@style-mirror
```

どちらか一方だけにしてください。Python 3 が要ります（標準ライブラリだけ）。

### 使い方

プロジェクトのフォルダで `/style-mirror`。または「僕が言いそうなことを先に洗い出して」「リリース前に僕の目線で見直して」「やり残していることある？」と頼むだけでも動きます。

- `/style-mirror learn` … 観点づくりだけ
- `/style-mirror review` … いまある観点で見直しだけ

### 流れ

1. **抜き出す** — `~/.claude/projects` の会話ログから、あなたが打った文だけを取り出します（ツールの結果・システムの文・ほかのセッションからの連絡・「OK」だけの返事は除く）。
2. **観点にする** — `lenses.md` に、観点（引用つき）・決め方のくせ・何度も言っている決まり・不満のサイン・やりかけのことをまとめます。
3. **見直す** — ルールの文書・画面・最近のコミット・TODO・スクショを洗い、サブエージェントで手分けして見て、**ひとつずつファイルや画面で裏を取って**から残します。
4. **まとめる** — `review-YYYY-MM-DD.md` に重さ順の 2 つのリストを書き、チャットでは要点だけ伝えます。

### プライバシー

すべて手元に残ります。会話の抜き出し・観点・レポートはリポジトリの外（`~/.claude/style-mirror/`）に書き、コミットや外部への共有はしません。
