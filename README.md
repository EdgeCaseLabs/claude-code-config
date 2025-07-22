# Claude Code Configuration Repository

A centralized configuration management system for [Claude Code](https://claude.ai/code) settings and hooks, distributed globally via symlinks.

## Overview

This repository maintains a single source of truth for Claude Code configurations that can be shared across all projects. Instead of managing separate configurations in each project, this system creates symlinks from `~/.claude/` to this repository, ensuring consistent behavior everywhere.

> [!WARNING]
> **⚠️ IMPORTANT: Personal Configuration Alert ⚠️**
> 
> These are **MY PERSONAL** Claude Code settings. You will **DEFINITELY** want to customize them for your own use!
> 
> **Before using this repository:**
> 1. **READ** the `src/settings.json` file carefully
> 2. **REVIEW** all hook scripts in `src/hooks/`
> 3. **MODIFY** settings to match your preferences and security requirements
> 
> Using these settings as-is may not align with your workflow or security needs.

## Features

- **Global Configuration**: Single `src/settings.json` file with comprehensive tool permissions
- **Global User Memory**: `src/CLAUDE.md` for personal preferences that apply across all Claude Code sessions
- **Advanced Hook System**: Complete lifecycle management with Python-based hooks
- **Automated Setup**: Idempotent setup script with safety features
- **Centralized Management**: All changes apply immediately to all projects

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository-url> claude-code-config
   cd claude-code-config
   ./setup.sh
   ```

2. **Verify Setup**:
   ```bash
   ls -la ~/.claude/
   # Should show symlinks to this repository
   ```

That's it! Your Claude Code configuration is now globally active.

## Repository Structure

```
claude-code-config/
├── README.md              # This file
├── CLAUDE.md              # Claude Code project instructions
├── PLANNING.md            # Detailed implementation plan
├── TASKS.md               # Task breakdown and progress
├── setup.sh               # Setup script for symlink management
└── src/                   # Source directory
    ├── settings.json      # Main Claude Code configuration
    ├── CLAUDE.md          # Global user preferences (symlinked to ~/.claude/CLAUDE.md)
    └── hooks/             # Hook system directory
        ├── hook_logger.py     # Logging utilities
        ├── notification.py    # Notification system
        ├── pre_tool_use.py    # Pre-tool execution hooks
        ├── post_tool_use.py   # Post-tool execution hooks
        ├── stop.py            # Session stop hooks
        ├── subagent_stop.py   # Subagent management
        ├── logs/              # Hook execution logs
        └── utils/             # Utility modules
            ├── llm/           # LLM integrations
            └── tts/           # Text-to-speech utilities
```

## Configuration Details

### Settings (`src/settings.json`)

The main configuration file includes:

- **Tool Permissions**: Granular control over allowed commands
- **Hook Definitions**: Lifecycle hooks for various events
- **Security Settings**: Controlled access to system operations

### Hook System

One of the primary features of this hook system is **real-time notifications** - you'll receive audio and system notifications when Claude Code needs your input, when agents complete tasks, or when important events occur. This allows you to multitask effectively while Claude Code works in the background.

#### Hook Descriptions

| Hook | Purpose | What It Does |
|------|---------|--------------|
| `PreToolUse` | Pre-execution validation and safety | • Logs all tool executions to JSON files<br>• Blocks dangerous commands (e.g., `rm -rf /`)<br>• Validates inputs before execution<br>• Provides audit trail of all actions |
| `PostToolUse` | Post-execution processing | • Logs tool results and outputs<br>• Tracks execution times<br>• Records success/failure states<br>• Maintains detailed activity logs |
| `Notification` | Audio and system alerts | • Plays audio notifications for key events<br>• Shows macOS system notifications<br>• Alerts when user input is needed<br>• Notifies on task completion<br>• Uses ElevenLabs TTS for voice alerts |
| `Stop` | Session cleanup and archival | • Archives chat transcripts<br>• Performs session cleanup<br>• Saves conversation history<br>• Notifies when session ends |
| `SubagentStop` | Subagent lifecycle management | • Tracks subagent completion<br>• Logs subagent results<br>• Manages nested agent states<br>• Provides completion notifications |

#### Audio Notifications Setup (Optional)

The notification hooks support ElevenLabs text-to-speech for audio alerts when Claude Code needs your attention:

1. Get your API key from [ElevenLabs](https://elevenlabs.io/) after creating an account
2. Find available voice IDs in your ElevenLabs dashboard or use their API to list voices
3. Add the environment variables to your shell profile:
   ```bash
   echo 'export ELEVENLABS_API_KEY="your_api_key_here"' >> ~/.bash_profile
   echo 'export ELEVENLABS_VOICE_ID="your_voice_id_here"' >> ~/.bash_profile
   ```

4. Reload your shell profile:
   ```bash
   source ~/.bash_profile
   ```


**Note**: If you're using zsh (default on newer macOS), use `~/.zshrc` instead of `~/.bash_profile`. The hooks will still function without these variables but will show setup instructions instead of playing audio.

## Setup Script Usage

The `setup.sh` script provides flexible setup options:

```bash
# Basic setup
./setup.sh

# Dry run (see what would be done)
./setup.sh --dry-run

# Verbose output
./setup.sh --verbose

# Force overwrite existing configs
./setup.sh --force

# Show help
./setup.sh --help
```

### Setup Process

1. **Validation**: Checks that configuration files exist
2. **Backup**: Saves existing `~/.claude/` configurations
3. **Symlinking**: Creates symlinks to this repository
4. **Verification**: Validates symlink integrity
5. **Reporting**: Shows final configuration status

## Symlinks Created

| Target | Source | Purpose |
|--------|--------|---------|
| `~/.claude/settings.json` | `./src/settings.json` | Main configuration |
| `~/.claude/hooks/` | `./src/hooks/` | Hook system |
| `~/.claude/CLAUDE.md` | `./src/CLAUDE.md` | Global user preferences |

## Usage

### Making Configuration Changes

1. Edit `src/settings.json` in this repository
2. Changes apply immediately to all Claude Code sessions
3. No restart or re-setup required

### Editing Global User Preferences

1. Edit `src/CLAUDE.md` in this repository
2. This file contains your personal preferences that apply across all Claude Code sessions
3. Changes are immediate - no restart needed

### Adding New Hooks

1. Add Python script to `src/hooks/` directory
2. Update `src/settings.json` hook definitions
3. Test with `uv run ~/.claude/hooks/your-script.py`

### Managing Permissions

Tool permissions are defined in `src/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(command:*)",
      "Write",
      "Edit"
    ],
    "deny": []
  }
}
```

## Development

### Requirements

- Python 3.8+ (for hooks)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Bash (for setup script)

### Testing Changes

```bash
# Test configuration syntax
python -m json.tool src/settings.json

# Test hooks individually
cd ~/.claude
uv run src/hooks/pre_tool_use.py
```

### Hook Development

Hooks are Python scripts that can:
- Access environment variables
- Log to `src/hooks/logs/`
- Use utility modules in `src/hooks/utils/`
- Integrate with external services

Example hook structure:
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Hook logic here
def main():
    # Your hook implementation
    pass

if __name__ == "__main__":
    main()
```

## Troubleshooting

### Common Issues

**Hook Errors**: If you see "No such file or directory" for hooks:
```bash
# Re-run setup to ensure symlinks are correct
./setup.sh
```

**Permission Denied**: If setup fails with permissions:
```bash
chmod +x setup.sh
./setup.sh
```

**Broken Symlinks**: If symlinks point to wrong locations:
```bash
./setup.sh --force
```

**Debug Mode**: Put Claude Code into debug mode to observe more details
```bash
claude --debug
```

### Verification Commands

```bash
# Check symlink targets
readlink ~/.claude/settings.json
readlink ~/.claude/hooks
readlink ~/.claude/CLAUDE.md

# Test hook accessibility  
ls -la ~/.claude/hooks/
uv run ~/.claude/hooks/stop.py --help

# Validate configuration
python -m json.tool ~/.claude/settings.json
```

## Safety Features

- **Automatic Backups**: Existing configurations are backed up before changes
- **Dry Run Mode**: Test changes without applying them
- **Idempotent Setup**: Safe to run multiple times
- **Rollback Support**: Backups can be restored if needed


---

**Note**: Changes to this repository immediately affect all Claude Code sessions. Test carefully before committing changes.

---

_Inspired by https://github.com/disler/claude-code-hooks-mastery/_