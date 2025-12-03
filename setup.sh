#!/bin/bash

# Claude Code Configuration Setup Script
# This script creates symlinks from ~/.claude/ to this repository for centralized configuration management

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS_TARGET="$SCRIPT_DIR/src/settings.json"
HOOKS_TARGET="$SCRIPT_DIR/src/hooks"
CLAUDE_MD_TARGET="$SCRIPT_DIR/src/CLAUDE.md"
COMMANDS_TARGET="$SCRIPT_DIR/src/commands"
AGENTS_TARGET="$SCRIPT_DIR/src/agents"


# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Claude Code Configuration Setup Script

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -f, --force     Force overwrite existing files/directories
    --dry-run       Show what would be done without making changes
    --remove        Remove existing symlinks (uninstall)

This script creates symlinks from ~/.claude/ to this repository's configuration files:
- ~/.claude/settings.json -> ./src/settings.json
- ~/.claude/hooks/ -> ./src/hooks/
- ~/.claude/CLAUDE.md -> ./src/CLAUDE.md
- ~/.claude/commands/ -> ./src/commands/
- ~/.claude/agents/ -> ./src/agents/

Use --remove to uninstall (remove symlinks).
Use --force to overwrite existing files/directories (WARNING: destructive).
The script will exit if existing files/directories are found unless --force is used.
EOF
}

# Parse command line arguments
VERBOSE=false
FORCE=false
DRY_RUN=false
REMOVE_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --remove)
            REMOVE_MODE=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Verbose logging
verbose_log() {
    if [[ "$VERBOSE" == true ]]; then
        log_info "$1"
    fi
}

# Dry run execution
execute_or_simulate() {
    local cmd="$1"
    local description="$2"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN] Would execute: $description"
        verbose_log "[DRY RUN] Command: $cmd"
    else
        verbose_log "Executing: $cmd"
        eval "$cmd"
        log_success "$description"
    fi
}

# Validation functions
validate_targets() {
    if [[ ! -f "$SETTINGS_TARGET" ]]; then
        log_error "Settings file not found: $SETTINGS_TARGET"
        return 1
    fi
    
    if [[ ! -d "$HOOKS_TARGET" ]]; then
        log_error "Hooks directory not found: $HOOKS_TARGET"
        return 1
    fi
    
    if [[ ! -f "$CLAUDE_MD_TARGET" ]]; then
        log_error "CLAUDE.md file not found: $CLAUDE_MD_TARGET"
        return 1
    fi
    
    if [[ ! -d "$COMMANDS_TARGET" ]]; then
        log_error "Commands directory not found: $COMMANDS_TARGET"
        return 1
    fi

    if [[ ! -d "$AGENTS_TARGET" ]]; then
        log_error "Agents directory not found: $AGENTS_TARGET"
        return 1
    fi

    log_success "Configuration targets validated"
    return 0
}



# Symlink removal function
remove_symlink() {
    local link="$1"
    local name="$2"
    
    if [[ -L "$link" ]]; then
        execute_or_simulate "rm '$link'" "Removed $name symlink"
        return 0
    elif [[ -e "$link" ]]; then
        log_warning "$name exists as a file/directory (not a symlink) at $link"
        log_warning "Please remove manually if desired"
        return 0
    else
        log_info "$name symlink does not exist at $link"
        return 0
    fi
}

# Symlink management functions
create_symlink() {
    local target="$1"
    local link="$2"
    local name="$3"
    
    # Check if symlink already exists and is correct
    if [[ -L "$link" ]]; then
        local current_target=$(readlink "$link")
        if [[ "$current_target" == "$target" ]]; then
            log_info "$name symlink already exists and is correct"
            return 0
        else
            log_warning "$name symlink exists but points to wrong target: $current_target"
        fi
    fi
    
    # Check for existing files/directories and exit if found (unless --force)
    if [[ -e "$link" ]] && [[ ! -L "$link" ]]; then
        if [[ "$FORCE" == false ]]; then
            log_error "$name already exists as a file/directory at $link"
            log_error "Please backup and remove your existing configuration first"
            log_error "Use --force to overwrite existing files (WARNING: will delete them)"
            exit 1
        else
            log_warning "$name exists as a file/directory at $link"
            log_warning "Using --force: will remove and replace with symlink"
            if [[ -d "$link" ]]; then
                execute_or_simulate "rm -r '$link'" "Removed existing $name directory (--force)"
            else
                execute_or_simulate "rm '$link'" "Removed existing $name file (--force)"
            fi
        fi
    fi
    
    # Remove existing symlink if it exists
    if [[ -L "$link" ]]; then
        execute_or_simulate "rm '$link'" "Removed existing $name symlink"
    fi
    
    # Create the symlink
    execute_or_simulate "ln -sf '$target' '$link'" "Created $name symlink"
}

# Remove symlinks function
remove_configuration() {
    log_info "Removing Claude Code configuration symlinks..."
    
    # Remove settings.json symlink
    remove_symlink "$CLAUDE_DIR/settings.json" "settings.json"
    
    # Remove hooks directory symlink
    remove_symlink "$CLAUDE_DIR/hooks" "hooks directory"
    
    # Remove CLAUDE.md symlink
    remove_symlink "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
    
    # Remove commands directory symlink
    remove_symlink "$CLAUDE_DIR/commands" "commands directory"

    # Remove agents directory symlink
    remove_symlink "$CLAUDE_DIR/agents" "agents directory"

    if [[ "$DRY_RUN" == false ]]; then
        log_success "Configuration symlinks removed successfully"
    else
        log_info "Dry run complete. Use without --dry-run to remove symlinks."
    fi
}

# Main setup function
setup_configuration() {
    log_info "Starting Claude Code configuration setup..."
    
    # Validate targets exist
    if ! validate_targets; then
        exit 1
    fi
    
    # Ensure .claude directory exists
    execute_or_simulate "mkdir -p '$CLAUDE_DIR'" "Ensured ~/.claude directory exists"
    
    # Create settings.json symlink
    create_symlink "$SETTINGS_TARGET" "$CLAUDE_DIR/settings.json" "settings.json"
    
    # Create hooks directory symlink
    create_symlink "$HOOKS_TARGET" "$CLAUDE_DIR/hooks" "hooks directory"
    
    # Create CLAUDE.md symlink
    create_symlink "$CLAUDE_MD_TARGET" "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
    
    # Create commands directory symlink
    create_symlink "$COMMANDS_TARGET" "$CLAUDE_DIR/commands" "commands directory"

    # Create agents directory symlink
    create_symlink "$AGENTS_TARGET" "$CLAUDE_DIR/agents" "agents directory"

    # Verify symlinks
    if [[ "$DRY_RUN" == false ]]; then
        log_info "Verifying symlink integrity..."
        
        if [[ -L "$CLAUDE_DIR/settings.json" ]] && [[ -f "$CLAUDE_DIR/settings.json" ]]; then
            log_success "Settings symlink is working correctly"
        else
            log_error "Settings symlink verification failed"
            exit 1
        fi
        
        if [[ -L "$CLAUDE_DIR/hooks" ]] && [[ -d "$CLAUDE_DIR/hooks" ]]; then
            log_success "Hooks symlink is working correctly"
        else
            log_error "Hooks symlink verification failed"
            exit 1
        fi
        
        if [[ -L "$CLAUDE_DIR/CLAUDE.md" ]] && [[ -f "$CLAUDE_DIR/CLAUDE.md" ]]; then
            log_success "CLAUDE.md symlink is working correctly"
        else
            log_error "CLAUDE.md symlink verification failed"
            exit 1
        fi
        
        if [[ -L "$CLAUDE_DIR/commands" ]] && [[ -d "$CLAUDE_DIR/commands" ]]; then
            log_success "Commands symlink is working correctly"
        else
            log_error "Commands symlink verification failed"
            exit 1
        fi

        if [[ -L "$CLAUDE_DIR/agents" ]] && [[ -d "$CLAUDE_DIR/agents" ]]; then
            log_success "Agents symlink is working correctly"
        else
            log_error "Agents symlink verification failed"
            exit 1
        fi

        log_success "All symlinks verified successfully"
        
        # Display final status
        echo
        log_info "Configuration setup complete!"
        log_info "Settings: $CLAUDE_DIR/settings.json -> $SETTINGS_TARGET"
        log_info "Hooks: $CLAUDE_DIR/hooks -> $HOOKS_TARGET"
        log_info "User Memory: $CLAUDE_DIR/CLAUDE.md -> $CLAUDE_MD_TARGET"
        log_info "Commands: $CLAUDE_DIR/commands -> $COMMANDS_TARGET"
        log_info "Agents: $CLAUDE_DIR/agents -> $AGENTS_TARGET"
        

    else
        log_info "Dry run complete. Use without --dry-run to apply changes."
    fi
}

# Error handling
trap 'log_error "Script failed at line $LINENO"' ERR

# Main execution
if [[ "$REMOVE_MODE" == true ]]; then
    remove_configuration
else
    setup_configuration
fi