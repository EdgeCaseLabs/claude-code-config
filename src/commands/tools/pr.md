---
description: "Commit all changes and create a pull request with auto-generated summary"
argument-hint: "[commit message] | (no args for auto-generated message)"
---

# Commit Changes and Create Pull Request

Follow these steps to commit staged/unstaged changes and create a PR:

## Step 1: Analyze Changes

1. Run `git status` to see all modified and untracked files
2. Run `git diff --stat` to understand the scope of changes
3. Run `git log --oneline -5` to see recent commit style

## Step 2: Stage and Commit

1. Stage all changes with `git add -A`
2. If the user provided a commit message argument, use it. Otherwise, analyze the changes and generate a concise commit message that:
   - Starts with a verb (Add, Fix, Update, Refactor, etc.)
   - Summarizes the main change in the first line (50 chars max)
   - Optionally includes bullet points for multiple changes
3. Commit with the message, including the Claude Code signature:

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Step 3: Push and Create PR

1. Check if the branch has a remote tracking branch with `git status`
2. Push with `git push -u origin <branch-name>` if needed
3. Create PR using `gh pr create` with:
   - A clear title summarizing the feature/fix
   - A body containing:
     - `## Summary` - bullet points of main changes
     - `## Test plan` - checklist of manual testing steps
     - The Claude Code signature

## Important Notes

- Never force push or amend commits that aren't yours
- If there are no changes to commit, inform the user
- If already on main/master, warn the user before proceeding
- Include all relevant file changes in the PR description
