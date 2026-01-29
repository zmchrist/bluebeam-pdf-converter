# Bluebeam BTX Icon Converter

A web application for converting Bluebeam Revu tool icons (.btx files) from custom "bid icons" to custom "deployment icons" within PDF markup workflows. When estimators mark equipment locations on venue maps (sports arenas, concert halls, festivals) with bid icons during the bidding phase, this tool converts those BTX definitions so the same markup locations automatically display as deployment icons after bid acceptance—eliminating hours of manual re-marking. Built with Python backend (FastAPI) and React frontend.

## Prerequisites

- **Python 3.11+** with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** with npm
- **Git** (optional, for cloning)

## Quick Start

### 1. Clone and Setup Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Backend runs at http://localhost:8000 (API docs at http://localhost:8000/docs)

### 2. Setup Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173

### 3. Open the App

Navigate to **http://localhost:5173** in your browser. Upload your BTX files and start converting!

## Architecture

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐
│ React/Vue.js    │ ◄───────────────► │ Flask/FastAPI   │
│   Port 5173     │                    │   Port 8000     │
└─────────────────┘                    └────────┬────────┘
                                                │
                                       ┌─────────────────┐
                                       │  BTX Processing │
                                       │  XML + zlib     │
                                       └─────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, Flask/FastAPI, XML parsing, zlib compression |
| Frontend | React/Vue.js, Drag-drop file upload, Progress indicators |
| Processing | BTX XML parsing, Icon mapping, File reconstruction |

### Project Structure

```
Bluebeam Conversion/
├── backend/
│   ├── app/
│   │   ├── main.py           # Flask/FastAPI entry point
│   │   ├── btx_parser.py     # BTX XML parsing and decompression
│   │   ├── icon_mapper.py    # Bid to deployment icon mapping
│   │   ├── file_processor.py # File upload/download handling
│   │   └── routers/          # API endpoints
│   │       ├── upload.py     # File upload endpoint
│   │       └── convert.py    # Conversion endpoint
│   └── tests/                # pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload/   # Drag-drop upload interface
│   │   │   ├── IconPreview/  # Visual icon mapping preview
│   │   │   └── BatchProcess/ # Batch processing controls
│   │   ├── pages/            # Route pages
│   │   └── lib/              # Utilities
│   └── package.json
├── toolchest/                # BTX files and Gear Icons
├── samples/                  # Sample icons and maps
│   ├── icons/                # bidIcons and deploymentIcons
│   └── maps/                 # BidMap.pdf and DeploymentMap.pdf
├── bluebeamPlan.md          # Project plan document
└── README.md
```

## Features

- **BTX File Conversion** — Convert bid icons to deployment icons with one click
- **Batch Processing** — Upload and convert multiple BTX files simultaneously
- **Visual Preview** — See bid → deployment icon mappings before conversion
- **Pattern Matching** — Automatic icon set recognition and mapping
- **Progress Tracking** — Real-time conversion progress indicators
- **Download Management** — Download converted files individually or as batch

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload BTX files for conversion |
| POST | `/api/convert` | Convert bid icons to deployment icons |
| GET | `/api/preview/{file_id}` | Preview icon mappings before conversion |
| GET | `/api/download/{file_id}` | Download converted BTX file |
| POST | `/api/batch-convert` | Batch convert multiple BTX files |

Full API documentation available at http://localhost:8000/docs when backend is running.

## Claude Commands

Slash commands for Claude Code to assist with development workflows. The AI coding workflow used to build this application follows the PIV (Prime, Implement, Validate) loop shown below:

![PIV Loop Diagram](PIVLoopDiagram.png)

### Planning & Execution
| Command | Description |
|---------|-------------|
| `/core_piv_loop:prime` | Load project context and codebase understanding |
| `/core_piv_loop:plan-feature` | Create comprehensive implementation plan with codebase analysis |
| `/core_piv_loop:execute` | Execute an implementation plan step-by-step |

### Validation
| Command | Description |
|---------|-------------|
| `/validation:validate` | Run full validation: tests, linting, coverage, frontend build |
| `/validation:code-review` | Technical code review on changed files |
| `/validation:code-review-fix` | Fix issues found in code review |
| `/validation:execution-report` | Generate report after implementing a feature |
| `/validation:system-review` | Analyze implementation vs plan for process improvements |

### Bug Fixing
| Command | Description |
|---------|-------------|
| `/github_bug_fix:rca` | Create root cause analysis document for a GitHub issue |
| `/github_bug_fix:implement-fix` | Implement fix based on RCA document |

### Misc
| Command | Description |
|---------|-------------|
| `/commit` | Create atomic commit with appropriate tag (feat, fix, docs, etc.) |
| `/init-project` | Install dependencies, start backend and frontend servers |
| `/create-prd` | Generate Product Requirements Document from conversation |
