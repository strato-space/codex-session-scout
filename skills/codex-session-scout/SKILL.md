---
name: codex-session-scout
description: Inspect local Codex session logs, find active threads, filter by title, session id, cwd, or repo path, and fetch recent event streams. Use when you need to understand what Codex sessions are doing right now or to recover the status of a specific thread.
---

# Codex Session Scout

Use this skill when the task is about local Codex session history or live thread activity.

Typical uses:

- find the sessions that are active right now
- locate a session by partial title, session id, cwd, or repo context
- check whether a session is `running`, `completed`, or `stale`, with default `agent_type` visibility
- fetch a session and inspect the latest messages or raw events

## Commands

Run the bundled tool directly:

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout list --view ops --active-within 24h
```

The pinned operational table is `Live, Age, Status, Agent, Session, CWD, Title`; `Age` is time since the session was created and `Live` is time since the last log activity.

Filter by a title fragment or id:

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout list --query build --view ops
```

Use regex matching:

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout list --regex 'review|worker' --view ops
```

Use path-aware filtering:

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout list --view paths --cwd /home/strato-space/copilot
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout list --columns live,age,status,agent_type,id,cwd,repo,title --repo strato-space/copilot
```

Use full-text matching across raw session JSONL:

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout list --source all --fulltext 'codex-plugin-session-repair-2026-03-21.md' --columns id,title
```

Use regex matching across raw session JSONL:

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout list --source all --fulltext-regex 'Update File: .*codex-plugin-session-repair' --columns id,title
```

Fetch one session:

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout fetch <session-id>
```

Follow one session in streaming mode (tail -f style):

```bash
uv run ~/.agents/skills/codex-session-scout/scripts/codex-session-scout follow <session-id>
```

## Workflow

1. Start with `list --view ops --active-within 24h` when the user wants a live operational view.
2. Add `--query` or `--regex` for title/id lookups, and `--cwd` / `--cwd-regex` / `--repo` for workdir-aware filtering when the list is noisy.
3. Add `--fulltext` or `--fulltext-regex` when you need to search session content, not just title/id metadata.
4. Use `fetch <session-id>` when the user asks what a session is doing or what it did last.
5. Summarize the relevant recent events instead of dumping the entire log unless the user asks for raw output.

## Notes

- The public CLI uses dash-case command names and explicit subcommands.
- The default `ops` view shows `Agent` / `agent_type` (`user` or a subagent role such as `architect` / `code-reviewer`) when session metadata provides it.
- The tool reads renamed thread names from `session_index.jsonl` when available.
- `path` remains the session log file path; `cwd` and `repo` are first-class metadata surfaces when they exist in session logs.
- The default data sources are `/root/.codex/sessions` and `/root/.codex/archived_sessions`.
