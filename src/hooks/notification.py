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
from pathlib import Path
from hook_logger import setup_hook_logger, log_exception
from utils.tts_announcer import announce

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional




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
        log_dir = os.path.expanduser('~/.claude/hooks/logs')
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
            announce("notification", include_name=True)
        
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