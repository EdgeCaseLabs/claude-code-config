---
description: "Merge the current branch's PR and optionally delete the branch"
argument-hint: "[PR number] | (no args to auto-detect from current branch)"
---

# Merge Pull Request and Cleanup

Follow these steps to merge a PR and clean up the branch:

## Step 1: Identify the PR

1. If a PR number was provided as an argument, use it
2. Otherwise, detect the PR for the current branch using `gh pr view --json number,state,title`
3. If no PR exists for this branch, inform the user and stop

## Step 2: Check PR Status

1. Verify the PR is open and mergeable using `gh pr view <number> --json mergeable,mergeStateStatus,state`
2. If there are merge conflicts or checks failing, inform the user and ask how to proceed
3. Show the PR title and number for confirmation

## Step 3: Merge the PR

1. Merge using `gh pr merge <number> --squash --delete-branch --subject "Merge branch '<branch-name>'"`
   - Use `--squash` to keep history clean
   - Use `--subject` to include the branch name in the merge commit
   - The `--delete-branch` flag will delete the remote branch automatically
2. If merge fails, show the error and suggest fixes

## Step 4: Local Cleanup

1. Switch to the main branch with `git checkout main` (or `master`)
2. Pull latest changes with `git pull`
3. Ask the user if they want to delete the local branch using AskUserQuestion:
   - "Delete local branch `<branch-name>`?"
   - Options: "Yes, delete it" / "No, keep it"
4. If yes, run from the main branch directory:
   - First: `git worktree remove <branch-name> -f` (force remove any worktree)
   - Then: `git delete-branch <branch-name>` (custom subcommand for final cleanup)

## Important Notes

- Never force merge without user confirmation
- Always pull main/master after merge to stay up to date
- Warn if trying to delete main/master branch
- Show the merged PR URL at the end for reference
