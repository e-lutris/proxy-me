# Review playbook — look at the project the way the user would

## 1. Inventory (you, before any subagent)

Collect, briefly:
- **Project rules:** `CLAUDE.md`, `AGENTS.md`, `README`, design/decision docs. Written rules are lenses too — a violation of a rule the user wrote down is always heavy.
- **Surface:** routes/screens/pages, main components, API endpoints, native shells, admin pages. A list with paths is enough.
- **Recent change:** `git log --oneline -40` and the files touched most. Recently changed areas regress; areas changed in one place only are where lens "fixed in one place" bites.
- **Open threads:** from `lenses.md`, plus `TODO`/`FIXME`/`XXX` in code and any task or plan files.
- **Screens:** if the user pointed to screenshots, use them. If there is a dev server and a browser tool, open the main screens (mobile width if the product is mobile) and save screenshots to the output folder. Don't start servers on ports another process is using.

## 2. Split into areas and fan out

3–6 areas, each small enough for one subagent to read properly. Typical split:
- one per screen group / feature area (e.g. onboarding & auth, core flow, settings & account, admin),
- one **consistency sweep** across the whole codebase: the same thing done differently in different places,
- one **platform / release** pass if the project ships to stores or several platforms.

Brief each subagent with: the full `lenses.md`, its area (paths, screenshots), "report only, don't edit", and the finding format below. Ask for at most ~12 findings each, best first.

### Finding format

```
- lens: <number and name>
  where: <file:line, route, or screenshot>
  what: <one sentence: what is wrong, concretely>
  why_they_care: <short quote from lenses.md>
  fix: <one sentence>
  size: S | M | L
  confidence: confirmed | plausible
```

## 3. Verify

For every finding: open the file at the line, or look at the screenshot, and confirm it is real and current (not already fixed on the branch, not intentional per a written rule). Merge duplicates across subagents. Drop what you cannot confirm; keep "plausible" only for things that need a device, account or data you don't have, and say what would confirm them.

## 4. Weigh and rank

Weight, roughly in this order:
1. **Breaks a written rule** of the project or a standing rule from the transcripts.
2. **Matches a high-frequency or emphatic lens** — the user has said it many times or with heat.
3. **User-visible on a main path** (first run, purchase, core loop) over edge screens.
4. **Release risk** — store review, payments, data loss, privacy, security.
5. **Cheap to fix** breaks ties: an S fix on a hot lens goes before an L fix on a cold one.

"Next to do" is ranked by what blocks the user's current goal (release, launch, a demo), then by how long the thread has been open.

## 5. Report

Write the report file (see SKILL.md), then in chat give: the top 5 of "fix before they say it", the top 3 of "next to do", and the path to the full file. Keep the chat summary short; the user can open the file.
