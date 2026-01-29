---
description: "Get up to speed on a new codebase with comprehensive analysis"
argument-hint: ""
---

# Onboard to Codebase

This command provides a structured exploration of a codebase to help you understand the project quickly. It covers:

- Project purpose and tech stack
- Architecture and code organization
- How to run the application locally
- Development workflow and conventions
- Key domain abstractions and patterns

After completion, you'll have a clear understanding of what the project does, how it's structured, and how to work with it effectively.

---

You are a senior software engineer with 15+ years of experience across Python and TypeScript ecosystems. I've just been assigned to this project and need to get up to speed quickly. Help me understand this codebase thoroughly.

**IMPORTANT**: At the end of your exploration, write all your findings to a file named `onboard-YYYY-MM-DD.md` in the project root directory, using today's date.

## Phase 1: Project Identity & Purpose

1. **Read the README and any docs/ folder** - Summarize what problem this project solves, who the users are, and what the core value proposition is.

2. **Identify the tech stack** - Check package.json, pyproject.toml, requirements.txt, Pipfile, or similar. What frameworks, ORMs, and major dependencies are in use?

3. **Understand the deployment target** - Is this a web app, CLI tool, library, microservice, monolith? Check for Dockerfile, docker-compose.yml, serverless configs, or cloud deployment manifests.

## Phase 2: Architecture & Code Organization

1. **Map the directory structure** - Explain the top-level folders and what lives where. Identify patterns (src/, lib/, app/, api/, services/, models/, etc.)

2. **Find the entry points**:
   - For web apps: main server file, route definitions, middleware chain
   - For CLIs: main entry script, command registration
   - For libraries: public API surface, __init__.py or index.ts exports

3. **Trace the data flow** - How does a request/command flow through the system? Identify:
   - Route handlers or controllers
   - Service/business logic layer
   - Data access layer (repositories, ORMs, raw queries)
   - External integrations (APIs, queues, caches)

4. **Database schema** - Check for migrations, schema files, or ORM models. What are the core entities and their relationships?

## Phase 3: Running the Application

1. **Local development setup** - What commands bootstrap the environment? Check for:
   - Makefile, justfile, or scripts/ folder
   - Docker compose for local services
   - Environment variables needed (.env.example, .env.template)

2. **Available URLs/endpoints** - For web apps, enumerate:
   - UI routes I can visit in a browser
   - API endpoints (look for OpenAPI specs, route files)
   - Admin interfaces, health checks, debug endpoints

3. **How to run tests** - Find the test command and run it. What's the test coverage like? What testing frameworks are used?

## Phase 4: Development Workflow

1. **Code style and linting** - Check for eslint, prettier, ruff, black, mypy configs. What are the enforced conventions?

2. **CI/CD pipeline** - Look at .github/workflows, .gitlab-ci.yml, or similar. What checks run on PRs?

3. **Git conventions** - Any branch naming conventions, commit message formats, or PR templates?

## Phase 5: Domain Knowledge

1. **Key abstractions** - What are the 5-10 most important classes/functions/types? These are the concepts I'll encounter repeatedly.

2. **Configuration system** - How is the app configured? Environment variables, config files, feature flags?

3. **Error handling patterns** - How are errors propagated and logged? Any custom exception hierarchies?

4. **Authentication/authorization** - If applicable, how do users authenticate? How are permissions checked?

## Deliverables

After exploration, write a comprehensive markdown document to `onboard-YYYY-MM-DD.md` in the project root that includes:

- A one-paragraph summary of what this project does
- A diagram or description of the high-level architecture
- The 3-5 files I should read first to understand the core logic
- Commands I need to run the app locally
- URLs I can visit to interact with the running application
- Any "gotchas" or non-obvious things a new developer should know
- All key findings from each phase of exploration

The document should be well-formatted, easy to navigate, and serve as a reference guide for new developers joining the project.
