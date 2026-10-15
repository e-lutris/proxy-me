#!/usr/bin/env python3
"""Extract the messages a human actually typed from local coding-agent transcripts.

Reads Claude Code transcripts (~/.claude/projects/**/*.jsonl) and, optionally,
Codex CLI transcripts (~/.codex/sessions/**/*.jsonl). Drops tool results, system
reminders, task notifications, messages from other sessions/subagents, compaction
summaries and other injected text, so only the user's own words remain.

Standard library only. Streams line by line, so multi-GB histories are fine.

Examples:
  extract.py                       # current project (and its worktrees)
  extract.py --project ~/my-app    # another project
  extract.py --all --since 90d     # every project, last 90 days
  extract.py --source codex        # Codex CLI history instead
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
CLAUDE_DIR = os.environ.get("CLAUDE_CONFIG_DIR", os.path.join(HOME, ".claude"))
CODEX_DIR = os.environ.get("CODEX_HOME", os.path.join(HOME, ".codex"))

# Text that starts like this was injected by the harness, not typed by a person.
DROP_PREFIXES = (
    "<system-reminder>",
    "<task-notification>",
    "<local-command-caveat>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<bash-input>",
    "<bash-stdout>",
    "<bash-stderr>",
    "<scheduled-task",
    "<channel ",
    "<user-prompt-submit-hook>",
    "<teammate-message",
    "<cross-session-message",
    "<agent-message",
    "[Request interrupted",
    "[Image:",
    "This session is being continued from a previous conversation",
    "Caveat: The messages below were generated",
    "Another Claude session sent a message",
    "Background (from the session that started this one)",
    "Tool loaded.",
    "Warmup",
    "# AGENTS.md instructions",
    "<environment_context>",
    "<user_instructions>",
    "<permissions instructions>",
)
# Injected by another session or a task even when a reminder block is stripped first.
DROP_PREFIXES_HARD = (
    "<task-notification>",
    "Another Claude session sent a message",
    "This session is being continued from a previous conversation",
)
INLINE_STRIP = [
    (re.compile(r"<system-reminder>.*?</system-reminder>", re.S), ""),
    (re.compile(r"<artifact-view-context[^>]*>.*?</artifact-view-context>", re.S), ""),
    (re.compile(r"<pasted_content[^>]*>.*?</pasted_content[^>]*>", re.S), " [pasted text] "),
    (re.compile(r"\[Image #\d+\]"), ""),
    (re.compile(r"\[Pasted text #\d+[^\]]*\]"), " [pasted text] "),
]
COMMAND_RE = re.compile(r"<command-name>\s*(/?[^<\s]+)\s*</command-name>", re.S)
COMMAND_ARGS_RE = re.compile(r"<command-args>(.*?)</command-args>", re.S)
# One-word acknowledgements carry no signal about what the user cares about.
ACKS = {
    "ok", "okay", "yes", "y", "no", "n", "go", "continue", "proceed", "thanks", "thank you",
    "ty", "lgtm", "sure", "plz", "please", "next", "done", "k", "yep", "nope",
    "はい", "いいえ", "ok です", "おk", "お願い", "お願いします", "おねがい", "よろしく", "続けて",
    "進めて", "続行", "ありがとう", "どうぞ", "許可する", "許可", "了解", "りょ", "うん", "いいよ",
}


def encode_project_dir(path: str) -> str:
    """Claude Code names a project's transcript folder after its path, non-alphanumerics -> '-'."""
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def parse_since(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    m = re.fullmatch(r"(\d+)([dwm])", value)
    now = dt.datetime.now(dt.timezone.utc)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        days = n * {"d": 1, "w": 7, "m": 30}[unit]
        return now - dt.timedelta(days=days)
    return dt.datetime.fromisoformat(value).replace(tzinfo=dt.timezone.utc)


def parse_ts(value) -> dt.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def clean_text(text: str, max_chars: int) -> str | None:
    text = text.strip()
    if not text:
        return None
    if "<command-name>" in text or "<command-message>" in text:
        name = COMMAND_RE.search(text)
        args = COMMAND_ARGS_RE.search(text)
        args_text = args.group(1).strip() if args else ""
        if not args_text:
            return None
        text = f"{name.group(1) if name else '/command'} {args_text}"
    if text.startswith(DROP_PREFIXES_HARD):
        return None
    # The app often prepends a reminder block to what the person typed; strip it, keep the rest.
    for pattern, repl in INLINE_STRIP:
        text = pattern.sub(repl, text)
    text = re.sub(r"[ \t]+\n", "\n", text).strip()
    if not text or text.startswith(DROP_PREFIXES):
        return None
    if not re.sub(r"\[pasted text\]", "", text).strip():
        return None  # nothing but pasted material
    if text.lower().rstrip("!.。！ ") in ACKS or len(text.replace(" ", "")) < 3:
        return None
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + " …[truncated]"
    return text


def content_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                return ""  # a tool result, not a person
            if block.get("type") in ("text", "input_text"):
                parts.append(block.get("text") or "")
        return "\n".join(parts)
    return ""


def is_human_claude(rec: dict) -> bool:
    if rec.get("isMeta") or rec.get("isCompactSummary") or rec.get("isSidechain"):
        return False
    if rec.get("isVisibleInTranscriptOnly"):
        return False
    origin = rec.get("origin")
    if isinstance(origin, dict):
        return origin.get("kind") == "human"
    if "turnOrigin" in rec or "promptSource" in rec:
        # Newer transcripts tag every prompt; anything not marked human came from
        # the app, another session, a schedule or the SDK.
        return rec.get("turnOrigin") == "human"
    return True  # older transcripts: rely on the text filters


def claude_files(project: str | None, include_all: bool) -> list[str]:
    root = os.path.join(CLAUDE_DIR, "projects")
    dirs = sorted(glob.glob(os.path.join(root, "*")))
    if not include_all:
        key = encode_project_dir(os.path.realpath(project))
        keep = []
        for d in dirs:
            name = os.path.basename(d)
            # the project itself, plus worktrees Claude Code makes inside it
            if name == key or name.startswith(key + "--claude-worktrees-"):
                keep.append(d)
        dirs = keep
    files = []
    for d in dirs:
        for f in glob.glob(os.path.join(d, "*.jsonl")):
            if os.path.basename(f).startswith("agent-"):
                continue  # subagent transcripts
            files.append(f)
    return files


def iter_claude(files, since):
    for path in files:
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"user"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("type") != "user" or not is_human_claude(rec):
                    continue
                ts = parse_ts(rec.get("timestamp"))
                if since and ts and ts < since:
                    continue
                msg = rec.get("message") or {}
                yield {
                    "ts": rec.get("timestamp") or "",
                    "project": rec.get("cwd") or "",
                    "session": rec.get("sessionId") or os.path.basename(path)[:-6],
                    "uuid": rec.get("uuid"),
                    "raw": content_text(msg.get("content")),
                }


def iter_codex(project, include_all, since):
    files = glob.glob(os.path.join(CODEX_DIR, "sessions", "**", "*.jsonl"), recursive=True)
    want = None if include_all else os.path.realpath(project)
    for path in files:
        cwd, interactive, session = "", True, os.path.basename(path)
        try:
            fh = open(path, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if "session_meta" not in line and "user_message" not in line and "UserMessage" not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                p = rec.get("payload") or {}
                if rec.get("type") == "session_meta":
                    cwd = p.get("cwd") or ""
                    session = p.get("id") or session
                    src = p.get("source")
                    # subagents, guardians, `codex exec` and MCP calls are not a person typing
                    interactive = isinstance(src, str) and src in ("cli", "vscode")
                    continue
                if not interactive:
                    break
                if want and not (cwd == want or cwd.startswith(want + os.sep)):
                    break
                text = None
                if p.get("type") == "user_message":
                    text = p.get("message")
                elif p.get("type") == "item_completed" and (p.get("item") or {}).get("type") == "UserMessage":
                    text = content_text((p.get("item") or {}).get("content"))
                if not text:
                    continue
                ts = parse_ts(rec.get("timestamp"))
                if since and ts and ts < since:
                    continue
                yield {"ts": rec.get("timestamp") or "", "project": cwd, "session": session, "uuid": None, "raw": text}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=os.getcwd(), help="project folder (default: current directory)")
    ap.add_argument("--all", action="store_true", help="read every project, not just one")
    ap.add_argument("--source", choices=["claude", "codex", "both"], default="claude")
    ap.add_argument("--since", help="only messages newer than this: 30d, 12w, 6m or YYYY-MM-DD")
    ap.add_argument("--max-chars", type=int, default=1200, help="truncate longer messages (default 1200)")
    ap.add_argument("--out", help="output folder (default: ~/.claude/proxy-me/<project>)")
    ap.add_argument("--chunk-chars", type=int, default=80000,
                    help="split messages.md into chunks of about this many characters (default 80000)")
    args = ap.parse_args()

    since = parse_since(args.since)
    label = "all-projects" if args.all else (os.path.basename(os.path.realpath(args.project)) or "root")
    out = os.path.expanduser(args.out or os.path.join(CLAUDE_DIR, "proxy-me", label))
    os.makedirs(out, exist_ok=True)

    streams = []
    n_files = 0
    if args.source in ("claude", "both"):
        files = claude_files(args.project, args.all)
        n_files += len(files)
        streams.append(iter_claude(files, since))
    if args.source in ("codex", "both"):
        streams.append(iter_codex(args.project, args.all, since))

    seen_uuid, seen_text, rows = set(), set(), []
    for stream in streams:
        for r in stream:
            if r["uuid"]:
                if r["uuid"] in seen_uuid:
                    continue  # forked/resumed sessions copy earlier messages
                seen_uuid.add(r["uuid"])
            text = clean_text(r["raw"], args.max_chars)
            if not text:
                continue
            h = hashlib.sha1(text.encode("utf-8")).hexdigest()
            if h in seen_text:
                continue
            seen_text.add(h)
            rows.append({"ts": r["ts"], "project": r["project"], "session": r["session"], "text": text})

    rows.sort(key=lambda r: r["ts"])

    with open(os.path.join(out, "messages.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Human-readable chunks, sized so one subagent can read one chunk.
    for old in glob.glob(os.path.join(out, "messages-*.md")):
        os.remove(old)
    chunks, buf, size = [], [], 0
    for r in rows:
        proj = os.path.basename(r["project"]) if r["project"] else "?"
        entry = f"- [{r['ts'][:16].replace('T', ' ')} · {proj}] {r['text']}\n"
        if buf and size + len(entry) > args.chunk_chars:
            chunks.append(buf)
            buf, size = [], 0
        buf.append(entry)
        size += len(entry)
    if buf:
        chunks.append(buf)
    for i, c in enumerate(chunks, 1):
        with open(os.path.join(out, f"messages-{i:02d}.md"), "w", encoding="utf-8") as f:
            f.write("".join(c))

    # Rough language mix so the report can be written in the user's language.
    cjk = sum(1 for r in rows if re.search(r"[぀-ヿ一-鿿가-힯]", r["text"]))
    projects: dict[str, int] = {}
    for r in rows:
        k = os.path.basename(r["project"]) if r["project"] else "?"
        projects[k] = projects.get(k, 0) + 1
    stats = {
        "output_dir": out,
        "source": args.source,
        "scope": "all projects" if args.all else os.path.realpath(args.project),
        "transcript_files": n_files if args.source != "codex" else None,
        "messages": len(rows),
        "chunks": len(chunks),
        "total_chars": sum(len(r["text"]) for r in rows),
        "first": rows[0]["ts"] if rows else None,
        "last": rows[-1]["ts"] if rows else None,
        "share_with_cjk_text": round(cjk / len(rows), 2) if rows else 0,
        "by_project": dict(sorted(projects.items(), key=lambda kv: -kv[1])[:15]),
    }
    with open(os.path.join(out, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if not rows:
        print("No messages found. Try --all, --project <path>, or --source codex.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
