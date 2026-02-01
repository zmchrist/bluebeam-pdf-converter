---
description: Generate a README.md based on project details and structure
argument-hint: [output-filename]
---

# Create README: Generate Project Documentation

## Overview

Analyze the current project structure, codebase, and configuration files to generate a comprehensive README.md file. The README should help developers understand, set up, and contribute to the project.

## Output File

Write the README to the project root directory: `$ARGUMENTS` (default: `./README.md` in the base folder of the project)

**Important:** Always write to the project's base/root folder, not a subdirectory, unless explicitly specified otherwise.

## README Structure

Create a well-structured README with the following sections. Adapt based on project type and available information:

### Required Sections

**1. Project Title & Description**
- Clear, descriptive project name as H1 heading
- 1-2 paragraph description explaining:
  - What the project does
  - The problem it solves
  - Key use cases
- Mention primary technologies (e.g., "Built with Python backend (FastAPI) and React frontend")

**2. Prerequisites**
- Required language versions (Python 3.x+, Node.js X+, etc.)
- Package managers (npm, uv, pip, etc.)
- System dependencies
- Optional tools (Git, Docker, etc.)

**3. Quick Start**
- Numbered steps to get running locally
- Backend setup commands in code blocks
- Frontend setup commands (if applicable)
- URLs for accessing the running application
- Keep it minimal - just what's needed to run

**4. Architecture**
- ASCII diagram showing system components and their connections
- Use box-drawing characters for visual clarity
- Show ports, protocols, data flow

**5. Tech Stack Table**
- Table with Layer and Technology columns
- Include versions where relevant
- Cover: Backend, Frontend, Database, Processing, etc.

**6. Project Structure**
- Tree diagram of key directories and files
- Brief inline comments explaining purpose of each
- Focus on important files, not every file
- Use standard tree format with `├──`, `│`, and `└──`

**7. Features**
- Bulleted list of key features
- Use em-dash format: `**Feature Name** — Description`
- 4-8 main features
- Focus on user-facing capabilities

**8. API Endpoints** (if applicable)
- Table with Method, Endpoint, Description columns
- Cover main CRUD operations
- Note where full API docs are available

**9. Claude Commands** (if .claude/commands exist)
- Reference to available slash commands
- Group by category (Planning, Validation, Git, etc.)
- Table format with Command and Description

**10. Additional Sections** (as needed)
- Environment Variables / Configuration
- Testing instructions
- Deployment guide
- Contributing guidelines
- License

## Instructions

### 1. Analyze the Project
- Read package.json, pyproject.toml, requirements.txt, Cargo.toml, or similar
- Examine directory structure
- Identify entry points (main.py, index.js, etc.)
- Look for existing documentation
- Check for .claude/commands directory

### 2. Gather Technical Details
- Determine tech stack from dependencies
- Identify API endpoints from router files
- Note any special configuration requirements
- Find port numbers and URLs

### 3. Write the README
- Start with a compelling project description
- Use clear, concise language
- Include working code examples
- Add ASCII diagrams for architecture
- Use tables for structured information

### 4. Quality Checks
- All code blocks have language specifiers
- Commands are copy-paste ready
- URLs and ports are accurate
- Project structure matches reality
- No placeholder text remaining

## Style Guidelines

- **Tone:** Professional, helpful, developer-focused
- **Format:** GitHub-flavored markdown
- **Code Blocks:** Always specify language (```bash, ```python, etc.)
- **Tables:** Use for structured data (tech stack, endpoints, commands)
- **Diagrams:** ASCII art for architecture, tree format for structure
- **Length:** Comprehensive but scannable (typically 100-200 lines)

## Template Reference

Use this general structure:

```markdown
# Project Name

Brief description of what the project does and why it exists.

## Prerequisites

- **Language X.X+** with package manager
- **Other requirements**

## Quick Start

### 1. Setup Backend

\`\`\`bash
cd backend
command to install
command to run
\`\`\`

### 2. Setup Frontend

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## Architecture

\`\`\`
ASCII diagram here
\`\`\`

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | ... |
| Frontend | ... |

### Project Structure

\`\`\`
project/
├── backend/
│   └── ...
├── frontend/
│   └── ...
└── README.md
\`\`\`

## Features

- **Feature 1** — Description
- **Feature 2** — Description

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/... | ... |

## Claude Commands

| Command | Description |
|---------|-------------|
| /command | ... |
```

## Output Confirmation

After creating the README:
1. Confirm the file path where it was written
2. Summarize what sections were included
3. Note any assumptions made
4. Suggest reviewing specific sections that may need refinement
