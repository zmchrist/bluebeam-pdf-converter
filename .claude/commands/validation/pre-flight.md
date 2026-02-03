---
description: Verify baseline stability before starting implementation
---

# Pre-Flight Validation

Run this command before starting any new feature implementation to ensure the codebase baseline is stable.

## Purpose

Catching broken builds or failing tests BEFORE you start implementing prevents:
- Wasted debugging time on pre-existing issues
- Confusion about whether new code caused failures
- Blocked PRs due to unrelated test failures

## Validation Steps

### 1. Backend Verification

```bash
cd backend

# Step 1: Sync dependencies
uv sync

# Step 2: Quick lint check
uv run ruff check . --fix

# Step 3: Smoke test (stops on first failure)
uv run pytest -x --tb=short
```

**Expected result:** ~121 passed, 6 failed (known), 11 skipped

**Known failures (do not block):**
- `test_annotation_replacer.py` - 6 failures due to PyMuPDF/PyPDF2 fixture incompatibility

### 2. Frontend Verification

```bash
cd frontend

# Step 1: Install dependencies
npm install

# Step 2: Type check
npx tsc --noEmit

# Step 3: Build verification
npm run build
```

**Expected result:** All commands succeed with no errors

### 3. Project Structure Check

Verify no orphaned directories or test artifacts:

```bash
# Should NOT exist
ls backend/backend/     # Duplicate directory
ls frontend/frontend/   # Duplicate directory

# Check for test output files that shouldn't be committed
ls samples/maps/*_converted_*.pdf
```

## Output

After running pre-flight validation, report:

### Pre-Flight Status

| Check | Status | Notes |
|-------|--------|-------|
| Backend uv sync | ✓/✗ | |
| Backend ruff | ✓/✗ | # auto-fixed |
| Backend pytest | ✓/✗ | X passed, Y failed (Z known) |
| Frontend npm install | ✓/✗ | |
| Frontend tsc | ✓/✗ | |
| Frontend build | ✓/✗ | |
| No orphan directories | ✓/✗ | |

### Blockers Found

If any unexpected failures:
- [ ] List each blocker
- [ ] Determine if it blocks your planned work
- [ ] Fix before proceeding OR document in plan's "Known Issues"

### Ready to Proceed

- [ ] All expected checks pass
- [ ] Known failures documented
- [ ] No unexpected blockers

## When to Run

- **Always:** Before starting any new feature implementation
- **After pulls:** When pulling changes from remote
- **After dependency changes:** When pyproject.toml or package.json changes
- **Before PRs:** To ensure clean baseline for reviewers
