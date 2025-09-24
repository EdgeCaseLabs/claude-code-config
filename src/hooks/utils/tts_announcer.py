#!/usr/bin/env python3
"""
Centralized TTS announcement functionality for Claude Code hooks.
Provides a unified interface for all TTS operations across different hooks.
"""

import os
import random
import subprocess
from pathlib import Path
from hook_logger import setup_hook_logger, log_exception


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "tts"

    # Check for ElevenLabs API key (highest priority)
    if os.getenv('ELEVENLABS_API_KEY'):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check for OpenAI API key (second priority)
    if os.getenv('OPENAI_API_KEY'):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)

    return None


def get_completion_messages():
    """Return list of friendly completion messages."""
    return [
        "Work complete!",
        "All done!",
        "Task finished!",
        "Job complete!",
        "Ready for next task!"
    ]


def get_llm_completion_message():
    """
    Generate completion message using available LLM services.
    Priority order: OpenAI > Anthropic > fallback to random message

    Returns:
        str: Generated or fallback completion message
    """
    # Get current script directory and construct utils/llm path
    script_dir = Path(__file__).parent
    llm_dir = script_dir / "llm"

    # Try OpenAI first (highest priority)
    if os.getenv('OPENAI_API_KEY'):
        oai_script = llm_dir / "oai.py"
        if oai_script.exists():
            try:
                result = subprocess.run([
                    "uv", "run", str(oai_script), "--completion"
                ],
                capture_output=True,
                text=True,
                timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Anthropic second
    if os.getenv('ANTHROPIC_API_KEY'):
        anth_script = llm_dir / "anth.py"
        if anth_script.exists():
            try:
                result = subprocess.run([
                    "uv", "run", str(anth_script), "--completion"
                ],
                capture_output=True,
                text=True,
                timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Fallback to random predefined message
    messages = get_completion_messages()
    return random.choice(messages)


def generate_notification_message(include_name=False):
    """
    Generate notification message for user input requests.

    Args:
        include_name: Whether to include engineer name (30% chance if available)

    Returns:
        str: Notification message
    """
    # Get engineer name if available
    engineer_name = os.getenv('ENGINEER_NAME', '').strip()

    # Create notification message with 30% chance to include name
    if include_name and engineer_name and random.random() < 0.3:
        return f"{engineer_name}, your agent needs your input"
    else:
        return "Your agent needs your input"


def announce(message_type="custom", custom_message=None, use_llm=False, include_name=False):
    """
    Unified TTS announcement function.

    Args:
        message_type: "notification", "completion", "subagent", or "custom"
        custom_message: Override message for custom announcements
        use_llm: Whether to use LLM for message generation (for completion type)
        include_name: Whether to include engineer name (for notification type)
    """
    logger = setup_hook_logger('tts_announcer')

    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return  # No TTS scripts available

        # Generate message based on type
        if custom_message:
            message = custom_message
        elif message_type == "notification":
            message = generate_notification_message(include_name)
        elif message_type == "completion":
            if use_llm:
                message = get_llm_completion_message()
            else:
                message = random.choice(get_completion_messages())
        elif message_type == "subagent":
            message = "Subagent Complete"
        else:
            # Default fallback
            message = "Agent notification"

        # Call the TTS script with the message
        subprocess.run([
            "uv", "run", tts_script, message
        ],
        capture_output=True,  # Suppress output
        timeout=10  # 10-second timeout
        )

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
        # Fail silently if TTS encounters issues
        log_exception(logger, e, f"TTS subprocess error in {message_type} announcement")
    except Exception as e:
        # Fail silently for any other errors
        log_exception(logger, e, f"Unexpected error in {message_type} TTS announcement")