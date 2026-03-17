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

Run this to get the summary (this is a simple pipe with no `$()`, so it's rememberable):

```bash
acli jira workitem view TEX-448 --json | python3 -c "import json,sys; print(json.load(sys.stdin)['fields']['summary'])"
```

## Step 3: Write the Script

Use the **Write tool** to create `/tmp/start-feature.sh` with the full logic filled in using the
actual ticket key, branch name, and paths you've determined. The script should look like this
(substitute real values — do NOT use shell variables for the paths, hardcode them):

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

# Add pane 2: terminal in feature worktree
PANE_REF=$(cmux new-pane --direction right --workspace "$WORKSPACE_UUID" | awk '{for(i=1;i<=NF;i++) if($i~/^pane:/) print $i}')
SURFACE_REF=$(cmux list-pane-surfaces --workspace "$WORKSPACE_UUID" --pane "$PANE_REF" | awk '{print $2}' | tail -1)
cmux send --workspace "$WORKSPACE_UUID" --surface "$SURFACE_REF" "cd $WORKTREE_DIR"$'\n'

echo ""
echo "Feature environment ready!"
echo "  Ticket:   $TICKET"
echo "  Branch:   $BRANCH"
echo "  Worktree: $WORKTREE_DIR"
echo "  cmux:     workspace \"$BRANCH\" (pane 1: claude --verbose, pane 2: terminal)"
```

To build the branch slug from the summary, apply this transformation mentally:
- Lowercase the summary
- Replace any non-alphanumeric characters with hyphens
- Collapse consecutive hyphens
- Strip trailing hyphens
- Prepend the ticket key: `<TICKET>-<slug>`

For the `MAIN_DIR`, use the **first line** of `git worktree list` output (the main worktree path).
The worktree parent dir is one level up from `MAIN_DIR`.

## Step 4: Execute the Script

Run the script with a single clean bash invocation (no `$()` — permission is rememberable):

```bash
bash /tmp/start-feature.sh
```

## Step 5: Confirm

Report the output to the user.

## Error Handling

- If `acli` is not authenticated: `Run 'acli jira auth' to authenticate first`
- If not inside a git repo: `Must be run from inside a git repository`
- If the worktree directory already exists: warn and skip worktree creation (cmux setup still runs)
- If `cmux` is not running: `cmux is not running — open cmux first`
