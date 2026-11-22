## 2026-11-21 v2.6.1

### PROBLEM SOLVED
- Reviewing user requests together with replies required selecting messages and reading verbose JSON metadata, increasing output size for session retrospectives.

### FEATURE IMPLEMENTED
- Added `transcript --format compact` to render chronological `---USER` / `---AGENT` blocks without tool output.
- Compact output labels ambiguous, interrupted, missing, and unlinked answers while preserving full final-answer text as stored.

### CHANGES
- Preserved existing JSON and JSONL output behavior and bumped the CLI version to `2.6.1`.

## 2026-11-21 v2.6.0

### PROBLEM SOLVED
- Generic hook failures could be caused by a stranded OMX live-pin mutation lock, but the prior diagnostic only searched dispatcher/app-server logs and could miss failures that happened before dispatch.

### FEATURE IMPLEMENTED
- Added read-only inspection of cached OMX plugin versions, mutation-lock owner PID/liveness, hard-link counts, expected stage links, same-inode `.reclaim` links, and the diagnosed session's pending/live pin state.
- The diagnosis flags the stranded-reclaim pattern as a strong candidate for required live-pin registration failures and explains why no native-hook dispatch log may exist.

### SAFETY
- The command never deletes or repairs pin, lock, intent, or cache files.

### CHANGES
- Bumped CLI version to `2.6.0` and added fixture coverage for an orphaned reclaim hard link.

## 2026-11-21 v2.5.0

### PROBLEM SOLVED
- The session transcript did not retain generic hook failures shown by the TUI, so an `exit code 1` message could not be correlated with local dispatcher or app-server diagnostics.

### FEATURE IMPLEMENTED
- Added a read-only `diagnose` command to correlate a session with optional tmux pane output, OMX `native-hook-*.jsonl` records, and Codex app-server warnings/errors from `logs_2.sqlite`.
- Added explicit uncertainty reporting when the TUI exposes only a generic hook exit code and no diagnostic record identifies the failing event or cause.
- Added `CODEX_HOME` support for session, archive, and app-log lookup while preserving the installed `transcript` command.

### CHANGES
- Added `diagnose SESSION_ID` with `--tmux-pane`, `--since`, `--cwd`, `--omx-log-dir`, `--codex-log-db`, `--limit`, and JSON output options.
- Tmux inspection uses only `capture-pane`; the command never sends keys or mutates a pane. The Codex SQLite database is opened read-only.
- Added tests for session correlation, hook/app log filtering, optional pane capture, missing logs, and missing sessions.

## 2026-05-30 v2.4.2

### PROBLEM SOLVED
- Session ids in human summaries could be abbreviated even though operators need the full value for `codex resume <session-id>`.

### FEATURE IMPLEMENTED
- Documented that the `Session` column is always a full UUID and only `Title` is truncated by `--max-title`.

### CHANGES
- Bumped CLI version to `2.4.2`.

## 2026-05-30 v2.4.1

### PROBLEM SOLVED
- Ordinary `--query` / `--regex` filters could scan raw session logs, slowing metadata lookups on large session trees.

### FEATURE IMPLEMENTED
- Keeps title/id metadata filters responsive by avoiding full-log searches unless the user opts into `--fulltext` or `--fulltext-regex`.

### CHANGES
- Bumped CLI version to `2.4.1`.

## 2026-05-30 v2.4.0

### PROBLEM SOLVED
- Operational session lists did not distinguish user threads from Codex subagents without inspecting raw `session_meta` data.

### FEATURE IMPLEMENTED
- Added the default operational columns `Live`, `Age`, `Status`, `Agent`, `Session`, `CWD`, and `Title`; `Agent` is derived from session metadata.
- Added `agent_type` and `agent_nickname` to JSON output, and bounded metadata scanning to keep active-session views responsive on large logs.

### CHANGES
- Bumped CLI version to `2.4.0` and documented agent metadata in the README and skill.

## 2026-04-07 v2.3.0

### PROBLEM SOLVED
- Zero-byte Codex session files could effectively disappear from operational lookup even when `session_index.jsonl` still had the thread name, making incident recovery slower and inconsistent.
- Session inspection could not answer which repo/workdir a session belonged to without manual raw-log spelunking.
- Installed skill copies could fail with `Permission denied` when the script entrypoint lost its executable bit.

### FEATURE IMPLEMENTED
- Codex Session Scout now surfaces `cwd` and derived `repo` context directly in `list` output and supports workdir-aware filtering.
- Degraded session recovery now preserves visibility for zero-byte session files and emits a synthetic recovery payload in `fetch`.

### CHANGES
- Added `cwd` / `repo` columns and `--cwd`, `--cwd-regex`, `--repo`, `--repo-regex` filters to `skills/codex-session-scout/scripts/codex-session-scout`.
- Added `session_index.jsonl`-backed recovery metadata for zero-byte and metadata-empty sessions; `fetch --format json` now returns a `session_recovery` payload for degraded cases.
- Tightened recovery after review: full-text queries no longer leak index-only ghost sessions, and readable non-zero session files now keep returning their real event stream even when metadata is sparse.
- Updated `README.md`, `skills/codex-session-scout/SKILL.md`, and `skills/codex-session-scout/agents/openai.yaml` to document cwd/repo-aware lookup and degraded-session recovery.
- Bumped CLI version to `2.3.0` and restored the skill script's executable mode.

## 2026-03-26 v2.1.0

### PROBLEM SOLVED
- Session lookup could find a thread by metadata but could not search its full event text or match content with regular expressions.

### FEATURE IMPLEMENTED
- Added full-text and regex search across session content, separate from metadata-only filters.

### CHANGES
- Bumped CLI version to `2.1.0` and documented the new search options.

## 2026-03-26 v2.0.0

### PROBLEM SOLVED
- The CLI relied on implicit command behavior and positional grep shortcuts that made its interface ambiguous.

### FEATURE IMPLEMENTED
- Redesigned the CLI around explicit `list` and `fetch` subcommands and made filtering and output selection explicit.

### CHANGES
- Bumped CLI version to `2.0.0` and adopted the public `codex-session-scout` dash-case executable name.
