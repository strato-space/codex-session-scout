# Codex Session Scout

Codex Session Scout is a compact inspection tool for local Codex session logs.

It is built for the moments when the normal picker is too slow or too visual: finding the sessions that are active right now, sorting by fresh live activity, locating a thread by partial title or session id, and tailing the raw event stream when you need to understand what a session is actually doing.

## What It Does

- Lists local Codex sessions from `~/.codex/sessions`
- Optionally includes archived sessions from `~/.codex/archived_sessions`
- Reads renamed thread names from `session_index.jsonl`
- Sorts active sessions to the top using recent file activity
- Shows compact operational views with `live age`, `age`, derived `status`, `agent_type`, and session `cwd` / repo context
- Filters by substring or grep-style regex against thread name, preview, or session id, with dedicated cwd/repo filters for workdir-aware lookup
- Supports full-text and regex search inside the full JSONL session stream
- Fetches the full JSONL or JSON payload for any session id
- Recovers degraded sessions from `session_index.jsonl` when the backing `.jsonl` is zero-byte or metadata-empty

## CLI Design

The command-line interface was redesigned as an explicit subcommand CLI.

- No implicit default command
- No positional grep shortcuts
- No alias flags for the same concept
- One filtering model for text, regex, status, and live-activity windows
- One output model based on `--view` presets or explicit `--columns`

The public executable uses `dash-case`: `codex-session-scout`.

That choice is deliberate. This project exposes a shell command, not a Python import API, and dash-case is easier to scan in shell history, docs, and pasted commands. Underscores remain fine for internal Python modules, but not as the primary CLI surface.

## Quick Start

```bash
uv run ./codex-session-scout list --view ops --active-within 24h
```

Example output:

```text
Live  Age  Status     Agent          Session                               CWD                              Title
  0s  12m  running    user           019d1234-aaaa-bbbb-cccc-1234567890ab  /home/tools/app                  Release lane follow-up
  3m  28m  completed  code-reviewer  019d1234-aaaa-bbbb-cccc-1234567890ac  /home/tools/app                  Docs polish
 14m   2h  stale      architect      019d1234-aaaa-bbbb-cccc-1234567890ad  /home/tools/app.omx-worktrees/a  Regression sweep
```

## Useful Commands

Show the operational view for sessions with live activity in the last 24 hours:

```bash
uv run ./codex-session-scout list --view ops --active-within 24h
```

Filter by partial thread name or id:

```bash
uv run ./codex-session-scout list --query worker --view ops
uv run ./codex-session-scout list --query 019d1234 --columns id,title
```

Filter by workdir/repo context:

```bash
uv run ./codex-session-scout list --view paths --cwd /home/strato-space/copilot
uv run ./codex-session-scout list --columns live,age,status,agent_type,id,cwd,repo,title --repo strato-space/copilot
```

Use regex matching like `grep`:

```bash
uv run ./codex-session-scout list --regex 'review|postreview' --view ops
```

Inspect the raw event stream for one session:

```bash
uv run ./codex-session-scout fetch 019d1234-aaaa-bbbb-cccc-1234567890ab
```

Fetch as pretty JSON:

```bash
uv run ./codex-session-scout fetch --format json 019d1234-aaaa-bbbb-cccc-1234567890ab
```

Build a custom table shape:

```bash
uv run ./codex-session-scout list --columns live,age,status,agent_type,id,title --format table
```

Emit structured JSON for automation:

```bash
uv run ./codex-session-scout list --source all --status running --format json
```

Full-text search inside session content:

```bash
uv run ./codex-session-scout list --source all --fulltext 'codex-plugin-session-repair-2026-03-21.md' --columns live,age,status,agent_type,id,title
```

Regex search inside session content:

```bash
uv run ./codex-session-scout list --source all --fulltext-regex 'Add File: .*codex-plugin-session-repair' --columns id,title
```

## Agent Type

The default table is pinned to the operational shape `Live, Age, Status, Agent, Session, CWD, Title`. `Agent` is backed by `agent_type`, so user-driven sessions can be separated from Codex subagents at a glance. User threads render as `user`; subagent threads render their `agent_role` when available, for example `architect`, `code-reviewer`, or `scholastic`. Structured JSON output also includes `agent_type` and `agent_nickname`.

## Status Model

- `running`: recent live activity and the latest event is not `task_complete`
- `completed`: the latest event is `task_complete`
- `stale`: not completed, but no longer active in the current live window

Use `--running-window 5m` to control when a session is considered live. Use `--active-within 24h` when you want a filter, not a status threshold.

## Skill

This repository includes an installable Codex skill at:

`skills/codex-session-scout`

After installing the skill, Codex can use the tool to:

- find active sessions
- locate a session by title fragment, id, cwd, or repo
- inspect recent activity
- fetch a session and summarize the latest messages

## Files

- [`codex-session-scout`](./codex-session-scout): root launcher
- [`skills/codex-session-scout/scripts/codex-session-scout`](./skills/codex-session-scout/scripts/codex-session-scout): core implementation
- [`skills/codex-session-scout/SKILL.md`](./skills/codex-session-scout/SKILL.md): reusable skill definition

## License

MIT
