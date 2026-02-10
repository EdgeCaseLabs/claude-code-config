---
name: git-worktree
description: /git-worktree - Create a git worktree (OPTIONAL workflow)
user_invocable: true
---

# Git Worktree Skill (Optional)

**Note**: This skill is for users who prefer git worktree workflows. Traditional branch workflows work fine too.

This skill creates a git worktree for a specified branch in a parallel directory, allowing you to work on multiple branches simultaneously without switching contexts.

**When to use:**
- You want to work on multiple features simultaneously
- You prefer separate directories for each branch
- You've set `SPECKIT_USE_WORKTREES=true` in your environment

**Alternative**: Use traditional `git checkout -b` workflow (default in create-new-feature.sh)

## Usage

Invoke this skill with:
```
/git-worktree <branch-name>
```

Or simply:
```
/git-worktree
```
Then Claude will ask for the branch name.

## What it does

1. **Validate branch**: Checks if the branch exists locally or remotely
2. **Create worktree**: Creates a new worktree in `../<branch-name>` directory
3. **Provide feedback**: Shows the created worktree path and next steps

## Implementation

When invoked, execute these steps:

### Step 1: Get the branch name

If the branch name is provided as an argument, use it. Otherwise, ask the user:
```
What branch would you like to create a worktree for?
```

### Step 2: Verify the branch exists

Check if the branch exists locally or remotely:

```bash
# Check if branch exists locally
git branch --list "<branch-name>"

# If not found locally, check remote
git branch -r --list "origin/<branch-name>"

# Fetch latest branches if needed
git fetch origin
```

### Step 3: Create the worktree

Create the worktree in the parent directory with the branch name as the directory name:

```bash
git worktree add ../<branch-name> <branch-name>
```

If the branch doesn't exist locally but exists on remote:
```bash
git worktree add ../<branch-name> origin/<branch-name>
```

If the branch doesn't exist at all, offer to create it:
```bash
git worktree add -b <branch-name> ../<branch-name>
```

### Step 4: Provide feedback

After creating the worktree, inform the user:

```
✅ Worktree created successfully!

Location: ../<branch-name>
Branch: <branch-name>

To switch to this worktree:
cd ../<branch-name>
```

## Directory Structure

Given a main repo at `/Users/user/code/my-project/main`, the worktree will be created at:
```
/Users/user/code/my-project/
├── main/                    # Main worktree
└── <branch-name>/          # New worktree
```

## Error Handling

- If the directory already exists, inform the user and ask if they want to use a different name
- If git worktree command fails, show the error message
- If not in a git repository, inform the user they must be in the main directory
- If the branch name is invalid, ask for a valid name

## Notes

- Worktrees share the same .git directory, so operations like fetch/push affect all worktrees
- Each worktree maintains its own working directory and can be on different branches
- Worktrees are ideal for working on features while keeping main clean for quick fixes
- To list all worktrees: `git worktree list`
- To remove a worktree: `git worktree remove <path>`

## Common Workflows

**Create worktree for existing remote branch:**
```
/git-worktree JIRA-123-feature-name
```

**Create worktree for new branch:**
If the branch doesn't exist, Claude will offer to create it when making the worktree.

**Switch between worktrees:**
```bash
cd ../JIRA-123-feature-name
# Work on feature...
cd ../main
# Quick fix on main...
```
