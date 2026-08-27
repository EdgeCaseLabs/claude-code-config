---
description: "Start a feature in a Docker Sandbox: fetch a Jira/Mira ticket, create a git worktree, create + bootstrap an sbx sandbox, and open a cmux workspace"
argument-hint: "<TICKET> — Jira (e.g. TEX-448) or Mira (e.g. TEXOMA-273)"
---

# Start Feature (Sandboxed)

Same workflow as [`/tools:start-feature`](./start-feature.md), except the agent runs **inside a
Docker Sandbox** (`sbx`) instead of on the host. One sandbox per branch, so several can run in
parallel. `/tools:start-feature` is untouched — use that one for host-side work.

Steps 1–4 (tracker detection, ticket fetch, branch resolution, ticket claim) are **identical to
`/tools:start-feature`** — follow that file for them, then run the driver below. Everything after
the ticket claim is handled by one script, so the Bash permission is rememberable.

## What the sandbox gets

| | |
|---|---|
| Mounts | worktree **rw**, the main repo's `.git` **rw**, `~/code/dotfiles` **ro** |
| Claude config | `agents`, `commands`, `hooks`, `rules`, `CLAUDE.md`, filtered `settings.json`, project memory pushed with `sbx cp -L`; skills via the shared `sbx skills` store |
| Env | mise + chezmoi (`remote=true`), zsh, the pinned supabase CLI, tool tier `minimal` (13 tools, ~20 s) or `full` |
| Its own | docker daemon, and therefore its own Supabase stack — **host services are not reachable** |

## Step 5: Run the driver

```bash
bash ~/.claude/scripts/sbx-start-feature.sh --ticket TEX-448 --branch TEX-448-some-slug --tracker-hint "in Jira"
```

Flags:

| Flag | Effect |
|---|---|
| `--tier full` | install every tool in the mise config (minus `npm:git-split-diffs`, `azure-cli`, which cannot build in-container) |
| `--resync` | reuse an existing sandbox: re-push config, re-run bootstrap. Use after editing anything in `~/.claude` |
| `--no-cmux` | skip the cmux workspace (testing) |

Not flags: **Supabase** is never started for you — open pane 2 (or `tex sbx shell`) and run
`supabase start` in there, against the sandbox's own docker daemon. The **template** image is
resolved automatically: `texoma-dev-sbx:latest` is used when it exists, otherwise a cold build.
Refresh it with `tex sbx template`.

`--tracker-hint` is what gets pasted into the sandboxed agent's opening prompt: `"in Jira"` for Jira
keys, `"in Mira (use the mira_get_card MCP tool)"` for `TEXOMA-*`.

The driver: creates/reuses the worktree → copies env files (`.env`, `.env.test`,
`supabase/functions/.env`, `scripts/.env`, `azure-functions/.env`, `.claude/settings.local.json`) →
creates the sandbox (named after the **worktree directory**, so `sbx-<BRANCH>` for a feature
worktree and `sbx-main` for the main one — mounts are fixed at creation, so the sandbox's identity
has to be the directory, not the branch checked out in it) → filters host-only hooks out of
`settings.json` → pushes config → runs the repo's `scripts/sbx/sbx-bootstrap.sh` inside, which
finishes by calling the personal `~/code/dotfiles/sbx-personal-bootstrap.sh` from the read-only
dotfiles mount → opens a cmux workspace `<BRANCH>-sbx` with pane 1 on the sandboxed agent and
pane 2 an **in-sandbox** shell in the worktree → prints a summary.

Everything sandbox-side goes through the repo's `tex` CLI (`tex sbx up`, `tex sbx claude`,
`tex sbx name`), invoked by absolute path from the worktree so it does not depend on PATH.

Both panes live inside the sandbox. Host-side work (the host Supabase stack, host
`docker compose`) needs a pane you open yourself; git push works from inside the sandbox via
the stored GitHub PAT.

## Step 6: Report

Report the driver summary plus the ticket-claim line, exactly as `/tools:start-feature` does.
Call out any of these if the summary shows them:

- `git remote: unusable here` — the sandbox has no working GitHub credential. Commits inside are
  fine, but pushes need a host pane. Normally the stored PAT covers this and the summary reads
  `git remote: SSH to HTTPS rewrite active (credential proven by fetch)` instead.
- `dropped N host-only hooks` — those hooks were removed from the sandbox's `settings.json`.

## First-run setup (once per machine)

1. **Anthropic key.** A fresh sandbox is not authenticated. Store the key once, globally — the proxy
   authenticates on the agent's behalf and the key never enters a sandbox filesystem:
   `echo "$ANTHROPIC_API_KEY" | sbx secret set anthropic`. Nothing to redo per sandbox.
2. **GitHub PAT (optional).** `sbx secret set github --password-stdin` lets the sandboxed agent push
   over HTTPS. Without it, SSH is blocked by the sandbox proxy and pushes must come from the host.
3. **The `tex` CLI.** `make bash-helpers` in the repo symlinks it onto your PATH. The driver calls
   `scripts/tex` by absolute path, so it works without this — but every command below needs it.
4. **Tailscale auth key (optional).** `tex sbx key` stores an ephemeral, reusable key in the login
   keychain and injects it into this worktree's sandbox; `make start` in-sandbox then brings the
   sidecar up and the dev server gets a tailnet URL. `tex sbx key --status` never prints the key.

## Afterwards: driving the sandbox

All from the worktree — the sandbox is resolved from your cwd, so there is no name to remember:

| | |
|---|---|
| `tex sbx claude --continue` | reattach the most recent session (`--resume <id>` for a specific one) |
| `tex sbx sessions` | list the sessions the sandbox holds: id, when, first prompt |
| `tex sbx shell` | shell inside it, in the worktree |
| `tex sbx status` | this worktree's sandbox plus every other one |
| `tex sbx save-history` | copy Claude transcripts + todo state out to the host |
| `tex sbx down` / `clean` | stop it / remove it (offers to save history first) |

Transcripts live on sandbox-managed volumes, so `tex sbx clean` destroys them — save first.

## Error handling

- `sbx` missing → install Docker Sandboxes; not signed in → `sbx login`.
- Sandbox already exists → the driver reuses it. **Mounts are fixed at creation**, so a mount change
  means removing the sandbox first.
- `git unusable in <worktree>` from the bootstrap → the main repo's `.git` was not mounted. A
  worktree's `.git` is only a pointer file into it; recreate the sandbox with that mount.
- Bootstrap failure → the driver stops and prints `sbx exec -it <sandbox> bash` to debug in place.
  Fix, then re-run with `--resync`.
- `cmux` not running → the driver warns and finishes; attach manually with the printed command.
- `repo sandbox tooling not found (expected scripts/tex)` → the worktree predates the `tex` CLI.
  Rebase it, or point `--main-dir` at a checkout that has it.
- Ticket-tracker failures (transition rejected, MCP error) → report and continue; a tracker hiccup
  must not block the environment.

## Known sandbox constraints (probed 2026-08-20)

- Host services (Supabase, Vite, Postgres) are **not** reachable from a sandbox — it has its own
  docker daemon. Either run `supabase start` in-sandbox or do DB work from a host pane you open.
- git over SSH is blocked (proxy closes port 22); HTTPS needs a stored credential.
- Mounts appear at their **host absolute paths** inside the sandbox (not `/host/home/...`).
- Symlinks pointing outside a mount dangle — that's why config is pushed rather than mounted.
