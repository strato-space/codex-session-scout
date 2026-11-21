---
name: codex-session-scout
description: Inspect local Codex session logs, find active threads, filter by title, session id, cwd, or repo path, and fetch recent event streams. Use when you need to understand what Codex sessions are doing right now or to recover the status of a specific thread.
---

# Codex Session Scout

Use this skill when the task is about local Codex session history, live thread activity, or diagnosing a reported hook/command failure.

Typical uses:

- find the sessions that are active right now
- locate a session by partial title, session id, cwd, or repo context
- check whether a session is `running`, `completed`, or `stale`, with default `agent_type` visibility
- fetch a session and inspect the latest messages or raw events
- investigate generic `Hook failed` messages using local session, OMX, Codex app-log, and optional tmux evidence

## Commands

Run the bundled tool directly:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --view ops --active-within 24h
```

The pinned operational table is `Live, Age, Status, Agent, Session, CWD, Title`; `Age` is time since the session was created and `Live` is time since the last log activity. Always keep `Session` as the full UUID because it is copied into `codex resume <session-id>`; do not abbreviate it in summaries.

Filter by a title fragment or id:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --query build --view ops
```

Use regex matching:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --regex 'review|worker' --view ops
```

Use path-aware filtering:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --view paths --cwd /home/strato-space/copilot
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --columns live,age,status,agent_type,id,cwd,repo,title --repo strato-space/copilot
```

Use full-text matching across raw session JSONL:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --source all --fulltext 'codex-plugin-session-repair-2026-03-21.md' --columns id,title
```

Use regex matching across raw session JSONL:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --source all --fulltext-regex 'Update File: .*codex-plugin-session-repair' --columns id,title
```

Fetch one session:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout fetch <session-id>
```

Follow one session in streaming mode (tail -f style):

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout follow <session-id>
```

Diagnose a visible hook failure such as `Hook failed / hook exited with code 1`:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout diagnose SESSION_ID --tmux-pane '%0' --since 30m
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout diagnose SESSION_ID --since 30m --format json
```

`diagnose` correlates the exact session with recent OMX native-hook records in
`<session-cwd>/.omx/logs/native-hook-*.jsonl`, warnings/errors from
`$CODEX_HOME/logs_2.sqlite` (default: `~/.codex/logs_2.sqlite`), and OMX
plugin-cache live-pin lock metadata. Use `--codex-log-db` or `--omx-log-dir`
when those logs live elsewhere. The time window is relative to now; narrow it
with `--since` when several sessions are active.

Use `--tmux-pane` only when the user asks to inspect a pane or provides its id.
It runs `tmux capture-pane` read-only and never sends keys or changes pane state.
The pane tail can contain private prompt text. A stranded mutation lock can be
identified when its owner exited, its expected `.stage-*` hard link is absent,
and a same-inode `.reclaim-*` link remains. This can block required live-pin
registration before native-hook dispatch. The diagnostic never removes locks
or pin files. If no matching logs or pin-lock evidence exists, preserve that
uncertainty instead of guessing a failing event or command.

## Workflow

1. Start with `list --view ops --active-within 24h` when the user wants a live operational view.
2. Add `--query` or `--regex` for title/id lookups, and `--cwd` / `--cwd-regex` / `--repo` for workdir-aware filtering when the list is noisy.
3. Add `--fulltext` or `--fulltext-regex` when you need to search session content, not just title/id metadata.
4. Use `fetch <session-id>` when the user asks what a session is doing or what it did last.
5. Use `diagnose <session-id>` for hook failures; capture a tmux pane only with an explicit pane id.
6. Summarize the relevant recent events instead of dumping the entire log unless the user asks for raw output.

## Notes

- The public CLI uses dash-case command names and explicit subcommands.
- The default `ops` view shows `Agent` / `agent_type` (`user` or a subagent role such as `architect` / `code-reviewer`) when session metadata provides it.
- The tool reads renamed thread names from `session_index.jsonl` when available.
- `path` remains the session log file path; `cwd` and `repo` are first-class metadata surfaces when they exist in session logs.
- The default data sources resolve from `CODEX_HOME` or `~/.codex`; app logs use `logs_2.sqlite` under the same root.

## Inspect user requirements and outcomes

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout transcript SESSION_ID
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout transcript SESSION_ID --message MESSAGE_ID --format json
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout transcript SESSION_ID --format compact --max-agent-chars 1500
```

The first command lists chronological user-authored messages without tool output;
select one or more exact IDs (repeat `--message`) to include available final
answers. IDs are session-scoped; `line:N` falls back to an append-only file line.
`ambiguous_shared_turn` marks finals shared by multiple user messages (or
multiple finals), not a proven one-to-one response. `interrupted`, `no_final`,
and `unknown_turn` mean completion or linkage is unproven. Missing text may
represent an attachment. Compare source events when accuracy matters; never
assume a final answer proves execution. Malformed event counts go to stderr.

Use `--format compact` when reviewing requests and replies across a session. It
prints `---USER` / `---AGENT` blocks, skips tool output, and labels ambiguous,
interrupted, missing, or unlinked answers instead of asserting a false match.
Add `--max-agent-chars N` to clip each final answer with a visible truncation
marker. Omit the cap to retain complete answer text. Existing JSON and JSONL
output is unchanged.
