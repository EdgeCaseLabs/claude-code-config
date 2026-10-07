#!/usr/bin/env python3
"""Jev model router for Claude Code.

Runs as a UserPromptSubmit hook. For each prompt it asks Jev (typesafe/jev-1.13
on OpenRouter) one question: what is the smallest model size that can do this
job well? When Jev is confident, it tells the main session to hand the job to
the matching helper agent (router-tiny / router-everyday / router-large /
router-hardest). Otherwise it stays silent and the main session handles it.

Fail-open by design: if the router is off, Jev is slow, the key is missing, or
anything at all raises, the hook exits 0 with no output and the prompt goes
through untouched.

One-time setup from a shell (copies the OpenRouter key from 1Password into
the macOS Keychain):  python3 ~/.claude/hooks/jev_router.py setup
Setup reads the 1Password location from JEV_OP_REFERENCE (op://vault/item/field)
and, optionally, JEV_OP_ACCOUNT (sign-in address).

Control words, typed as the whole message (handled here, never sent to Jev):
    router on       enable
    router off      disable
    router status   counts per size, routing decisions, Jev cost so far

Also usable from a shell:  python3 ~/.claude/hooks/jev_router.py on|off|status|forget
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone

STATE_DIR = os.path.expanduser("~/.claude/jev-router-state")
ENABLED_FLAG = os.path.join(STATE_DIR, "enabled")
LOG_FILE = os.path.join(STATE_DIR, "log.jsonl")

JEV_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_MODEL = "typesafe/jev-1.13"
JEV_TIMEOUT_SECONDS = 2.0
MAX_STATE_CHARS = 6000
CONFIDENCE_THRESHOLD = 0.60

KEYCHAIN_SERVICE = "jev-router"
KEYCHAIN_ACCOUNT = "openrouter"
# Org-specific 1Password location, kept out of this public repo. Set in your shell.
OP_REFERENCE = os.environ.get("JEV_OP_REFERENCE", "")  # op://<vault>/<item>/<field>
OP_ACCOUNT = os.environ.get("JEV_OP_ACCOUNT", "")  # optional, e.g. example.1password.com
OP_TIMEOUT_SECONDS = 8  # stays under the hook's 10s timeout in settings.json

# Smallest to biggest. Each size maps to one helper agent pinned to one model.
SIZES = {
    "tiny": {
        "criteria": "a lookup, a rename, a one-line answer",
        "agent": "router-tiny",
        "model": "claude-haiku-4-5",
    },
    "everyday": {
        "criteria": "a normal email, post or short document",
        "agent": "router-everyday",
        "model": "claude-sonnet-5",
    },
    "large": {
        "criteria": "a multi-step build, research, a full report",
        "agent": "router-large",
        "model": "claude-opus-5-5",
    },
    "hardest": {
        "criteria": "strategy, or anything where a wrong call is expensive",
        "agent": "router-hardest",
        "model": "claude-fable-5-1",
    },
}

# A short message leaning on earlier turns ("yes do that but shorter").
SHORT_REPLY_MAX_WORDS = 12
CONTEXT_CUES = re.compile(
    r"\b(yes|yeah|yep|yup|no|nope|ok|okay|sure|go ahead|do that|do it|that|this|"
    r"it|those|them|same|again|instead|shorter|longer|redo|retry|continue|"
    r"above|previous|last one)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------- state ----

def is_enabled():
    return os.path.exists(ENABLED_FLAG)


def append_log(entry):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_log():
    if not os.path.exists(LOG_FILE):
        return []
    entries = []
    with open(LOG_FILE) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue
    return entries


# ------------------------------------------------------------------ key ----

def keychain_read():
    result = subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE,
         "-a", KEYCHAIN_ACCOUNT, "-w"],
        capture_output=True, text=True, timeout=1.0,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def api_key():
    return os.environ.get("OPENROUTER_API_KEY") or keychain_read()


def fetch_key_from_1password():
    if not OP_REFERENCE:
        raise RuntimeError(
            "JEV_OP_REFERENCE is not set. Export it (and optionally JEV_OP_ACCOUNT), "
            "or set OPENROUTER_API_KEY instead."
        )
    command = ["op", "read", OP_REFERENCE]
    if OP_ACCOUNT:
        command += ["--account", OP_ACCOUNT]
    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        timeout=OP_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "op read failed")
    return result.stdout.strip()


def store_key(key):
    subprocess.run(
        ["security", "add-generic-password", "-U", "-s", KEYCHAIN_SERVICE,
         "-a", KEYCHAIN_ACCOUNT, "-w", key],
        check=True, capture_output=True, timeout=10,
    )


def delete_key():
    subprocess.run(
        ["security", "delete-generic-password", "-s", KEYCHAIN_SERVICE,
         "-a", KEYCHAIN_ACCOUNT],
        capture_output=True, timeout=10,
    )


# ------------------------------------------------------------------ jev ----

def ask_jev(prompt, key):
    """Return (size, confidence, probabilities, cost) from Jev."""
    body = {
        "model": JEV_MODEL,
        "state": prompt[:MAX_STATE_CHARS],
        "questions": {
            "size": {
                "type": "choice",
                "instructions": (
                    "What is the smallest AI model size that can do this job well?"
                ),
                "criteria": {name: s["criteria"] for name, s in SIZES.items()},
            }
        },
    }
    request = urllib.request.Request(
        JEV_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(request, timeout=JEV_TIMEOUT_SECONDS) as response:
        data = json.load(response)
    answer = data["answers"]["size"]
    size = answer["choice"]
    if size not in SIZES:
        raise ValueError(f"unexpected size {size!r}")
    cost = float(data.get("usage", {}).get("cost") or 0)
    return size, float(answer["confidence"]), answer.get("probabilities", {}), cost


def is_context_reply(prompt):
    words = prompt.split()
    return len(words) <= SHORT_REPLY_MAX_WORDS and bool(CONTEXT_CUES.search(prompt))


def decide(prompt, key):
    """Size one prompt. Returns a log entry describing the decision."""
    started = time.monotonic()
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "chars": len(prompt)}
    try:
        size, confidence, probabilities, cost = ask_jev(prompt, key)
    except Exception as exc:  # timeout, network, HTTP, bad JSON: fail open
        entry.update(route="self:jev-error", error=type(exc).__name__,
                     latency_ms=int((time.monotonic() - started) * 1000))
        return entry
    entry.update(size=size, confidence=round(confidence, 3), cost=cost,
                 probabilities=probabilities,
                 latency_ms=int((time.monotonic() - started) * 1000))
    if is_context_reply(prompt):
        entry["route"] = "self:context-reply"
    elif confidence < CONFIDENCE_THRESHOLD:
        entry["route"] = "self:low-confidence"
    else:
        entry["route"] = "helper:" + SIZES[size]["agent"]
    return entry


def routing_context(entry):
    size = entry["size"]
    agent = SIZES[size]["agent"]
    return (
        f"[jev-router] Jev sized this message as {size.upper()} "
        f"(confidence {entry['confidence']:.0%}). Hand the job to the "
        f"`{agent}` helper: call the Agent tool with subagent_type \"{agent}\", "
        "passing the user's message verbatim plus any conversation context the "
        "helper needs (file paths, earlier decisions, constraints). Relay the "
        "helper's result to the user. It must end with the line "
        f"'Model: {SIZES[size]['model']}'; add that line yourself if the helper "
        "left it out. If the Agent call fails, do the job yourself."
    )


# ------------------------------------------------------------- commands ----

SETUP_HINT = "! python3 ~/.claude/hooks/jev_router.py setup"


def cmd_setup():
    """Shell-only: copy the key from 1Password into the macOS Keychain.

    Not run from the hook: 1Password approves each process tree separately,
    so `op` inside a hook waits on a Touch ID prompt nobody sees.
    """
    store_key(fetch_key_from_1password())
    return "OpenRouter key stored in Keychain (service 'jev-router')."


def cmd_forget():
    delete_key()
    return "OpenRouter key removed from Keychain."


def cmd_on():
    if not api_key():
        return f"No OpenRouter key cached yet. Run this once, then retry:\n  {SETUP_HINT}"
    os.makedirs(STATE_DIR, exist_ok=True)
    open(ENABLED_FLAG, "w").close()
    return ("Jev router is ON. Every message now goes to Jev on OpenRouter "
            "(TypeSafe) for sizing. Say `router off` before private work.")


def cmd_off():
    if os.path.exists(ENABLED_FLAG):
        os.remove(ENABLED_FLAG)
    return "Jev router is OFF. Messages no longer leave this machine for sizing."


def cmd_status():
    entries = read_log()
    sized = [e for e in entries if "size" in e]
    sizes = Counter(e["size"] for e in sized)
    routes = Counter(e.get("route", "?") for e in entries)
    total_cost = sum(e.get("cost", 0) for e in entries)
    latencies = sorted(e["latency_ms"] for e in entries if "latency_ms" in e)
    median_ms = latencies[len(latencies) // 2] if latencies else 0

    lines = [
        f"Jev router: {'ON' if is_enabled() else 'OFF'}",
        f"Messages sized: {len(sized)}  (Jev failures/timeouts: "
        f"{routes.get('self:jev-error', 0)})",
        "",
        "Jev's pick per size:",
    ]
    for name, spec in SIZES.items():
        lines.append(f"  {name:<9} {sizes.get(name, 0):>4}   -> {spec['model']}")
    lines += [
        "",
        "Where messages went:",
        *[f"  {route:<26} {count:>4}" for route, count in sorted(routes.items())],
        "",
        f"Jev cost so far: ${total_cost:.6f}",
        f"Median Jev latency: {median_ms} ms",
    ]
    return "\n".join(lines)


COMMANDS = {"on": cmd_on, "off": cmd_off, "status": cmd_status}
SHELL_COMMANDS = {**COMMANDS, "setup": cmd_setup, "forget": cmd_forget}
CONTROL_PATTERN = re.compile(r"^\s*/?router\s+(on|off|status)\s*[.!]?\s*$",
                             re.IGNORECASE)


# ----------------------------------------------------------------- hook ----

def emit(payload):
    sys.stdout.write(json.dumps(payload))


def run_hook():
    try:
        prompt = json.load(sys.stdin).get("prompt", "") or ""
    except Exception:
        return

    control = CONTROL_PATTERN.match(prompt)
    if control:
        try:
            message = COMMANDS[control.group(1).lower()]()
        except Exception as exc:
            message = f"Jev router command failed: {exc}"
        emit({"decision": "block", "reason": message})
        return

    if not is_enabled() or not prompt.strip() or prompt.lstrip().startswith("/"):
        return
    key = api_key()
    if not key:
        return

    entry = decide(prompt, key)
    try:
        append_log(entry)
    except OSError:
        pass
    if entry["route"].startswith("helper:"):
        emit({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": routing_context(entry),
        }})


def main():
    if len(sys.argv) > 1:
        command = SHELL_COMMANDS.get(sys.argv[1].lower())
        if not command:
            print("usage: jev_router.py setup|on|off|status|forget")
            sys.exit(2)
        print(command())
        return
    try:
        run_hook()
    except Exception:
        pass  # never block or slow a prompt
    sys.exit(0)


if __name__ == "__main__":
    main()
