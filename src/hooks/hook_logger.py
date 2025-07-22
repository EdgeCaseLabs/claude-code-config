import logging
import os
import traceback
from datetime import datetime

def setup_hook_logger(hook_name):
    """
    Setup a logger for a specific hook that logs to .claude/hook-errors.log
    
    Args:
        hook_name: Name of the hook (e.g., 'pre_tool_use', 'post_tool_use')
    
    Returns:
        A configured logger instance
    """
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, 'hook-errors.log')
    
    # Create a logger specific to this hook
    logger = logging.getLogger(f'claude_hook.{hook_name}')
    logger.setLevel(logging.ERROR)
    
    # Only add handler if one doesn't exist (to avoid duplicates)
    if not logger.handlers:
        # Create file handler
        handler = logging.FileHandler(log_file, mode='a')
        handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            f'[%(asctime)s] [%(name)s] [%(levelname)s]\n%(message)s\n{"="*80}\n',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger

def log_exception(logger, exception, context=None):
    """
    Log an exception with full stack trace
    
    Args:
        logger: The logger instance to use
        exception: The exception that was caught
        context: Optional context string to include in the log
    """
    error_msg = f"Exception in hook: {type(exception).__name__}: {str(exception)}"
    if context:
        error_msg = f"{context}\n{error_msg}"
    
    # Get the full stack trace
    tb_str = traceback.format_exc()
    
    # Log the error with stack trace
    logger.error(f"{error_msg}\n\nStack trace:\n{tb_str}")