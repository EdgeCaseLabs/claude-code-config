---
description: "Start a new feature: fetch a Jira ticket, create a git worktree, and open a cmux workspace"
argument-hint: "<JIRA-TICKET> (e.g. TEX-448)"
---

# Start Feature Workflow

Set up a full development environment for a Jira ticket: git worktree + cmux workspace.

**Key approach:** All logic is written to a single shell script file first, then executed with one
clean `bash /tmp/start-feature.sh` call. This avoids `$()` substitution in the Bash tool invocation,
so the permission can be remembered.

## Step 1: Validate Input

The user must provide a Jira ticket key as an argument (e.g. `TEX-448`). If not provided, ask for it.

## Step 2: Fetch Ticket Info

Run both commands in parallel — get the Jira summary AND search for existing branches at the same time:

```bash
acli jira workitem view TEX-448 --json | python3 -c "import json,sys; print(json.load(sys.stdin)['fields']['summary'])"
```

```bash
git -C /Users/wthomas/code/texoma/main fetch --prune origin 2>/dev/null; git -C /Users/wthomas/code/texoma/main branch -a | grep -i "TEX-448"
```

## Step 3: Determine Branch Name

**This step is critical — always check for existing branches before deriving a name from the summary.**

Analyze the branch search results:

- **No matches** → derive the branch name from the Jira summary:
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

The Jira summary is only a fallback for naming when no branch exists yet.

## Step 4: Write the Script

Use the **Write tool** to create `/tmp/start-feature.sh` with all values hardcoded:

```bash
#!/usr/bin/env bash
set -euo pipefail

TICKET="TEX-448"
BRANCH="TEX-448-navigator-suggestions-in-human-mode-rooms"
MAIN_DIR="/Users/wthomas/code/texoma/main"
WORKTREE_DIR="/Users/wthomas/code/texoma/TEX-448-navigator-suggestions-in-human-mode-rooms"

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
sleep 1
cmux send --workspace "$WORKSPACE_UUID" --surface "$CLAUDE_SURFACE" "❯ /speckit.specify Read $TICKET and let's plan it out. You are in worktree $WORKTREE_DIR. All your reading and changes should go there unless otherwise directed."

echo ""
echo "Feature environment ready!"
echo "  Ticket:   $TICKET"
echo "  Branch:   $BRANCH"
echo "  Worktree: $WORKTREE_DIR"
echo "  cmux:     workspace \"$BRANCH\" (pane 1: claude --verbose --name $BRANCH, pane 2: terminal)"
```

For the `MAIN_DIR`, use the **first line** of `git worktree list` output (the main worktree path).
The worktree parent dir is one level up from `MAIN_DIR`.

## Step 5: Execute the Script

Run the script with a single clean bash invocation (no `$()` — permission is rememberable):

```bash
bash /tmp/start-feature.sh
```

## Step 6: Confirm

Report the output to the user.

## Error Handling

- If `acli` is not authenticated: `Run 'acli jira auth' to authenticate first`
- If not inside a git repo: `Must be run from inside a git repository`
- If the worktree directory already exists: warn and skip worktree creation (cmux setup still runs)
- If `cmux` is not running: `cmux is not running — open cmux first`
- If multiple branches match the ticket: **stop and ask the user** which branch to use before continuing
