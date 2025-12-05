---
name: jira-integration
description: Query and manage Jira work items using the acli tool. Search issues with JQL, view work item details, create tickets, update statuses, manage assignments, list projects and sprints. Use when working with Jira tickets, project management tasks, or when the user mentions Jira issue keys.
allowed-tools: [Bash, Read, Write, Glob]
---

# Jira Integration Skill

This skill provides integration with Atlassian Jira using the `acli jira` command-line tool.

## Prerequisites

- The `acli` tool must be installed and authenticated
- Run `acli jira auth` to authenticate if not already done

## Core Capabilities

### 1. Work Item Management

**Search for work items:**
```bash
# Basic JQL search with pagination
acli jira workitem search --jql "project = TEAM" --paginate

# Search with specific fields
acli jira workitem search --jql "assignee = currentUser() AND status = 'In Progress'" --fields "key,summary,assignee,status"

# Export to CSV
acli jira workitem search --jql "project = TEAM" --csv

# Get count only
acli jira workitem search --jql "project = TEAM" --count

# Limit results
acli jira workitem search --jql "project = TEAM" --limit 50

# Search by filter ID
acli jira workitem search --filter 10001 --json
```

**View work item details:**
```bash
# View basic details
acli jira workitem view KEY-123

# View with specific fields
acli jira workitem view KEY-123 --fields summary,comment,description

# Export to JSON
acli jira workitem view KEY-123 --json
```

**Create work items:**
```bash
# Create a task
acli jira workitem create --summary "Task title" --project "TEAM" --type "Task"

# Create with description and assignment
acli jira workitem create --summary "Bug fix" --project "PROJ" --type "Bug" \
  --description "Details here" --assignee "user@example.com"

# Create with labels
acli jira workitem create --summary "New feature" --project "TEAM" --type "Story" \
  --label "feature,priority"
```

**Update work items:**
```bash
# Edit work item
acli jira workitem edit KEY-123 --summary "Updated title"

# Assign work item
acli jira workitem assign KEY-123 --assignee "@me"

# Transition work item
acli jira workitem transition KEY-123 --state "In Progress"
```

### 2. Project Management

**List projects:**
```bash
# List all projects (requires one of: --recent, --limit, --paginate)
acli jira project list --paginate

# List recent projects
acli jira project list --recent

# List limited number of projects
acli jira project list --limit 10
```

**View project details:**
```bash
acli jira project view PROJ
```

### 3. Board and Sprint Management

**Search boards:**
```bash
acli jira board search
```

**List sprints for a board:**
```bash
# List all sprints for a board
acli jira board list-sprints --id 123

# List active sprints only
acli jira board list-sprints --id 123 --state active

# List with pagination
acli jira board list-sprints --id 123 --paginate

# Output as JSON
acli jira board list-sprints --id 123 --json
```

**List work items in a sprint:**
```bash
# List work items in a sprint (both --sprint and --board are required)
acli jira sprint list-workitems --sprint 456 --board 123

# List with custom fields
acli jira sprint list-workitems --sprint 456 --board 123 --fields "key,summary,status,assignee"

# List with JQL filter
acli jira sprint list-workitems --sprint 456 --board 123 --jql "assignee = currentUser()"

# Output as JSON
acli jira sprint list-workitems --sprint 456 --board 123 --json
```

## Limitations

### Sprint Assignment
The acli tool does not provide a direct command to add work items to sprints. The `create` and `edit` commands do not have a `--sprint` flag. After creating work items, you must either:
- Add them to sprints via the Jira web UI (drag/drop in board view)
- Use the board's sprint planning view
- Potentially use `acli jira workitem edit --from-json` with the sprint custom field (requires knowing your instance's custom field ID, typically `customfield_10020`)

**Workflow for creating items for a sprint:**
```bash
# Step 1: Find the active sprint
acli jira board list-sprints --id 576 --state active

# Step 2: Create work items
acli jira workitem create --summary "Task title" --project "INS" --type "ToDo" --assignee "@me"

# Step 3: Note the returned key (e.g., INS-388)
# Step 4: Add to sprint manually via Jira web UI
```

**To list items already in a sprint:**
```bash
acli jira sprint list-workitems --sprint 1671 --board 576
```

## Common JQL Patterns

- `project = TEAM` - All issues in a project
- `assignee = currentUser()` - Issues assigned to authenticated user
- `status = "In Progress"` - Issues in a specific status
- `created >= -7d` - Issues created in last 7 days
- `project = TEAM AND assignee = currentUser() AND status != Done` - Active user issues
- `labels = bug` - Issues with specific label
- `priority = High` - High priority issues

## Output Formats

- **Default**: Human-readable table format
- **JSON**: Use `--json` flag for machine-readable output
- **CSV**: Use `--csv` flag for spreadsheet export
- **Web**: Use `--web` flag to open in browser

## Important Notes

1. **Authentication**: If commands fail with auth errors, user needs to run `acli jira auth`
2. **Project Keys**: Work item keys are in format `PROJECT-123` (uppercase project code)
3. **Field Names**: Use exact field names from Jira (case-sensitive)
4. **JQL Queries**: Must be properly quoted and escaped
5. **Pagination**: Use `--paginate` for large result sets, `--limit N` to restrict count

## Error Handling

Common issues:
- **"Unauthorized"**: Run `acli jira auth` to authenticate
- **"Project not found"**: Verify project key spelling
- **"Invalid JQL"**: Check JQL syntax and quotes
- **"Field not found"**: Use exact Jira field names

## Workflow Examples

**Daily standup prep:**
```bash
acli jira workitem search --jql "assignee = currentUser() AND status != Done" \
  --fields "key,summary,status,priority"
```

**Create bug from user report:**
```bash
acli jira workitem create --summary "Bug: Login fails" --project "TEAM" \
  --type "Bug" --description "User cannot login" --priority "High"
```

**Check sprint progress:**
```bash
acli jira sprint list-workitems --sprint-id 123 --json
```

## Best Practices

1. Always use `--json` when parsing output programmatically
2. Use `--fields` to limit returned data for performance
3. Use `--paginate` for comprehensive searches
4. Quote JQL queries properly to avoid shell parsing issues
5. Validate work item keys before operations
6. Use `--count` to check result size before fetching all data
