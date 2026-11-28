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
- Correlates hook failures with optional read-only tmux capture, OMX native-hook logs, Codex app-server warnings/errors, and stranded OMX plugin-cache live-pin locks
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

Investigate a generic Codex hook failure for a known session. The pane capture is
opt-in and read-only; no keys are sent to tmux:

```bash
uv run ./codex-session-scout diagnose SESSION_ID --tmux-pane '%0' --since 30m
uv run ./codex-session-scout diagnose SESSION_ID --since 30m --format json
```

`diagnose` reads the session metadata, the project's `.omx/logs/native-hook-*.jsonl`,
`CODEX_HOME/logs_2.sqlite`, and OMX plugin-cache live-pin lock metadata in
read-only mode. It flags a stale lock whose expected stage link is missing but a
same-inode `.reclaim` link remains—a state that can prevent required pin
registration and make a hook exit before native-hook error logging. The command
never removes locks or pin files. A generic TUI message still does not identify
the failing event by itself; the output distinguishes direct evidence from a
likely pin-registration cause.

## Agent Type

The default table is pinned to the operational shape `Live, Age, Status, Agent, Session, CWD, Title`. `Session` is always the full session UUID so it can be copied directly into `codex resume <session-id>`; only `Title` is affected by `--max-title`. `Agent` is backed by `agent_type`, so user-driven sessions can be separated from Codex subagents at a glance. User threads render as `user`; subagent threads render their `agent_role` when available, for example `architect`, `code-reviewer`, or `scholastic`. Structured JSON output also includes `agent_type` and `agent_nickname`.

## Status Model

- `running`: for a session-file record, effective activity time is within the running window and the last nonempty line does not parse as a `task_complete` event
- `completed`: for a session-file record, the last nonempty line parses as a `task_complete` event
- `stale`: a session-file record has no recent activity and no latest `task_complete` event; every record emitted by the index fallback is also marked `stale`

Use `--running-window 5m` to control when a session is considered live. Use `--active-within 24h` when you want a filter, not a status threshold.

The effective activity time is the file's modification time, except that a zero-byte session file uses `session_index.jsonl`'s `updated_at` when available. These are operational labels inferred from local records, not a direct check of whether a Codex process or thread is alive. A recent zero-byte or unreadable session file can be labeled `running` because no `task_complete` event can be read. `stale` does not prove that a thread was stopped, cancelled, or abandoned.

Known filter limitation: filtering happens before session IDs are marked as seen. If a file-backed record is filtered out, the index fallback can emit the same ID as `stale` even though its session file exists. As a result, `--status stale` may show sessions whose file record was `running` or `completed`; `--status running` may omit those records. `--active-within` prefilters by file modification time before applying the zero-byte index timestamp fallback, so a zero-byte session with recent index activity may reappear as `stale`. For a status check, start with an unfiltered list and inspect the session with `fetch` if the result matters.

## User-message transcript

Use `transcript` to inspect user-authored messages in chronological order without
printing tool output or intermediate assistant commentary:

```bash
./codex-session-scout transcript SESSION_ID
./codex-session-scout transcript SESSION_ID --message MESSAGE_ID --message OTHER_ID --format json
./codex-session-scout transcript SESSION_ID --format compact
```

The command reconstructs user messages from the local session log and associates
available final-answer text with them using recorded turn information. The
association describes the log structure; it does not establish that the answer
fulfilled the request or that a reported action ran. Use `fetch` to inspect
recorded events and tool results when execution matters, and interpret that
evidence separately.

The default JSONL output includes the message ID, source line, timestamp, turn ID,
text, and association status; `--message` selects exact IDs and includes the
available final answer text. IDs use the original user item ID when available;
`line:N` is a stable fallback while the session file is append-only. IDs are
scoped to the session. A message with attachments may have empty text: the tool
does not extract images or other non-text content.

`matched` means exactly one user message and one final in a recorded turn, not
proof that the answer fulfilled the request. `ambiguous_shared_turn` means
multiple user messages or finals share a turn; the shared finals are shown as
candidates without claiming which message they answer. `interrupted`, `no_final`,
and `unknown_turn` preserve uncertainty. When explicit final events are absent,
a completed turn's `last_agent_message` is used if present. System and ambient
user-role messages are excluded when they lack user provenance. Malformed lines
are counted on stderr. No data is sent over the network. The reader supports
JSONL, gzip, and zstd using the same local sources as `fetch`.

Use `--format compact` to render chronological `---USER` / `---AGENT` blocks
without JSON metadata or tool output. It retains full extracted text without
display truncation, labels ambiguous answers as candidates, and keeps missing or
interrupted status in the agent marker. Non-text content such as images is not
extracted. JSON and JSONL formats keep their existing behavior.

## Skills

This repository includes two installable Codex skills:

- `skills/codex-session-scout` — inspect local Codex sessions and transcripts.
- `skills/close-session` — produce a durable session handoff and close-out.

Link them into a Codex skills directory so the repository remains the canonical source:

```sh
skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$skills_dir"
ln -sfn "$PWD/skills/codex-session-scout" "$skills_dir/codex-session-scout"
ln -sfn "$PWD/skills/close-session" "$skills_dir/close-session"
```

After installing `codex-session-scout`, Codex can use the tool to:

- find active sessions
- locate a session by title fragment, id, cwd, or repo
- inspect recent activity
- fetch a session and summarize the latest messages
- inspect user requests and their recorded final replies without truncating extracted text
- correlate a hook failure with a supplied tmux pane and local hook/app logs

After installing `close-session`, Codex can use it to:

- inspect the current session with `codex-session-scout` before writing the handoff
- preserve open work, decisions, tests, and unblock items in a durable location
- commit session-owned changes when safe and recommend whether to archive the session

## Files

- [`codex-session-scout`](./codex-session-scout): root launcher
- [`skills/codex-session-scout/scripts/codex-session-scout`](./skills/codex-session-scout/scripts/codex-session-scout): core implementation
- [`skills/codex-session-scout/SKILL.md`](./skills/codex-session-scout/SKILL.md): reusable skill definition
- [`skills/close-session/SKILL.md`](./skills/close-session/SKILL.md): durable session close-out workflow
- [`skills/close-session/REVIEW.md`](./skills/close-session/REVIEW.md): audit and repair rationale for the skill

## Development

Run tests with `python3 -m unittest discover -s tests -v`.

## License

MIT
