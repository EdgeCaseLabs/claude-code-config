---
description: "Disable TTS announcements for all active Claude Code sessions"
argument-hint: ""
---

# Enable Quiet Mode

Creates a `.quiet` file in `~/.claude/hooks/` to disable all TTS announcements across all active Claude Code sessions.

When quiet mode is active:
- No completion announcements will be spoken
- No notification sounds will be played
- All TTS functionality is silently disabled

Use `/unquiet` to re-enable TTS announcements.

---

I'll enable quiet mode by creating the quiet flag file.