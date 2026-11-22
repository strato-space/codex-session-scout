---
name: codex-session-scout
description: Inspect local Codex session logs, review user requests with recorded final replies, find active threads, filter by title, session id, cwd, or repo path, and diagnose hook failures. Use when you need session history, activity, or local evidence about a reported failure.
---

# Codex Session Scout

Use this skill when the task is about local Codex session history, live thread activity, or diagnosing a reported hook/command failure.

Typical uses:

- find the sessions that are active right now
- locate a session by partial title, session id, cwd, or repo context
- inspect the derived `running`, `completed`, or `stale` status, with default `agent_type` visibility
- fetch a session and inspect the latest messages or raw events
- review user requests and recorded final replies in chronological order, preserving all extracted text without display truncation
- investigate generic `Hook failed` messages using local session, OMX, Codex app-log, and optional tmux evidence

## Commands

Run the bundled tool directly:

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout list --view ops --active-within 24h
```

The pinned operational table is `Live, Age, Status, Agent, Session, CWD, Title`; `Age` is time since the session was created and `Live` is time since the last log activity. Always keep `Session` as the full UUID because it is copied into `codex resume <session-id>`; do not abbreviate it in summaries.

For a session-file record, `Status` is inferred from effective activity time and the last nonempty line: a timestamp within the running window with no readable `task_complete` event is `running`; a last nonempty line that parses as `task_complete` is `completed`; and activity outside the window without that event is `stale`. Effective activity time is file modification time, except zero-byte session files use `session_index.jsonl`'s `updated_at` when available. A recent zero-byte or unreadable file can therefore be labeled `running`. Every index-fallback record is labeled `stale`, even if the underlying session file exists but its record was filtered out. These labels do not directly inspect process state; `stale` does not prove a thread was stopped or cancelled.

Known filter limitation: filters run before session IDs are marked as seen. `--status stale` can therefore show a file-backed session whose actual session-file record was `running` or `completed`, while `--status running` may omit such records. `--active-within` prefilters by file modification time before applying the zero-byte index timestamp fallback, so a zero-byte session with recent index activity may reappear as `stale`. For a status check, start with an unfiltered list and inspect the session with `fetch` if the result matters.

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
4. Use `transcript <session-id> --format compact` to review the user's requests and the final replies recorded for them. Use `fetch <session-id>` to inspect raw events and tool results when the user asks what actions the session attempted or performed.
5. Use `diagnose <session-id>` for hook failures; capture a tmux pane only with an explicit pane id.
6. For a status question, summarize relevant recent events. When the user asks to review requests and replies, return the compact transcript with its complete extracted text; do not shorten or truncate it to save space. A recorded final reply alone does not prove that the request was fulfilled or an action executed.

## Notes

- The public CLI uses dash-case command names and explicit subcommands.
- The default `ops` view shows `Agent` / `agent_type` (`user` or a subagent role such as `architect` / `code-reviewer`) when session metadata provides it.
- The tool reads renamed thread names from `session_index.jsonl` when available.
- `path` remains the session log file path; `cwd` and `repo` are first-class metadata surfaces when they exist in session logs.
- The default data sources resolve from `CODEX_HOME` or `~/.codex`; app logs use `logs_2.sqlite` under the same root.

## Inspect user requests and recorded final replies

```bash
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout transcript SESSION_ID
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout transcript SESSION_ID --message MESSAGE_ID --format json
uv run ~/.codex/skills/codex-session-scout/scripts/codex-session-scout transcript SESSION_ID --format compact
```

The first command lists chronological user-authored messages without tool output;
select one or more exact IDs (repeat `--message`) to include available final
answer text. IDs are session-scoped; `line:N` falls back to an append-only file line.
`ambiguous_shared_turn` marks finals shared by multiple user messages (or
multiple finals), not a proven one-to-one response. `interrupted`, `no_final`,
and `unknown_turn` mean completion or linkage is unproven. A recorded final is
evidence that text was logged, not that the request was fulfilled or an action
ran. Use `fetch` to inspect event and tool-result evidence when execution matters;
that evidence may still need interpretation. Missing text may represent an
attachment, which the transcript reader does not extract. Malformed event counts
go to stderr.

Use `--format compact` when reviewing requests and replies across a session. It
prints `---USER` / `---AGENT` blocks, skips tool output, and labels ambiguous,
interrupted, missing, or unlinked answers instead of asserting a false match.
It preserves all extracted text for each surfaced user message and available
final reply as stored, without display truncation; images and other non-text
content are not extracted. Existing JSON and JSONL output is unchanged.
