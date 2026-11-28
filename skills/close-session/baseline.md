---
name: close-session
description: Close the current session so the user never has to read its transcript. Moves open items to the repo's backlog and STATUS.md, prints a 3-5 line close-out (what to test, what to unblock), recommends archiving, and refreshes the user's status page if they have one. Use when the user says "close-session", "close the session", "wrap up", "cerrá la sesión", "cerramos" or similar. Lighter than a release checklist: no release brief, no push to production.
---

# close-session

Goal: after this runs, nothing in the conversation is lost and the user can archive it unread. Describe outcomes; if
the harness has a better native way to do a step (its own close-out box, task list, archive action), use it.

**User overrides win.** If the user's instructions (CLAUDE.md, AGENTS.md or similar) define STATUS.md section names, a
priority marker, a language, a git policy or a status page, use theirs. Defaults below apply only where they say
nothing.

## Operating distinctions

- A **session observation** is evidence from this conversation or its Codex session record. A **pattern** is a
  repeated observation across distinct sessions; one occurrence is not a pattern.
- A **handoff item** is unfinished, actionable work. A **bead** is a project issue managed by Beads, not a synonym
  for every note or status summary.
- A **canonical skill copy** is the full, editable source in the user's repository. The installed copy under
  `~/.codex/skills/` is a runtime installation, not automatically a Git repository.
- The practical goal is continuity: preserve evidence-backed work and decisions so the next session can resume
  without reconstructing this conversation.

## 1. Inspect this session and find what is still open

Use the `codex-session-scout` skill to inspect the current session before writing the handoff:

1. Locate the current session from the active session list or known session ID. Use `fetch` for its events and
   `transcript --format compact` to review user requests and agent replies. If the current session cannot be
   identified or read, state that limitation and do not claim introspection was completed.
2. Read for explicit user feedback, corrections, unresolved requests, and recurring interaction patterns. For a
   recurrence claim, compare distinct sessions with Scout search/fetch; do not infer recurrence from repeated
   messages in one session. Keep observations specific and supported by session IDs or event references when
   available. Do not copy private transcript content into a public issue unnecessarily.
3. Turn an observation into a work item only when it identifies a concrete, useful change. Separate confirmed
   user feedback from an agent hypothesis; label the latter as tentative and omit it if it cannot be tested.
   Do not create generic “improve the assistant” items or duplicate an existing issue.

Then inspect the current repository and its existing status/backlog before collecting open items:


From this conversation and every repo or folder it touched, not only the working directory (`git status --short`,
commits made in this session, unpushed commits):
- **Test**: things built here that a human must try. Concrete steps: command, URL or flow, expected result.
- **Unblock**: decisions or actions only the user can take (product choices, approvals, credentials, pushing to a
  production repo, external accounts). Each with options and your recommendation.
- **Pending**: work discussed or started but not done, that was not resolved later in the conversation.
- **Decisions**: decisions taken here that a future agent must not reopen.

Anything you asked the user to do (run a script or command, apply a migration, change a setting, load a credential,
answer a question) that the conversation does not show as done goes under Unblock. If its effect is cheap to check
(the migration exists, the variable is set by name, the file changed), check it and drop it if done; never read secret
values to check.

Anything waiting on a third party (a reply, an approval, a support ticket) goes to the backlog with who, what was
asked, when, and what to do once it arrives. If it has a deadline, it also goes under Unblock.

Files this session produced outside any repo that the user needs (scratchpad, `/tmp`, downloads, generated reports)
disappear or get lost: move them into the repo, or name their full path in the close-out.

Drop anything resolved later in the same conversation. Do not invent items to fill a section.

**Loose threads: ask, in as few rounds as fit.** After reading the repo's current `STATUS.md` and backlog, go through the conversation
again for threads that fit none of the lists above and are not already recorded: an analysis or proposal you made that
the user never answered, an idea the user floated and nobody followed up, a question left hanging, a topic dropped
when the conversation moved on. You cannot tell on your own whether the user still wants these, so do not drop them
silently and do not file them by default. Ask one question per thread (the harness's question UI), with your
recommendation first among backlog, Unblock and drop, and put as many questions in each round as the UI allows. If
there are more threads than fit, ask another round. If an answer opens a doubt (the user wants it but it is unclear
what exactly), ask a follow-up before filing it: a vague backlog item is as useless as a lost one. File what the user
keeps, drop the rest, and continue. If there are no loose threads, do not ask.

**If the conversation was compacted, or the context is above roughly 80% full** (the close-out itself could trigger a
compaction, and early turns are easy to miss in a very long context), read the full transcript before
listing anything: requests, decisions and pending work from the early part are exactly what a summary loses. Use the
harness's own way to read or search the session's transcript; in Claude Code CLI it is the session's `.jsonl` under
`~/.claude/projects/<project>/`, in Codex the rollout under `~/.codex/sessions/`. Do not load it into your own context,
which is already full: if the harness has subagents, hand the transcript to one on a cheaper model and ask it for the
list only (requests to the user, pending work, unblock items, decisions, each with where it appears), reading in
chunks. Without subagents, read it in chunks yourself and keep only the items, not the text. If it cannot be read, say
so in the close-out and recommend keeping the session instead of archiving.

## 2. Persist it in the repo

Skip this step only if nothing the session touched lives in a repo. Resolve symlinks before deciding: a file under a
config folder (`~/.claude/scripts`, `~/.codex`) may link into a repo. Resolve it and find the owning Git root before
choosing where project work belongs. If the installed skill is a standalone file outside Git, do not treat the
skill installation directory as the project repo or write project handoff data there.

### 2a. Choose the project's task store

For each affected repository, check whether Beads is configured there (for example, a `.beads/` directory and a
working `bd` project context). The presence of the `bd` executable alone does not mean this repository uses Beads.

- **When Beads is configured:** inspect existing beads and create or update beads for actionable pending work,
  including concrete follow-up derived from supported session observations. Search for duplicates first. Preserve
  source context (session date/title and, when useful, session ID) without embedding unnecessary transcript text.
  Keep `STATUS.md` as the short current-session view; link to bead IDs where useful. Do not duplicate the entire
  backlog into `STATUS.md`.
- **When Beads is absent:** use the repository's established backlog (`BACKLOG.md`, `backlog.md`, issues, or its
  documented equivalent). If none exists, create a short `BACKLOG.md` with one line per pending item.
- **When store configuration is uncertain:** do not initialize Beads or install tooling during close-out. Use the
  existing repository backlog if present; otherwise record the uncertainty as an Unblock and ask the user only if
  choosing a store would change repository policy.

- Pending work goes to the selected task store above. In Beads projects, persist actionable items as beads; in
  other projects, use the existing backlog format. If the repo has no task store, create a short `BACKLOG.md`.
  `STATUS.md` never holds the pending list; if an older `STATUS.md` still has a pending section, move its items to the
  backlog and drop the section.
- Durable decisions go where the repo keeps them (`AGENTS.md`, decision log, backlog notes). Ask only if it would
  change repo rules.
- Rewrite `STATUS.md` at the repo root whole, merging with what is already there (keep still-valid items from earlier
  sessions, remove what is done). Default layout:

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

Empty sections say `Nothing.` Make it as long as it needs to be, with urgent items first. It is not a copy of the backlog: details belong there.

Prefix with `[PRIORITY]` the items that should not wait past this week (money at risk, a deadline, something blocking
other work), at most 3 per repo, and remove the mark once it no longer applies. A status page can surface them first.

Keep each item in that shape (what it is, the recommendation, the options or the how, the source conversation): the
status page splits items on those markers.

- Commit following the user's git policy (or one commit for the close-out if they have none), in every repo the
  session touched. Push where that policy allows it and check the CI result; a failed CI goes under Unblock. Never
  push a production repo from here; list it under Unblock instead, with how many commits are waiting.

## 3. Close-out

The summary is 3 to 5 lines: what was done (one line), what to test, what to unblock, and anything to review. Use the
user's language, no headers. Steps 4 and 5 add at most one line each (the archive recommendation, the page refresh);
the whole close-out never goes beyond that.

Before printing, check that every test or unblock line in the summary matches an item in `STATUS.md` (one direction
only: `STATUS.md` may hold older items the summary leaves out). If a line has no item, add it to `STATUS.md` and
commit; never drop it from the summary to make them match.

## 4. Archive recommendation

First check what this session left running, by looking, not from memory: background shells and dev servers it
started (and the ports it used), scheduled wakeups, loops or cron jobs it created, subagents or side sessions still
working, worktrees with work not merged anywhere. Stop what is this session's own and no longer needed; anything that
must stay (a scheduled job, a side session) goes in the close-out. Never stop something another session started:
mention it in one line.

Recommend archiving or keeping the session, in one line with the reason:
- **Archive** when everything open is persisted in the repo and nothing is running or uncommitted. The session's
  context lives on in `STATUS.md` (including the next-session prompt), so a fresh session can pick it up.
- **Keep** when work is still running, something is uncommitted (or unpushed outside a production repo), or the next
  step depends on context that did not fit in the repo (say what).

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
