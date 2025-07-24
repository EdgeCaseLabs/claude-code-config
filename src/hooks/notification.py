#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import os
import sys
import subprocess
import random
from pathlib import Path
from hook_logger import setup_hook_logger, log_exception

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"
    
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


def announce_notification():
    """Announce that the agent needs user input."""
    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return  # No TTS scripts available
        
        # Get engineer name if available
        engineer_name = os.getenv('ENGINEER_NAME', '').strip()
        
        # Create notification message with 30% chance to include name
        if engineer_name and random.random() < 0.3:
            notification_message = f"{engineer_name}, your agent needs your input"
        else:
            notification_message = "Your agent needs your input"
        
        # Call the TTS script with the notification message
        out = subprocess.run([
            "uv", "run", tts_script, notification_message
        ], 
        capture_output=True,  # Suppress output
        timeout=10  # 10-second timeout
        )
        if out.returncode != 0:
            print(f"TTS script failed with return code: {out.returncode}")
            print(f"Output: {out.stdout}")
            print(f"Error: {out.stderr}")
            sys.exit(1)
        
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
        # Fail silently if TTS encounters issues
        logger = setup_hook_logger('notification')
        log_exception(logger, e, "TTS subprocess error in notification hook")
    except Exception as e:
        # Fail silently for any other errors
        logger = setup_hook_logger('notification')
        log_exception(logger, e, "Unexpected error in TTS function of notification hook")


def main():
    logger = setup_hook_logger('notification')
    
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--notify', action='store_true', help='Enable TTS notifications')
        parser.add_argument('--skip-generic-message', action='store_true', help='Skip the generic "Claude is waiting for your input" message')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Ensure log directory exists
        import os
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'notification.json')
        
        # Read existing log data or initialize empty list
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Announce notification via TTS only if --notify flag is set
        # Skip TTS for the generic "Claude is waiting for your input" message
        if args.notify and (input_data.get('message') != 'Claude is waiting for your input' or not args.skip_generic_message):
            announce_notification()
        
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        log_exception(logger, e, "JSON decode error while processing notification hook input")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully
        log_exception(logger, e, "Unexpected error in notification hook")
        sys.exit(0)

if __name__ == '__main__':
    main()