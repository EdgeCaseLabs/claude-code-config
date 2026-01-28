---
description: "Enable .env file security protection in hooks"
argument-hint: ""
---

# Enable .env Security Protection

Removes the `.allow-env` file from `~/.claude/hooks/` to re-enable the security feature that blocks access to .env files.

When .env security is enabled:
- Claude Code cannot read, edit, or write .env files
- Pre-tool-use hook will block .env file access
- Protects sensitive environment variables from exposure

Use `/feature:disable-env-security` to disable protection.

---

I'll enable .env security by removing the allow-env flag file.
