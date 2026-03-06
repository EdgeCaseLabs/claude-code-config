---
name: obsidian
description: Capture notes, tasks, and ideas into an Obsidian vault using the official Obsidian CLI. Use when the user wants to save notes, capture tasks, search their vault, or manage content in Obsidian. Triggers on phrases like "add to obsidian", "save this as a note", "capture this", "add task to my notes", "search my notes", "log this", "remember this".
allowed-tools: [Bash]
---

# Obsidian CLI Skill

Use the official `obsidian` CLI to interact with the user's Obsidian vault. This replaces losing things in random text files.

## Prerequisites

1. Obsidian v1.12+ must be **installed and running** — the CLI communicates with the open app
2. CLI must be enabled: Obsidian → Settings → General → Command line interface → Enable
3. The `obsidian` binary is in PATH (Obsidian adds it automatically when enabled)

**Check if ready:**
```bash
obsidian version
obsidian vault   # shows active vault name and path
```

If Obsidian isn't running or CLI isn't enabled, tell the user and stop — the commands will fail.

## Vault Selection

By default, all commands target the **active vault** in the running Obsidian app.

For multiple vaults, add `vault="VaultName"` to any command:
```bash
obsidian create name="TODO" path="Tasks/" content="# Tasks\n\n" vault="MyVault"
obsidian tasks vault="MyVault"
obsidian search query="topic" vault="MyVault"
```

There is no persistent vault selection — ask the user for their vault name if they have multiple vaults.

## Vault Structure Convention

Use this layout (create folders if they don't exist):
```
vault/
├── Inbox/          # Quick captures — triage later
├── Tasks/
│   └── TODO.md     # Persistent task list
└── Daily Notes/    # Auto-managed by Obsidian
```

Create the tasks file if it doesn't exist:
```bash
obsidian create name="TODO" path="Tasks/" content="# Tasks\n\n" --silent
```

## Core Operations

### Quick Note Capture

Capture a thought or idea to Inbox:
```bash
# Create a new note with a title
obsidian create name="Note Title" path="Inbox/" content="# Note Title\n\ncontent here"

# With date prefix for ordering
obsidian create name="2026-03-06 Note Title" path="Inbox/" content="# Note Title\n\ncontent here"

# If you're not sure of a title, use a timestamp
obsidian create name="2026-03-06 Quick Capture" path="Inbox/" content="# Quick Capture\n\ncontent here"
```

### Task Management

Tasks are markdown checkboxes (`- [ ]`). There is no `task:create` command — add tasks by appending to a note.

```bash
# Add a task to Tasks/TODO.md
obsidian append file="TODO" content="- [ ] Task description"

# Add multiple tasks
obsidian append file="TODO" content="- [ ] First task\n- [ ] Second task"

# List incomplete tasks across vault
obsidian tasks todo

# List all tasks (done + todo)
obsidian tasks

# List tasks from today's daily note only
obsidian tasks daily

# Count tasks
obsidian tasks total

# Toggle a task done/undone — requires path:line reference
# First get line numbers via JSON output:
#   obsidian tasks todo format=json
# Then toggle using file + line from the "file" and "line" fields:
obsidian task ref="Tasks/TODO.md:3" toggle
```

### Daily Notes

Good for capturing time-sensitive notes, meeting thoughts, quick todos:
```bash
# Append to today's daily note (creates it if needed)
obsidian daily:append content="- [ ] Something to do today"

# Append a note/observation
obsidian daily:append content="\n## Meeting Notes\n\ncontent here"

# Read today's daily note
obsidian daily:read

# Open a specific day
obsidian daily:open date=2026-03-06
```

### Search

Find existing notes before creating duplicates:
```bash
# Full-text search
obsidian search query="keyword or phrase"

# Search with context (shows surrounding text)
obsidian search:context query="keyword"

# Search by tag
obsidian search query="[tag:meeting]"

# Search by property
obsidian search query="[status:active]"

# Limit results
obsidian search query="topic" limit=10

# JSON output for parsing
obsidian search query="topic" format=json
```

### Browse and Read

```bash
# List all files in vault
obsidian files

# List files in a specific folder
obsidian files folder=Inbox/

# List folder structure
obsidian folders format=tree

# Read a specific note
obsidian read file="Note Name"
obsidian read path="Inbox/2026-03-06 Note Title.md"
```

### Edit Existing Notes

```bash
# Append content to an existing note
obsidian append file="Note Name" content="Additional content"

# Prepend content (useful for adding to top of inbox notes)
obsidian prepend file="Note Name" content="New header"

# Move a note (automatically updates wikilinks)
obsidian move file="Draft Idea" to=Projects/

# Delete a note (goes to trash)
obsidian delete file="Old Note"
```

## Recommended Workflows

### "Remember this / save this idea"
1. Search first to see if a related note exists
2. If yes, append to it; if no, create in Inbox/
```bash
obsidian search query="related topic"
# Then either:
obsidian append file="Existing Note" content="\n\nNew thought: ..."
# Or:
obsidian create name="2026-03-06 New Idea" path="Inbox/" content="# New Idea\n\ncontent"
```

### "Add a task / I need to do..."
```bash
obsidian append file="TODO" content="- [ ] Task description"
```
Or for today-specific tasks:
```bash
obsidian daily:append content="- [ ] Task description"
```

### "What tasks do I have?"
```bash
obsidian tasks todo
```

### "What did I write about X?"
```bash
obsidian search query="X"
obsidian search:context query="X"
```

### "Brain dump" (long unstructured content)
Create a dated note in Inbox:
```bash
obsidian create name="2026-03-06 Brain Dump" path="Inbox/" content="# Brain Dump\n\n<content>"
```

## Output Formats

- `format=json` — machine-readable, use for parsing
- `format=md` — markdown list
- `format=tree` — hierarchical view
- `format=paths` — one path per line

## Error Handling

| Error | Solution |
|-------|----------|
| `connection refused` or command not found | Obsidian isn't running or CLI not enabled |
| `vault not found` | Run `obsidian vault` to see active vault |
| `file not found` | Note doesn't exist; create it first |
| `already exists` | Use `--overwrite` flag or `append` instead |

## Important Notes

- Obsidian **must be running** for any CLI command to work
- The CLI targets the **currently active vault** in Obsidian
- If the user has multiple vaults, they need to switch to the right one in Obsidian first
- Use `\n` for newlines in content strings
- Quote values with spaces: `name="My Note Title"`
