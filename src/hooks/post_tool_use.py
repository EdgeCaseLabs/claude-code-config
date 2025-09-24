#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import os
import sys
from pathlib import Path
from hook_logger import setup_hook_logger, log_exception

def main():
    logger = setup_hook_logger('post_tool_use')
    
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Ensure log directory exists
        log_dir = os.path.expanduser('~/.claude/hooks/logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'post_tool_use.json')
        
        # Read existing log data or initialize empty list
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []
        
        # Append new data
        log_data.append(input_data)
        
        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        log_exception(logger, e, "JSON decode error while processing tool output")
        sys.exit(0)
    except Exception as e:
        # Exit cleanly on any other error
        log_exception(logger, e, "Unexpected error in post_tool_use hook")
        sys.exit(0)

if __name__ == '__main__':
    main()