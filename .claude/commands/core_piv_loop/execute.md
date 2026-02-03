---
description: Execute an implementation plan
argument-hint: [path-to-plan]
---

# Execute: Implement from Plan

## Plan to Execute

Read plan file: `$ARGUMENTS`

## Execution Instructions

### 0. Pre-Flight Verification (BEFORE Starting)

Run these checks BEFORE implementing any tasks to ensure a stable baseline:

```bash
# Backend projects
cd backend && uv sync
uv run pytest -x --tb=short

# Frontend projects
cd frontend && npm install
npm run build
```

**If any fail:**
- Fix the issue first, OR
- Document as "known issue" and proceed only if it won't affect your work
- Never start implementation on a broken baseline

### 1. Read and Understand

- Read the ENTIRE plan carefully
- Understand all tasks and their dependencies
- Note the validation commands to run
- Review the testing strategy
- Check the "Known Issues" section for expected failures

### 2. Execute Tasks in Order

For EACH task in "Step by Step Tasks":

#### a. Navigate to the task
- Identify the file and action required
- Read existing related files if modifying

#### b. Implement the task
- Follow the detailed specifications exactly
- Maintain consistency with existing code patterns
- Include proper type hints and documentation
- Add structured logging where appropriate

#### c. Verify as you go
- After each file change, check syntax
- Ensure imports are correct
- Verify types are properly defined

### 3. Implement Testing Strategy

After completing implementation tasks:

- Create all test files specified in the plan
- Implement all test cases mentioned
- Follow the testing approach outlined
- Ensure tests cover edge cases

### 4. Run Validation Commands

Execute validation commands in this order:

**Step 1: Lint and Format (auto-fix what you can)**
```bash
# Python
cd backend && uv run ruff check . --fix

# TypeScript/JavaScript
cd frontend && npm run lint --fix  # if configured
```

**Step 2: Type Checking**
```bash
# Python (if configured)
cd backend && uv run mypy app/

# TypeScript
cd frontend && npx tsc --noEmit
```

**Step 3: Unit Tests**
```bash
# Run each command exactly as specified in plan
```

**Step 4: Integration/E2E Tests**
```bash
# Run each command exactly as specified in plan
```

If any command fails:
- Fix the issue
- Re-run the command
- Continue only when it passes
- Compare against "Known Issues" - some failures may be pre-existing

### 5. Final Verification

Before completing:

- ✅ All tasks from plan completed
- ✅ All tests created and passing
- ✅ All validation commands pass
- ✅ Code follows project conventions
- ✅ Documentation added/updated as needed

## Output Report

Provide summary:

### Completed Tasks
- List of all tasks completed
- Files created (with paths)
- Files modified (with paths)

### Tests Added
- Test files created
- Test cases implemented
- Test results

### Validation Results
```bash
# Output from each validation command
```

### Ready for Commit
- Confirm all changes are complete
- Confirm all validations pass
- Ready for `/commit` command

## Notes

- If you encounter issues not addressed in the plan, document them
- If you need to deviate from the plan, explain why in the execution report
- If tests fail, fix implementation until they pass (unless documented as known failure)
- Don't skip validation steps
- If API signatures changed, search for and update all usages: `grep -r "old_function" --include="*.py"`

## Divergence Documentation

When you must deviate from the plan, document:

```markdown
### Divergence: [Brief description]
- **Planned:** [What the plan specified]
- **Actual:** [What you implemented instead]
- **Reason:** [Why the change was necessary]
- **Type:** [Better approach found | Plan assumption wrong | External constraint]
```

This helps system review identify process improvements.
