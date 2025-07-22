# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository manages centralized Claude Code configurations and hooks that are shared across all projects via symlinks to `~/.claude/`. It provides a single source of truth for Claude Code settings, global user preferences, and a comprehensive Python-based hook system for lifecycle management.

## Architecture

- **Configuration Distribution**: Uses symlinks from this repo to `~/.claude/` to share settings globally
- **Primary Config**: `src/settings.json` contains the main Claude Code configuration with tool permissions and hook definitions
- **Global User Memory**: `src/CLAUDE.md` provides user preferences that apply across all Claude Code sessions
- **Hook System**: Python-based hooks in `src/hooks/` handle various lifecycle events
- **Setup Automation**: `setup.sh` script handles symlink creation with multiple modes and safety features

## Directory Structure

```
claude-code-config/
├── setup.sh                 # Main setup script with install/remove/dry-run modes
├── src/
│   ├── settings.json       # Claude Code configuration file
│   ├── CLAUDE.md          # Global user preferences (symlinked to ~/.claude/CLAUDE.md)
│   └── hooks/              # Python hook implementations
│       ├── pre_tool_use.py     # Pre-execution validation and safety checks
│       ├── post_tool_use.py    # Post-execution processing
│       ├── notification.py     # System notifications
│       ├── stop.py            # Session cleanup and transcript management
│       ├── subagent_stop.py   # Subagent lifecycle management
│       ├── hook_logger.py     # Shared logging utilities
│       └── utils/             # Supporting utilities
│           ├── llm/           # LLM integrations (Anthropic, OpenAI)
│           └── tts/           # Text-to-speech utilities
└── logs/                   # Hook execution logs (JSON format)
```

## Setup Process

The setup workflow:
1. Run `./setup.sh` to create symlinks:
   - `~/.claude/settings.json` → `./src/settings.json`
   - `~/.claude/hooks/` → `./src/hooks/`
   - `~/.claude/CLAUDE.md` → `./src/CLAUDE.md`
2. Optional flags:
   - `--dry-run`: Preview changes without executing
   - `--force`: Overwrite existing symlinks
   - `--verbose`: Detailed output
   - `--remove`: Uninstall symlinks
3. The script validates paths, creates backups if needed, and verifies symlinks

## Hook System

All hooks are executed via `uv run` and triggered at specific events:
- **PreToolUse**: Validates tool inputs, blocks dangerous commands (e.g., `rm -rf` patterns)
- **PostToolUse**: Logs tool execution results
- **Notification**: Handles significant events
- **Stop**: Manages session cleanup and transcript archival
- **SubagentStop**: Handles subagent termination

## Development Notes

This is a configuration management repository. When working here:
- Changes to `src/settings.json` immediately affect all projects using the symlinked configuration
- Test configuration changes carefully as they apply globally
- The setup script is idempotent and handles existing symlinks gracefully
- Hook modifications take effect immediately for all Claude Code sessions
- Logs in the `logs/` directory track hook execution for debugging

## Safety Features

- Pre-tool-use hook includes dangerous command detection
- Setup script creates backups before overwriting
- Validation ensures correct symlink targets
- All hooks include error handling and logging