---
description: "Disable .env file security protection in hooks"
argument-hint: ""
---

# Disable .env Security Protection

Creates a `.allow-env` file in `~/.claude/hooks/` to disable the security feature that blocks access to .env files.

When .env security is disabled:
- Claude Code can read, edit, and write .env files
- Pre-tool-use hook will not block .env file access
- **Warning:** This allows sensitive environment variables to be exposed

Use `/feature:enable-env-security` to re-enable protection.

---

I'll disable .env security by creating the allow-env flag file.
