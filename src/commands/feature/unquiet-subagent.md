---
description: "Re-enable TTS announcements for subagent completions"
argument-hint: ""
---

# Disable Subagent Quiet Mode

Removes the `.quiet-subagent` file from `~/.claude/hooks/` to re-enable TTS announcements for subagent completions.

When subagent quiet mode is disabled:
- Subagent completion announcements will be spoken again
- All TTS functionality is restored for subagents

Use `/quiet-subagent` to disable subagent TTS announcements.

---

I'll disable subagent quiet mode by removing the quiet-subagent flag file.
