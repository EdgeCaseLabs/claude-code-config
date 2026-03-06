---
name: cmux
description: Browser automation and interaction for debugging web apps using the cmux CLI. Use when the user wants to automate a browser, inspect page state, interact with DOM elements, capture screenshots, debug JS errors, or test web app flows.
allowed-tools: [Bash, Read, Write]
---

# cmux Browser Automation Skill

This skill provides browser automation capabilities using the `cmux browser` CLI for debugging and testing web applications.

## Prerequisites

- `cmux` must be installed and a browser session must be open
- Surfaces are identified as `surface:N` (e.g., `surface:1`, `surface:2`)

## Targeting Surfaces

`CMUX_SURFACE_ID` is auto-set in cmux terminals, so surface targeting is automatic when running inside cmux. When running from an **external terminal** (e.g., Claude's shell), the surface is NOT auto-detected — you must specify it explicitly:

```bash
# Positional surface argument (preferred)
cmux browser surface:1 url

# Flag syntax
cmux browser --surface surface:1 url
```

Use `cmux browser identify` to list available surfaces.

## Navigation

```bash
# Open a URL (creates a browser split in caller's workspace)
cmux browser open "https://example.com"

# Open in a split view
cmux browser open-split "https://example.com"

# Navigate to a URL (in-page navigation)
cmux browser navigate "https://example.com/path"
# or: cmux browser goto "https://example.com/path"

# Browser history
cmux browser back
cmux browser forward
cmux browser reload

# Get current URL
cmux browser url
```

## Waiting for Page State

Block until a condition is met before proceeding:

```bash
# Wait for full page load (interactive or complete)
cmux browser wait --load-state complete --timeout-ms 15000

# Wait for a selector to appear
cmux browser wait --selector "#checkout" --timeout-ms 10000

# Wait for specific text
cmux browser wait --text "Order confirmed"

# Wait for URL to contain a fragment
cmux browser wait --url-contains "/dashboard"

# Wait for a JavaScript condition
cmux browser wait --function "window.__appReady === true"
```

## DOM Inspection

```bash
# Snapshot the DOM (primary tool for understanding page structure)
cmux browser snapshot

# Interactive snapshot (with clickable elements highlighted)
cmux browser snapshot --interactive

# Compact snapshot (less verbose)
cmux browser snapshot --compact

# Snapshot scoped to a selector
cmux browser snapshot --selector "#main-content"

# Limit snapshot depth
cmux browser snapshot --max-depth 3

# Get page info
cmux browser get title
cmux browser get url
cmux browser get text --selector ".error-message"
cmux browser get html --selector "#app"
cmux browser get value --selector "input[name=email]"
cmux browser get count --selector ".item"
cmux browser get box --selector "#modal"       # dimensions/position
cmux browser get styles --selector "button.primary"

# Check element state (selector is positional, not a flag)
cmux browser is visible "#spinner"
cmux browser is enabled "button[type=submit]"
cmux browser is checked "input[type=checkbox]"
```

## Finding Elements

```bash
# Find by ARIA role
cmux browser find role button

# Find by visible text
cmux browser find text "Sign in"

# Find by label
cmux browser find label "Email address"

# Find by placeholder
cmux browser find placeholder "Search..."

# Find by test ID
cmux browser find testid "login-form"

# Positional
cmux browser find first ".item"
cmux browser find last ".item"
cmux browser find nth 2 ".item"   # zero-indexed
```

## DOM Interaction

All mutating actions support `--snapshot-after` for immediate verification.

**Note:** Selectors for `click`, `fill`, `type`, `select`, etc. are **positional arguments**, not `--selector` flags.

```bash
# Click
cmux browser click "button[type=submit]"
cmux browser click "#login-btn" --snapshot-after

# Double click
cmux browser dblclick ".editable-cell"

# Hover
cmux browser hover ".dropdown-trigger"

# Focus
cmux browser focus "input[name=search]"

# Type (APPENDS to existing value — does not clear first)
cmux browser type "input[name=search]" "query"

# Fill (clears then types; empty string clears the input)
cmux browser fill "input[name=email]" "user@example.com"

# ⚠️ React inputs: fill sets the DOM value but does NOT trigger React's
# onChange/synthetic events. For React-controlled inputs, use eval:
cmux browser eval "
  const el = document.querySelector('input[name=email]');
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  nativeInputValueSetter.call(el, 'user@example.com');
  el.dispatchEvent(new Event('input', { bubbles: true }));
"

# Press a key (no selector — applies to focused element)
cmux browser press "Enter"
cmux browser keydown "Escape"
cmux browser keyup "Shift"

# Select dropdown option
cmux browser select "select[name=country]" "US"

# Scroll (use --dx for horizontal, --dy for vertical)
cmux browser scroll --selector ".feed" --dy 500
cmux browser scroll-into-view "#target-section"

# Checkbox
cmux browser check "input[type=checkbox]"
cmux browser uncheck "input[type=checkbox]"

# Highlight an element (visual debugging)
cmux browser highlight ".problematic-element"
```

## JavaScript Execution

```bash
# Evaluate JavaScript and return result
cmux browser eval "document.title"
cmux browser eval "document.querySelectorAll('.error').length"

# Inject a script that runs on every page load
cmux browser addinitscript "window.__debug = true"

# Inject a script into current page
cmux browser addscript "console.log('injected')"

# Inject CSS
cmux browser addstyle ".ad { display: none !important; }"
```

## Debugging: Console Logs and Errors

```bash
# List console messages
cmux browser console list

# Clear console
cmux browser console clear

# List JS errors
cmux browser errors list

# Clear errors
cmux browser errors clear
```

## Cookies and Storage

```bash
# Get all cookies
cmux browser cookies get --all

# Get specific cookie
cmux browser cookies get --name "session_id"

# Set a cookie
cmux browser cookies set --name "feature_flag" --value "true" --domain "example.com"

# Clear cookies
cmux browser cookies clear --name "session_id"
cmux browser cookies clear --all

# Local storage (requires 'local' or 'session' subcommand)
cmux browser storage local get --key "user_prefs"
cmux browser storage local set --key "debug_mode" --value "true"
cmux browser storage local clear --key "user_prefs"

# Session storage
cmux browser storage session get --key "temp_data"
cmux browser storage session set --key "temp_data" --value "value"
```

## Tabs

```bash
# List open tabs
cmux browser tab list

# Open a new tab
cmux browser tab new

# Switch to a tab by index (positional)
cmux browser tab switch 2

# Close current tab
cmux browser tab close
```

## Dialogs (alert/confirm/prompt)

```bash
cmux browser dialog accept
cmux browser dialog dismiss
```

## Frames (iframes)

```bash
# Enter an iframe context (selector is positional)
cmux browser frame "iframe#payment-frame"

# Return to main document
cmux browser frame main
```

## Downloads

```bash
# Wait for and save a download (--path, not --out)
cmux browser download wait --path /tmp/downloaded-file.pdf --timeout-ms 10000
```

## Session State

```bash
# Save browser state (cookies, storage) to file (path is positional)
cmux browser state save /tmp/session.json

# Restore browser state from file
cmux browser state load /tmp/session.json
```

## Common Debugging Workflows

### Inspect a page for errors

```bash
# Navigate and wait for load
cmux browser open "https://app.example.com"
cmux browser wait --load-state complete --timeout-ms 15000

# Capture current state
cmux browser snapshot --compact

# Check for JS errors
cmux browser errors list
cmux browser console list
```

### Debug a form submission

```bash
cmux browser open "https://app.example.com/login"
cmux browser wait --load-state complete --timeout-ms 15000
cmux browser fill "input[name=email]" "user@example.com"
cmux browser fill "input[name=password]" "secret"
cmux browser click "button[type=submit]" --snapshot-after
cmux browser wait --url-contains "/dashboard" --timeout-ms 10000
cmux browser get title
```

### Check element visibility and state

```bash
cmux browser snapshot --selector "#main-form"
cmux browser is visible ".loading-spinner"
cmux browser is enabled "button#submit"
cmux browser get text --selector ".error-message"
```

### Capture network/auth state

```bash
cmux browser cookies get --all
cmux browser storage local get --key "authToken"
cmux browser eval "document.cookie"
```

### Measure viewport

```bash
cmux browser eval "window.innerWidth + 'x' + window.innerHeight"
```

## Error Handling

- If a selector is not found, commands will fail with a timeout — use `cmux browser snapshot` first to confirm selectors
- For dynamic content, always use `wait` before interacting
- Use `--snapshot-after` on click/fill to immediately verify the result
- Capture `cmux browser errors list` and `cmux browser console list` when debugging unexpected behavior
- When running outside a cmux terminal, always specify `--surface surface:N` or prefix with `surface:N` as first arg
- There is no `screenshot` command — use `cmux browser snapshot` to capture DOM state instead
