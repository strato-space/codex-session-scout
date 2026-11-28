---
name: close-session
description: >-
  Close the current session with a durable handoff in a ticket system, STATUS.md, repository, or local file; preserve open work and decisions, commit this session's changes when safe, and recommend archiving. Use when the user says "close-session", "close the session", "wrap up", "cerrá la sesión", "cerramos" or similar. Lighter than a release checklist: no release brief, no push to production.
---

# close-session

Goal: preserve the session's relevant outcomes and open work so the user can resume without rereading the conversation.
Report any gaps in the evidence or handoff. Describe outcomes; if
the harness has a better native way to do a step (its own close-out box, task list, archive action), use it.

**User overrides win.** If the user's instructions (CLAUDE.md, AGENTS.md or similar) define STATUS.md section names, a
priority marker, a language, a git policy or a status page, use theirs. Defaults below apply only where they say
nothing.

## Project instructions and Landing the Plane

Before choosing a handoff destination, find and read the applicable project `AGENTS.md` (including parent
directories and relevant nested instructions). If it contains a `Landing the Plane` / `Session Completion`
section, treat that section as part of this skill's required close-out workflow and follow its applicable steps;
do not silently skip it because this skill has a separate close-out sequence. Reconcile overlaps by following the
project instructions and the user's Git policy, while retaining this skill's privacy, ownership, and safe-write
constraints. Report any requirement that cannot be completed and why.

When Beads is configured for the project, include its applicable `Landing the Plane` steps in the close-out:
record actionable remaining work, update issue states, and verify the handoff in the correct Beads context. A `bd`
executable by itself does not prove that Beads belongs to the project; verify `.beads/` or another explicit project
configuration before writing.

For a Beads-backed project with no Git repository, adapt Git-specific Landing the Plane steps to the available
tracker: record pending work and the handoff in Beads, update and verify issue states, and report the Beads issue
identifiers. Do not run `git pull`, `git push`, `bd sync`, Git commit, branch cleanup, or other repository-only
steps when there is no Git repository. Do not treat the missing Git repository as a reason to skip the remaining
applicable Beads close-out steps or to claim a push occurred.

## Operating distinctions

- A **session observation** is evidence from this conversation or its Codex session record. A cross-session
  **pattern** is a recurrence of comparable observations across distinct sessions; one occurrence is not enough.
- A **handoff item** is unfinished, actionable work. An **issue tracker** is the project's configured system for
  recording and managing work, such as Beads, GitHub Issues, GitLab Issues, Jira, or Linear. A **bead** is an issue
  in Beads; other trackers use their own issue types and workflows.
- A **canonical skill copy** is the full, editable source in the user's repository. The installed copy under
  `~/.codex/skills/` is a runtime installation, not automatically a Git repository.
- The practical goal is continuity: preserve evidence-backed work and decisions so the next session can resume
  without reconstructing this conversation.

## 1. Inspect this session and find what is still open

Use the `codex-session-scout` skill to inspect the current session before writing the handoff:

1. Identify the exact current session. Prefer its full session ID; otherwise match the active Scout entry against
   the current working directory and conversation title. If more than one entry remains plausible, do not choose
   by recency alone. Use `fetch` for the selected session's events and `transcript --format compact` to review user
   requests and agent replies. If the session cannot be identified or read, state that limitation and do not claim
   introspection was completed.
2. Read for explicit user feedback, corrections, unresolved requests, and recurring interaction patterns. A
   recurrence claim requires evidence from at least two distinct sessions; repeated messages in one session count
   as one occurrence. The observations must concern the same behavior in comparable circumstances; two sessions
   are a minimum, not proof of a stable general tendency. Label uncertain comparisons as hypotheses. Record dates
   and enough source references to verify the comparison. Distinguish direct user feedback from agent inference.
3. Before writing transcript-derived material to Beads or any other issue tracker, check whether the remote or
   issue store is public/shared and whether the content includes sensitive details. Store only the minimum useful
   summary; omit transcript excerpts and full session IDs from public issues unless they are necessary and safe.
   Keep private evidence in the session record and reference it in a privacy-preserving way.
4. Turn an observation into a work item only when it identifies a concrete, useful change. Separate confirmed
   user feedback from an agent hypothesis; label the latter as tentative and omit it if it cannot be tested.
   Do not create generic “improve the assistant” items or duplicate an existing issue.

Then inspect the current repository (if one exists) and its existing status/backlog before collecting open items:


From this conversation and every repo or folder it touched, not only the working directory (for each Git repo,
`git status --short`, commits made in this session, and unpushed commits; without Git, inspect the configured
tracker and relevant files):
- **Test**: things built here that a human must try. Concrete steps: command, URL or flow, expected result.
- **Unblock**: decisions or actions only the user can take (product choices, approvals, credentials, pushing to a
  production repo, external accounts). Each with options and your recommendation.
- **Pending**: work discussed or started but not done, that was not resolved later in the conversation.
- **Decisions**: decisions taken here that a future agent must not reopen.

Anything you asked the user to do (run a script or command, apply a migration, change a setting, load a credential,
answer a question) that the conversation does not show as done goes under Unblock. If its effect is cheap to check
(the migration exists, the variable is set by name, the file changed), check it and drop it if done; never read secret
values to check.

Anything waiting on a third party (a reply, an approval, a support ticket) goes to the chosen task store with who, what was
asked, when, and what to do once it arrives. If it has a deadline, it also goes under Unblock.

Files this session produced outside any repo that the user needs (scratchpad, `/tmp`, downloads, generated reports)
disappear or get lost: move them into the repo, or name their full path in the close-out.

Drop anything resolved later in the same conversation. Do not invent items to fill a section.

**Loose threads: ask, in as few rounds as fit.** After reading the available `STATUS.md` and task store, go through the conversation
again for threads that fit none of the lists above and are not already recorded: an analysis or proposal you made that
the user never answered, an idea the user floated and nobody followed up, a question left hanging, a topic dropped
when the conversation moved on. You cannot tell on your own whether the user still wants these, so do not drop them
silently and do not file them as actionable work by default. Before asking, persist the known handoff using section 2;
record each unresolved thread there as awaiting the user's decision, without creating a task for it. Then ask one
question per thread (the harness's question UI when available),
with your recommendation first among backlog, Unblock and drop, and put as many questions in each round as the UI allows. If
there are more threads than fit, ask another round. If an answer opens a doubt (the user wants it but it is unclear
what exactly), ask a follow-up before filing it: a vague backlog item is as useless as a lost one. File what the user
keeps, drop the rest, and update the handoff after the user answers. If the harness has no question UI, ask the same
concise question in chat. While awaiting an answer, retain the saved handoff and recommend keeping the session. If
there are no loose threads, do not ask.

**If the conversation was compacted, or the context is above roughly 80% full** (the close-out itself could trigger a
compaction, and early turns are easy to miss in a very long context), read the full transcript before
listing anything: requests, decisions and pending work from the early part are exactly what a summary loses. Use the
harness's own way to read or search the session's transcript; in Claude Code CLI it is the session's `.jsonl` under
`~/.claude/projects/<project>/`, in Codex the rollout under `~/.codex/sessions/`. Do not load it into your own context,
which is already full: if the harness has subagents, hand the transcript to one on a cheaper model and ask it for the
list only (requests to the user, pending work, unblock items, decisions, each with where it appears), reading in
chunks. Without subagents, read it in chunks yourself and keep only the items, not the text. If it cannot be read, say
so in the close-out and recommend keeping the session instead of archiving.

## 2. Persist a handoff in every case

Always create or update a durable handoff, even if nothing the session touched lives in a repo. Resolve symlinks before deciding: a file under a
config folder (`~/.claude/scripts`, `~/.codex`) may link into a repo. Resolve it and find the owning Git root before
choosing where project work belongs. If the installed skill is a standalone file outside Git, do not treat the
skill installation directory as the project repo or write project handoff data there.

### 2a. Choose the handoff destination

Identify the relevant project and its existing task store, including a configured ticket system outside Git. Apply
user instructions and access permissions. Check for duplicate issues before creating or updating any. Preserve the
outcome, current state, actionable pending work, decisions, tests, blockers, relevant paths and a next-session prompt;
mark unknowns and do not invent work. Apply the privacy check in section 1 to all destinations.

The cases below can overlap. Choose in this order: explicit user or project instructions; an accessible configured
project tracker; an existing project `STATUS.md`; a new `STATUS.md` in the affected repo; otherwise a local handoff
file. If the selected configured destination is unavailable, use the fallback described below and report the gap.

- **Beads or another issue tracker configured for the project:** use that tracker's established workflow for both
  handoff and actionable follow-up, including improvements supported by session introspection. Verify that the
  tracker belongs to this project and is accessible. For Beads, verify its project context (for example `.beads/`
  and a working `bd` context); the executable alone is insufficient. For another tracker, use its configured
  project, issue types, permissions, and available integration or CLI; do not use Beads-specific commands or assume
  that `.beads/` is required. Create or update a handoff issue with the
  context needed to resume, and link or create separate actionable follow-up issues where useful. If `STATUS.md`
  is also maintained, update its concise status and link the issues.
- **Only a project `STATUS.md` is used:** update that file with the full handoff, including pending work and a
  next-session prompt. Do not require a separate backlog merely to hold that work.
- **Repo without a configured ticket system or existing status:** create `STATUS.md` at the repo root with the full
  handoff. Use an established backlog as well if the repo already has one; do not initialize Beads automatically.
- **No repo:** use an existing project `STATUS.md` or configured ticket system if available. If Beads is explicitly
  configured and accessible for this no-repo context, store the handoff and actionable follow-up there; apply the
  no-Git adaptation in Project instructions and Landing the Plane. Otherwise create a uniquely named Markdown
  handoff under `~/.codex/handoffs/` with the date and session ID when known, without overwriting another handoff.
  Include its absolute path or ticket identifier in the close-out.

If a configured store is unavailable or its configuration is uncertain, preserve the handoff in an existing local
`STATUS.md`, or in a uniquely named file under `~/.codex/handoffs/` if none exists. Report the failed destination
and fallback path; do not claim the ticket was created. Never initialize a tracker to resolve uncertainty.

### 2b. Handoff content and Git

- Durable decisions go where the repo keeps them (`AGENTS.md`, decision log, backlog notes). Ask only if it would
  change repo rules.
- When using `STATUS.md`, update it while preserving still-valid information from earlier sessions and removing
  items verified done. In a status-only project, add a Pending section with actionable items. Default layout:

```markdown
# Status

_Updated YYYY-MM-DD · <agent>_

## Test
- [ ] <flow>: <what changed>. How: <steps>. _(«conversation title» · tool · dd/mm)_

## Unblock
- <decision>. **Recommend:** <x>. (options: a / b / c) _(«conversation title» · tool · dd/mm)_

## Last change
<one line>

## Next session
<a ready-to-paste prompt for the next agent: objective, where to start, what not to reopen. Two to four lines.>
```

Empty sections say `Nothing.` Make it as long as needed, with urgent items first. Where a ticket system or backlog holds pending work, link it; where `STATUS.md` is the only store, keep the pending details there.

Prefix with `[PRIORITY]` the items that should not wait past this week (money at risk, a deadline, something blocking
other work), at most 3 per repo, and remove the mark once it no longer applies. A status page can surface them first.

Keep each item in that shape (what it is, the recommendation, the options or the how, the source conversation): the
status page splits items on those markers.

- Commit this session's own changes, including its implementation and handoff, in each affected repo, following
  the user's Git policy and any explicit instructions. Inspect the current status, staged and unstaged diffs, and
  session evidence to identify ownership. Stage only changes attributable to this session; inspect the staged diff
  before committing. Preserve pre-existing staged changes, other sessions' changes and unrelated work. If changes
  share a file, isolate only this session's hunks when safe; if ownership or isolation is uncertain, leave the mixed
  changes uncommitted and report the path and reason. When the normal index contains unrelated staged changes, an
  isolated temporary Git index may be used to construct and inspect the session-only commit. Preserve the normal
  index and verify its staged changes remain intact after the commit, accounting for the changed HEAD; use this
  approach only when that can be done safely. Otherwise leave the session changes uncommitted and explain why. Do
  not overwrite or reset another person's index or work.
  Push only where the user's policy permits; never push a production repo. Record an unavailable required push and
  failed CI under Unblock.

## 3. Close-out

The summary is 3 to 5 lines: what was done (one line), what to test, what to unblock, and anything to review. Use the
user's language, no headers. Steps 4 and 5 add at most one line each (the archive recommendation, the page refresh);
the whole close-out never goes beyond that.

Before printing, check that each test or unblock line in the summary is represented in the chosen durable handoff.
If missing, add it to that destination; never drop it from the summary to make them match. Include the handoff's
path or ticket identifier. If persistence fails, report the gap and recommend keeping the session.

## 4. Archive recommendation

First check what this session left running, by looking, not from memory: background shells and dev servers it
started (and the ports it used), scheduled wakeups, loops or cron jobs it created, subagents or side sessions still
working, worktrees with work not merged anywhere. Stop what is this session's own and no longer needed; anything that
must stay (a scheduled job, a side session) goes in the close-out. Never stop something another session started:
mention it in one line.

Recommend archiving or keeping the session, in one line with the reason:
- **Archive** when all open work is durably recorded in an appropriate accessible place, the necessary context can
  be recovered, nothing belonging to this session is running or uncommitted, and no session commits remain unpushed
  outside a production repo. Identify the handoff location in the close-out. If no durable handoff exists, recommend
  keeping the session.
- **Keep** when this session’s work is still running, uncommitted or unpushed outside a production repo, or its next
  step depends on context not captured in the handoff (say what). Mention other sessions’ work without stopping it.

Ask once, with the recommendation as the default answer (use the harness's question or button UI when it has one).
On yes, archive through the harness if it can; otherwise say it is safe to archive by hand.

## 5. Refresh the status page

Only if `STATUS.md` changed and the user's instructions name a status page and how to refresh it. Run exactly the
steps they give and nothing else. When they say the page reads from a database and a script prints the write to
apply, apply that output as printed: do not read the page, do not regenerate or republish it, do not open the
written file. If a step fails, skip the refresh and say so in one line; the page's own schedule will pick it up.
If this session changed the page's own code (its shell or template, not the data it shows), the data write alone
will not show it: republish the page once, the way the user's instructions say, and say so in the close-out.
Without such instructions, skip this step.
