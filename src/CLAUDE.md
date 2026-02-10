# Global Claude Code User Preferences

This file contains global user preferences that apply to all Claude Code sessions across all projects.

## Important Instructions

- Be concise and direct in responses
- Focus on implementation over explanation unless asked
- Minimize output tokens while maintaining quality
- Avoid unnecessary preambles or postambles
- In planning mode, always end by writing out your plans to PLANNING.md and TASKS.md in the project working directory


## Code Style Preferences

- Follow existing project conventions and patterns
- Prioritize readability and maintainability
- Use descriptive variable and function names
- Keep functions focused and single-purpose

## Development Workflow

- Always use the TodoWrite tool for complex multi-step tasks
- Search thoroughly before implementing changes
- Test changes when possible
- Run linting and type checking when available
- Don't commit and push right away. I want to review things first.

## Git Worktree Workflow

This user prefers git worktrees for feature branch development.

### Preferences

- Always use worktrees when creating features in projects that support it
- Set `SPECKIT_USE_WORKTREES=true` in shell (see ~/.zshrc)
- Use `/git-worktree` skill for manually creating worktrees for existing branches

### Directory Structure

Feature branches are created as sibling directories to the main worktree:

```
~/<project>/
├── main/                          # Main worktree
├── JIRA-123-feature-name/        # Feature worktree
└── JIRA-456-another-feature/     # Another feature worktree
```

### Benefits

- Work on multiple features simultaneously without context switching
- Each worktree has its own working directory and checked-out branch
- Main branch always clean and ready for quick fixes
- Shared .git directory means fetch/push operations are synchronized

## Tool Usage

- Prefer Grep/Glob over manual file navigation
- Batch multiple independent operations when possible
- Use Task tool for open-ended searches
- Always read files before editing them

## Safety and Best Practices

- Never expose or log sensitive information
- Always validate inputs and handle errors appropriately
- Create backups before destructive operations
- Test configuration changes carefully

---

Note: This file is symlinked to ~/.claude/CLAUDE.md and applies to all Claude Code sessions.