# Plan: Commit + Cleanup (3 Parts)

## Overview
Three sequential commits: (1) commit pending work, (2) add background file cleanup, (3) migrate PyPDF2 to pypdf.

---

## Part 1: Commit Uncommitted Work

### Step 1.1: Add BidMap2 to `.gitignore`
**File:** `.gitignore` (line 47, after existing test output patterns)
```
samples/maps/BidMap2*.pdf
```

### Step 1.2: Stage and commit all pending work

**Stage modified tracked files (10):**
- `.gitignore`, `.claude/memories.md`, `CLAUDE.md`, `README.md`
- `backend/app/services/icon_config.py`, `annotation_replacer.py`, `icon_renderer.py`
- `backend/tests/test_icon_renderer.py`, `backend/scripts/test_conversion.py`
- `backend/data/mapping.md`

**Stage untracked files:**
- `.agents/code-reviews/device-id-assignment-system.md`
- `.agents/execution-reports/device-id-assignment-system.md`
- `.agents/plans/automated-icon-visual-verification.md`
- `.agents/plans/device-id-assignment-system.md`
- `.agents/system-reviews/device-id-assignment-system-review.md`
- `.claude/images/` (4 reference PNGs)
- `backend/scripts/icon_tuner/` (5 files)
- `backend/scripts/run_icon_tuner.py`

**Do NOT stage:** `samples/maps/BidMap2*.pdf` (now gitignored)

**Commit message:** `feat: device ID assignment, legend deletion, and icon tuner tooling`

---

## Part 2: Background File Cleanup

### Step 2.1: Modify `backend/app/main.py`

Add a FastAPI `lifespan` context manager that:
1. Runs `file_manager.cleanup_expired()` once at startup (handle orphans)
2. Starts an `asyncio.create_task` that runs cleanup every 15 minutes
3. Cancels the task on shutdown

**New imports:** `asyncio`, `contextlib.asynccontextmanager`, `app.services.file_manager.file_manager`

**New code (before `app = FastAPI(...)`):**
```python
CLEANUP_INTERVAL_SECONDS = 15 * 60

async def _periodic_cleanup() -> None:
    while True:
        try:
            count = file_manager.cleanup_expired()
            if count > 0:
                logger.info(f"Background cleanup removed {count} expired file(s)")
        except Exception as e:
            logger.error(f"Error during background cleanup: {e}")
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup cleanup
    try:
        count = file_manager.cleanup_expired()
        if count > 0:
            logger.info(f"Startup cleanup removed {count} expired file(s)")
    except Exception as e:
        logger.error(f"Error during startup cleanup: {e}")
    # Start periodic task
    cleanup_task = asyncio.create_task(_periodic_cleanup())
    logger.info("Background file cleanup task started (interval: 15 minutes)")
    yield
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
```

**Modify:** `app = FastAPI(..., lifespan=lifespan)`

**Reuses existing code:** `file_manager.cleanup_expired()` in `backend/app/services/file_manager.py:202`

**Commit message:** `feat: add background cleanup task for expired temporary files`

---

## Part 3: PyPDF2 to pypdf Migration

### Step 3.1: Update dependencies
- `backend/pyproject.toml`: `"PyPDF2>=3.0.0"` -> `"pypdf>=4.0.0"`
- `backend/requirements.txt`: `PyPDF2>=3.0.0` -> `pypdf>=4.0.0` (remove commented `pypdf` line)
- Run `uv sync`

### Step 3.2: Update imports (all `PyPDF2` -> `pypdf`, `PyPDF2.generic` -> `pypdf.generic`)

**Production code (3 files):**
| File | Import changes |
|------|---------------|
| `backend/app/services/pdf_parser.py` | Line 8 |
| `backend/app/services/annotation_replacer.py` | Lines 15-23, line 173 |
| `backend/app/services/icon_renderer.py` | Lines 18-27 |

**Test code (1 file):**
| File | Import changes |
|------|---------------|
| `backend/tests/test_icon_renderer.py` | Line 8 |

**Scripts (7 files):**
| File | Import changes |
|------|---------------|
| `backend/scripts/test_icon_render.py` | Lines 17-25 |
| `backend/scripts/test_single_icon.py` | Lines 19-26 |
| `backend/scripts/test_mr36h_icon.py` | Lines 19-26 |
| `backend/scripts/test_clone_icon.py` | Lines 12-17 |
| `backend/scripts/test_batch_clone.py` | Lines 9-13 |
| `backend/scripts/diagnose_annotations.py` | Line 20 |
| `backend/scripts/icon_tuner/icon_comparator.py` | Lines 14-22 |

**No changes needed:** `validate_fix.py` (uses pymupdf), `test_conversion.py` (imports from app.services)

**Commit message:** `chore: migrate from deprecated PyPDF2 to pypdf`

---

## Verification

After all 3 commits:

1. **Tests pass:** `cd backend && uv run pytest` -> 147 passed, 5 failed (known), 11 skipped
2. **No PyPDF2 references:** `grep -r "PyPDF2" backend/app/ backend/tests/ backend/scripts/ --include="*.py"` -> zero matches
3. **No deprecation warning** in test output
4. **Server starts:** `uv run uvicorn app.main:app --port 8000` -> logs show "Background file cleanup task started"
5. **Clean git status:** only ignored BidMap2 files remain untracked
