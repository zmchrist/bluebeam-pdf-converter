---
description: Run all validation commands in the correct sequence
---

# Full Validation Workflow

Run this command to execute all validation checks in the proper sequence. This comprehensive validation ensures code quality, stability, and readiness for deployment.

## Purpose

This command provides a complete validation pipeline:
1. **Pre-flight**: Verify baseline stability (dependencies, build, tests)
2. **Validate**: Run comprehensive project validation
3. **Code Review**: Technical review for quality and bugs
4. **Code Review Fix**: Address any issues found
5. **System Review**: Analyze implementation against plan
6. **Execution Report**: Generate final implementation report

## Full Validation Sequence

### Step 1: Pre-Flight Check ✅ START HERE
```bash
/validation:pre-flight
```
**Purpose:** Catch any broken baseline issues before proceeding

**Expected result:**
- Backend: ~121 passed, 6 failed (known), 11 skipped
- Frontend: Build succeeds, type check passes
- All expected checks pass

**If this fails:** Fix baseline issues before proceeding to next step

---

### Step 2: Comprehensive Validation
```bash
/validation:validate
```
**Purpose:** Run full project validation suite

**Includes:**
- PDF processing validation
- API endpoint validation
- Icon rendering validation
- File management validation

**Expected result:** All validations pass with no critical issues

---

### Step 3: Code Quality Review
```bash
/validation:code-review
```
**Purpose:** Technical review for bugs, style, and quality

**Checks:**
- Code pattern violations
- Type safety issues
- Error handling completeness
- Test coverage gaps
- Accessibility compliance
- Security considerations

**Expected result:** No critical or blocking issues identified

---

### Step 4: Fix Code Review Issues
```bash
/validation:code-review-fix
```
**Purpose:** Remediate any issues found in code review

**Only needed if:** Code review found issues

**Expected result:** All reported issues fixed or documented as known

---

### Step 5: System Review
```bash
/validation:system-review
```
**Purpose:** Analyze implementation against original plan and architecture

**Checks:**
- Implementation completeness vs plan
- Architectural consistency
- Documentation accuracy
- Process improvements

**Expected result:** Implementation matches plan or improvements documented

---

### Step 6: Execution Report
```bash
/validation:execution-report
```
**Purpose:** Generate final implementation report

**Includes:**
- Validation summary
- Test results
- Code quality metrics
- Known issues
- Recommendations

**Expected result:** Complete report generated for review

---

## Quick Validation (Fast Path)

If you only want baseline verification without full analysis:

```bash
/validation:pre-flight
```

Use full validation for:
- Before major releases
- After significant refactoring
- Before submitting PRs
- When adding new features

## Running Sequentially

**Important:** Run each step and verify success before proceeding to the next:

1. If **Step 1 (Pre-flight)** fails → Fix baseline, re-run Step 1
2. If **Step 2 (Validate)** fails → Investigate and fix, re-run Step 2
3. If **Step 3 (Code Review)** finds issues → Run Step 4 to fix
4. Steps 5-6 are analysis/reporting - no blockers expected

## When to Run Full Validation

- **Always:** Before submitting PRs
- **After major changes:** Feature implementations, refactoring
- **Before releases:** Before deploying to production
- **When unsure:** If you're uncertain about code quality

## Single Command Orchestration

To run all steps in sequence without stopping between them:

```bash
# Backend verification chain
cd backend && \
  uv sync && \
  uv run ruff check . --fix && \
  uv run pytest -x --tb=short && \
  cd ../frontend && \
  npm install && \
  npx tsc --noEmit && \
  npm run build && \
  cd ../backend && \
  uv run pytest --cov=app --cov-report=term-missing
```

Then proceed with individual validation skills:
- `/validation:validate`
- `/validation:code-review`
- `/validation:code-review-fix` (if needed)
- `/validation:system-review`
- `/validation:execution-report`

## Validation Checklist

After running full validation, verify:

- [ ] Pre-flight check: All baseline tests pass
- [ ] Comprehensive validation: No critical issues
- [ ] Code review: No blocking issues
- [ ] Code review fix: Issues resolved or documented
- [ ] System review: Implementation matches plan
- [ ] Execution report: Generated and reviewed

---

## Related Commands

- [`/validation:pre-flight`](./pre-flight.md) - Quick baseline check before starting work
- [`/validation:validate`](./validate.md) - Comprehensive project validation
- [`/validation:code-review`](./code-review.md) - Technical code review
- [`/validation:code-review-fix`](./code-review-fix.md) - Fix review issues
- [`/validation:system-review`](./system-review.md) - Implementation analysis
- [`/validation:execution-report`](./execution-report.md) - Generate final report
