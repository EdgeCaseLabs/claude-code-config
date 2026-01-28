---
description: "Disable TTS announcements for subagent completions only"
argument-hint: ""
---

# Enable Subagent Quiet Mode

Creates a `.quiet-subagent` file in `~/.claude/hooks/` to disable TTS announcements for subagent completions while keeping other notifications active.

When subagent quiet mode is active:
- Subagent completion announcements will be silenced
- Other notifications (completion, user input requests) will still be spoken
- Only subagent TTS is disabled

Use `/unquiet-subagent` to re-enable subagent TTS announcements.

---

I'll enable subagent quiet mode by creating the quiet-subagent flag file.
