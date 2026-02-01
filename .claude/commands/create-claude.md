# Create CLAUDE.md

Generate a comprehensive CLAUDE.md project documentation file for this codebase.

## Instructions

Analyze the current project structure, configuration files, and codebase to generate a CLAUDE.md file that serves as the primary reference document for working with this project.

## Required Sections

### 1. Project Header
- Project name and one-line description
- Core purpose and functionality

### 2. Tech Stack
Document all technologies used:
- **Backend**: Language, framework, ORM, database, logging
- **Frontend**: Framework, build tool, styling, state management
- **Testing**: Test frameworks for each layer
- **Authentication**: Auth approach or "No authentication" if local-only

### 3. Project Structure
Create an ASCII tree showing:
- Top-level directories
- Key files with brief comments explaining their purpose
- Configuration files
- Test organization

### 4. Commands
Provide copy-paste ready commands for:
- Installation/setup
- Running development servers
- Running tests (unit, integration, E2E)
- Building for production
- Any project-specific scripts

### 5. MCP Servers (if applicable)
Document any MCP servers used with:
- Installation command
- Use cases

### 6. Reference Documentation
Create a table linking to project docs:
| Document | When to Read |
|----------|--------------|
| Path to doc | Context for when to reference it |

### 7. Code Conventions
Document patterns for each layer:
- Backend conventions (schemas, dependencies, patterns)
- Frontend conventions (folder structure, state management, styling)
- API design (REST patterns, status codes, error handling)

### 8. Logging
Document logging approach:
- Library used
- Configuration for dev vs production
- Example usage code
- What gets logged automatically

### 9. Database
Document database setup:
- Database type and mode
- Required initialization (PRAGMAs, migrations)
- Schema overview or reference to schema docs

### 10. Testing Strategy
Document the testing approach:
- Testing pyramid percentages
- What each test layer covers
- Test organization structure
- How to run each type of test

## Process

1. **Explore the codebase** to understand:
   - Languages and frameworks used
   - Project structure and organization
   - Existing documentation
   - Configuration files (package.json, pyproject.toml, etc.)
   - Test setup and patterns

2. **Identify key patterns** by reading:
   - Entry point files
   - Example endpoints/components
   - Test files
   - Any existing README or docs

3. **Generate CLAUDE.md** at the project root with all sections populated based on actual project details

4. **Validate** that all commands are accurate and paths are correct

## Output

Write the generated CLAUDE.md file to the project root directory.
