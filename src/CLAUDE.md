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