# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository manages centralized Claude Code configurations and hooks that are shared across all projects via symlinks to `~/.claude/`.

## Architecture

- **Configuration Distribution**: Uses symlinks from this repo to `~/.claude/` to share settings globally
- **Primary Config**: `settings.json` will contain the main Claude Code configuration
- **Setup Automation**: A setup script will handle the symlinking process

## Setup Process

The intended workflow involves:
1. Creating a `src/settings.json` file with Claude Code configurations
2. Running a setup script that creates `~/.claude/settings.json` as a symlink to this repo's `src/settings.json`
3. This allows all projects to inherit the same Claude Code configuration

## Development Notes

This is a configuration management repository, not a traditional codebase. When working here:
- Changes to `src/settings.json` will immediately affect all projects using the symlinked configuration
- Test configuration changes carefully as they apply globally
- The setup script should be idempotent and handle existing symlinks gracefully