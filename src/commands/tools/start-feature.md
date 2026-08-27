---
description: "Start a new feature: fetch a Jira or Mira ticket, create a git worktree, and open a cmux workspace"
argument-hint: "<TICKET> — Jira (e.g. TEX-448) or Mira (e.g. TEXOMA-273)"
---

# Start Feature Workflow

Set up a full development environment for a ticket: git worktree + cmux workspace.

> **Sandboxed variant:** [`/tools:start-feature-sbx`](./start-feature-sbx.md) runs the agent inside a
> Docker Sandbox (`sbx`) instead of on the host — one sandbox per branch, its own docker daemon and
> Supabase stack, host services unreachable. Steps 1–4 below are shared; it swaps the cmux tail for
> `sbx create` + bootstrap. Use this file for host-side work, that one for isolation.

## Tracker Detection

Two trackers are supported. Pick one from the ticket key prefix:

| Prefix | Tracker | Summary source |
|---|---|---|
| `TEXOMA-<n>` | **Mira** | `mcp__plugin_mira_mira__mira_get_card` |
| anything else (e.g. `TEX-<n>`) | **Jira** | `acli jira workitem view` |

Everything after Step 2 is tracker-agnostic — the branch name, worktree, and cmux setup use the
ticket key and summary the same way regardless of source.

**Key approach:** All logic is written to a single shell script file first, then executed with one
clean `bash /tmp/start-feature.sh` call. This avoids `$()` substitution in the Bash tool invocation,
so the permission can be remembered.

## Step 1: Validate Input

The user must provide a ticket key as an argument — Jira (e.g. `TEX-448`) or Mira (e.g. `TEXOMA-273`).
If not provided, ask for it. Determine the tracker from the prefix per the table above.

## Step 2: Fetch Ticket Info

Fetch the summary AND search for existing branches **in parallel** — one message, both calls.

**Summary — Jira tickets:**

```bash
acli jira workitem view TEX-448 --json | python3 -c "import json,sys; print(json.load(sys.stdin)['fields']['summary'])"
```

**Summary — Mira tickets (`TEXOMA-*`):** call the MCP tool instead of a shell command.

```
mcp__plugin_mira_mira__mira_get_card({ card: "TEXOMA-273", history: false })
```

Take the card **title** as the summary. If the tool errors with an unknown card, stop and tell the
user the card does not exist on the board — do NOT fall back to `acli`.

**Branch search (both trackers, same call):**

```bash
git -C /Users/wthomas/code/texoma/main fetch --prune origin 2>/dev/null; git -C /Users/wthomas/code/texoma/main branch -a | grep -i "TEX-448"
```

Grep for the full ticket key. Note `TEX-` is a prefix of nothing else, but `TEXOMA-273` must be
grepped as `TEXOMA-273` — grepping `TEX` alone would match every Jira branch on the repo.

## Step 3: Determine Branch Name

**This step is critical — always check for existing branches before deriving a name from the summary.**

Analyze the branch search results:

- **No matches** → derive the branch name from the ticket summary:
  - Lowercase the summary
  - Replace non-alphanumeric characters with hyphens
  - Collapse consecutive hyphens, strip leading/trailing hyphens
  - **Drop common English stopwords** so the remaining words carry meaning. Also drop words that are 2 chars or shorter (unless they're part of an identifier like a ticket prefix).
  - **Keep only the first 4 remaining meaningful words** (keeps branch names short and readable). Prefer nouns, verbs, and domain terms (product names, technologies, feature names). If filtering leaves fewer than 4 words, keep what remains.
  - Prepend the ticket key: `<TICKET>-<slug>`
  - Example: summary `"FeatBit: base Texoma migration targeting on segment membership instead of user property"` → candidates after stopword filter: `featbit, base, texoma, migration, targeting, segment, membership, user, property` → first 4: `featbit-texoma-migration-segment` (skip weak filler like "base"). Result: `TEX-535-featbit-texoma-migration-segment`. Use judgment on a per-summary basis.

- **Exactly one match** → use that existing branch name (strip the `remotes/origin/` prefix if present).
  Do NOT create a new branch name from the summary.

- **Multiple matches** → show the list to the user and ask which branch to use before proceeding.

The ticket summary is only a fallback for naming when no branch exists yet.

## Step 4: Claim the Ticket

Move the ticket to **in progress** — but only when it is yours to move. Assignment decides:

| Current assignee | Action |
|---|---|
| **You** | Set status to in progress. Leave assignee alone. |
| **Nobody** | Assign to yourself, **then** set status to in progress. |
| **Someone else** | Do nothing. Leave assignee and status untouched. Tell the user who owns it and carry on with the worktree setup. |

Never reassign a ticket away from another person. Never transition a ticket you do not own.

Also skip the status change (but still report) if the ticket is already in a further-along state —
`in_review`, `done`, `blocked`, or `cancelled` on Mira; the Jira equivalents. Only `backlog` / `todo`
(Jira: `To Do`, `Backlog`, `Open`) should be pulled forward.

### Mira (`TEXOMA-*`)

`mira_get_card` from Step 2 already returned the `assignee` and `status` — no second read needed.
Compare its assignee against `mira_whoami` (or just the git identity, which is what Mira uses).

Assigned to you, needs moving:

```
mcp__plugin_mira_mira__mira_update_card({
  card: "TEXOMA-273",
  status: "in_progress",
  branch: "TEXOMA-273-enrollment-dedup-termed-row",
  comment: "Started — worktree created via /tools:start-feature"
})
```

Unassigned — claim it in the same call:

```
mcp__plugin_mira_mira__mira_update_card({
  card: "TEXOMA-273",
  assignee: "me",
  status: "in_progress",
  branch: "TEXOMA-273-enrollment-dedup-termed-row",
  comment: "Started — worktree created via /tools:start-feature"
})
```

Setting `branch` links the card to the worktree branch so later `mira_link_pr` / board views line up.

### Jira

Test ownership with JQL rather than parsing `fields.assignee` — Jira redacts `emailAddress`, so
`accountId` comparison is fragile. An empty `[]` result means false:

```bash
acli jira workitem search --jql "key = TEX-448 AND assignee = currentUser()" --json
```

```bash
acli jira workitem search --jql "key = TEX-448 AND assignee IS EMPTY" --json
```

Then, matching the table:

```bash
acli jira workitem assign --key "TEX-448" --assignee "@me"
```

```bash
acli jira workitem transition --key "TEX-448" --status "In Progress" --yes
```

If the transition is rejected because `In Progress` is not reachable from the current status, do not
retry with a guessed status name — report it and move on.

## Step 5: Write the Script

Use the **Write tool** to create `/tmp/start-feature.sh` with all values hardcoded:

```bash
#!/usr/bin/env bash
set -euo pipefail

TICKET="TEX-448"
BRANCH="TEX-448-navigator-suggestions-in-human-mode-rooms"
MAIN_DIR="/Users/wthomas/code/texoma/main"
WORKTREE_DIR="/Users/wthomas/code/texoma/TEX-448-navigator-suggestions-in-human-mode-rooms"
# Tells the Claude pane where to read the ticket from. Set per tracker:
#   Jira  -> "in Jira"
#   Mira  -> "in Mira (use the mira_get_card MCP tool)"
TRACKER_HINT="in Jira"

echo "Setting up feature environment for $TICKET..."

# Create worktree
if [ -d "$WORKTREE_DIR" ]; then
  echo "Worktree already exists at $WORKTREE_DIR"
elif git -C "$MAIN_DIR" branch --list "$BRANCH" | grep -q .; then
  echo "Branch exists locally, creating worktree..."
  git -C "$MAIN_DIR" worktree add "$WORKTREE_DIR" "$BRANCH"
elif git -C "$MAIN_DIR" branch -r --list "origin/$BRANCH" | grep -q .; then
  echo "Branch exists on remote, creating worktree with tracking..."
  git -C "$MAIN_DIR" worktree add --track -b "$BRANCH" "$WORKTREE_DIR" "origin/$BRANCH"
else
  echo "Creating new branch and worktree..."
  git -C "$MAIN_DIR" worktree add -b "$BRANCH" "$WORKTREE_DIR"
fi

# Create cmux workspace (pane 1: claude --verbose in main worktree)
# new-workspace returns "OK workspace:N" — resolve to stable UUID via list-workspaces
echo "Creating cmux workspace..."
WORKSPACE_REF=$(cmux new-workspace --cwd "$MAIN_DIR" --command "claude --verbose --name $BRANCH" | awk '{print $NF}')
WORKSPACE_UUID=$(cmux --id-format both list-workspaces | grep "^[* ]*${WORKSPACE_REF} " | grep -oiE '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}')
cmux rename-workspace --workspace "$WORKSPACE_UUID" "$BRANCH"
LAST_INDEX=$(cmux list-workspaces | wc -l | tr -d ' ')
cmux reorder-workspace --workspace "$WORKSPACE_UUID" --index "$LAST_INDEX"

# Copy env files and local settings from main worktree
echo "Copying env files and local settings..."
for f in .env .env.test; do
  [ -f "$MAIN_DIR/$f" ] && cp "$MAIN_DIR/$f" "$WORKTREE_DIR/$f" && echo "  Copied $f"
done
[ -f "$MAIN_DIR/supabase/functions/.env" ] && cp "$MAIN_DIR/supabase/functions/.env" "$WORKTREE_DIR/supabase/functions/.env" && echo "  Copied supabase/functions/.env"
[ -f "$MAIN_DIR/scripts/.env" ] && cp "$MAIN_DIR/scripts/.env" "$WORKTREE_DIR/scripts/.env" && echo "  Copied scripts/.env"
[ -f "$MAIN_DIR/azure-functions/.env" ] && cp "$MAIN_DIR/azure-functions/.env" "$WORKTREE_DIR/azure-functions/.env" && echo "  Copied azure-functions/.env"
mkdir -p "$WORKTREE_DIR/.claude"
[ -f "$MAIN_DIR/.claude/settings.local.json" ] && cp "$MAIN_DIR/.claude/settings.local.json" "$WORKTREE_DIR/.claude/settings.local.json" && echo "  Copied .claude/settings.local.json"

# Add pane 2: terminal in feature worktree
PANE_REF=$(cmux new-pane --direction right --workspace "$WORKSPACE_UUID" | grep -oE 'pane:[0-9]+' | tail -1)
SURFACE_REF=$(cmux list-pane-surfaces --workspace "$WORKSPACE_UUID" --pane "$PANE_REF" | grep -oE 'surface:[0-9]+' | tail -1)
cmux send --workspace "$WORKSPACE_UUID" --surface "$SURFACE_REF" "cd $WORKTREE_DIR"$'\n'

# Send rename + initial context to Claude pane (pane 1)
# List all surfaces in the workspace, grab the first one (Claude's pane)
CLAUDE_SURFACE=$(cmux list-pane-surfaces --workspace "$WORKSPACE_UUID" | grep -oE 'surface:[0-9]+' | head -1)
sleep 5  # Give Claude time to start up before sending
cmux send --workspace "$WORKSPACE_UUID" --surface "$CLAUDE_SURFACE" "/rename $BRANCH"$'\n'
sleep 5
cmux send --workspace "$WORKSPACE_UUID" --surface "$CLAUDE_SURFACE" "/speckit.specify Read $TICKET $TRACKER_HINT and let's plan it out. Work back and forth with me, starting with your open questions and outline before writing the plan. You are in worktree $WORKTREE_DIR. All your reading and changes should go there unless otherwise directed."

echo ""
echo "Feature environment ready!"
echo "  Ticket:   $TICKET"
echo "  Branch:   $BRANCH"
echo "  Worktree: $WORKTREE_DIR"
echo "  cmux:     workspace \"$BRANCH\" (pane 1: claude --verbose --name $BRANCH, pane 2: terminal)"
```

For the `MAIN_DIR`, use the **first line** of `git worktree list` output (the main worktree path).
The worktree parent dir is one level up from `MAIN_DIR`.

## Step 6: Execute the Script

Run the script with a single clean bash invocation (no `$()` — permission is rememberable):

```bash
bash /tmp/start-feature.sh
```

## Step 7: Confirm

Report the script output to the user, plus one line on what Step 4 did to the ticket — one of:

- `Ticket: TEXOMA-273 → in progress (already yours)`
- `Ticket: TEXOMA-273 → assigned to you, in progress`
- `Ticket: TEX-448 left alone — assigned to Ian Evans`
- `Ticket: TEX-448 left alone — already In Review`

## Error Handling

- If `acli` is not authenticated (Jira tickets): `Run 'acli jira auth' to authenticate first`
- If the Mira MCP server is unavailable or `mira_get_card` returns no such card (`TEXOMA-*` tickets):
  stop and report it. Do not silently fall through to Jira — the key spaces are distinct.
- If not inside a git repo: `Must be run from inside a git repository`
- If the worktree directory already exists: warn and skip worktree creation (cmux setup still runs)
- If `cmux` is not running: `cmux is not running — open cmux first`
- If multiple branches match the ticket: **stop and ask the user** which branch to use before continuing
- If the Step 4 claim fails (transition rejected, assign denied, MCP error): report it and **continue**
  with the worktree + cmux setup. A ticket-tracker hiccup should not block the dev environment.
