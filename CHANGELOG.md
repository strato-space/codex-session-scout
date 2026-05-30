## 2026-05-30 v2.4.2

### PROBLEM SOLVED
- Session ids in human summaries could be abbreviated even though operators need the full value for `codex resume <session-id>`.

### FEATURE IMPLEMENTED
- Documented that the `Session` column is always a full UUID and only `Title` is truncated by `--max-title`.

### CHANGES
- Bumped CLI version to `2.4.2`.

## 2026-05-30

### PROBLEM SOLVED
- Operational session lists did not identify which rows were user sessions versus Codex subagents, forcing raw JSONL inspection of `session_meta` fields.

### FEATURE IMPLEMENTED
- Codex Session Scout now derives `agent_type` from `session_meta.agent_role` / subagent spawn metadata and shows it in the default `ops` and `paths` views.
- JSON output now includes `agent_type` and `agent_nickname` for automation.

### CHANGES
- Bumped CLI version to `2.4.1`.
- Documented `agent_type` semantics and updated default examples.

## 2026-04-07

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
