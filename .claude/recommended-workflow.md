# Recommended Implementation Workflow

Step-by-step command workflow for feature implementations.

---

## Quick Reference

```
/validation:pre-flight     → Verify baseline stability
/core_piv_loop:plan-feature → Create implementation plan
/core_piv_loop:execute      → Execute the plan
/validation:code-review     → Review code for bugs
/validation:code-review-fix → Fix found issues
/validation:validate        → Run all checks
/validation:execution-report → Document what was built
/validation:system-review   → Improve the process
/git:commit                 → Commit changes
/git:push                   → Push to remote
```

---

## Full Workflow

### Phase 1: Before You Start

#### 1. Pre-flight Check
```
/validation:pre-flight
```
**Purpose:** Verify the codebase is stable before starting work
- Runs tests to confirm baseline
- Checks for uncommitted changes
- Ensures you're starting from a clean state

**If pre-flight fails:** Fix issues before proceeding

---

### Phase 2: Planning

#### 2. Plan the Feature
```
/core_piv_loop:plan-feature
```
**Purpose:** Create a comprehensive implementation plan
- Analyzes codebase for relevant patterns
- Identifies files to create/modify
- Defines validation criteria
- Outputs plan to `.agents/plans/[feature-name].md`

**Review the plan** before proceeding to execution.

---

### Phase 3: Implementation

#### 3. Execute the Plan
```
/core_piv_loop:execute
```
**Purpose:** Implement the feature according to the plan
- Follows the plan step by step
- Creates/modifies files
- Runs tests as it goes

---

### Phase 4: Quality Assurance

#### 4. Code Review
```
/validation:code-review
```
**Purpose:** Deep analysis of changes for bugs and issues
- Checks for logic errors, security issues, performance problems
- Verifies adherence to codebase patterns
- Outputs report to `.agents/code-reviews/[name].md`

#### 5. Fix Issues (if any found)
```
/validation:code-review-fix [report-file] [scope]
```
**Purpose:** Fix issues identified in code review
- Addresses each issue one by one
- Runs tests to verify fixes
- Runs `/validate` at the end

**Example:**
```
/validation:code-review-fix .agents/code-reviews/phase-5.md "backend services"
```

#### 6. Full Validation
```
/validation:validate
```
**Purpose:** Run all automated checks
- Linting
- Tests with coverage
- API health check
- E2E conversion test

**Must pass before committing.**

---

### Phase 5: Documentation

#### 7. Execution Report
```
/validation:execution-report
```
**Purpose:** Document what was implemented
- Records files changed
- Notes challenges and divergences from plan
- Captures lessons learned
- Outputs to `.agents/execution-reports/[feature-name].md`

#### 8. System Review (Optional but Recommended)
```
/validation:system-review [plan-file] [execution-report]
```
**Purpose:** Meta-analysis to improve the process
- Compares plan vs actual implementation
- Identifies process improvements
- Suggests updates to CLAUDE.md, commands, etc.

**Example:**
```
/validation:system-review .agents/plans/phase-5.md .agents/execution-reports/phase-5.md
```

---

### Phase 6: Commit

#### 9. Commit Changes
```
/git:commit
```
**Purpose:** Stage and commit with proper message

#### 10. Push to Remote
```
/git:push
```
**Purpose:** Push commits to remote repository

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     BEFORE YOU START                        │
├─────────────────────────────────────────────────────────────┤
│  /validation:pre-flight                                     │
│  └── Verify baseline stability                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        PLANNING                             │
├─────────────────────────────────────────────────────────────┤
│  /core_piv_loop:plan-feature                                │
│  └── Create implementation plan                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     IMPLEMENTATION                          │
├─────────────────────────────────────────────────────────────┤
│  /core_piv_loop:execute                                     │
│  └── Build the feature                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    QUALITY ASSURANCE                        │
├─────────────────────────────────────────────────────────────┤
│  /validation:code-review                                    │
│  └── Find bugs and issues                                   │
│                              │                              │
│                              ▼                              │
│  /validation:code-review-fix  (if issues found)             │
│  └── Fix each issue                                         │
│                              │                              │
│                              ▼                              │
│  /validation:validate                                       │
│  └── Run all checks                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DOCUMENTATION                          │
├─────────────────────────────────────────────────────────────┤
│  /validation:execution-report                               │
│  └── Document what was built                                │
│                              │                              │
│                              ▼                              │
│  /validation:system-review  (optional)                      │
│  └── Improve the process                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         COMMIT                              │
├─────────────────────────────────────────────────────────────┤
│  /git:commit                                                │
│  └── Stage and commit changes                               │
│                              │                              │
│                              ▼                              │
│  /git:push                                                  │
│  └── Push to remote                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Shortcuts for Small Changes

For minor fixes or small changes, use the abbreviated workflow:

```
/validation:pre-flight       → Verify stable baseline
(make changes)
/validation:validate         → Run all checks
/git:commit                  → Commit
```

---

## Error Handling

If you encounter errors during any step:

1. Check `.claude/errors.md` for known solutions
2. Debug and fix the issue
3. Document new errors in `errors.md` (per Error Handling Protocol)
4. Re-run the failed step before continuing

---

## Output Locations

| Command | Output Location |
|---------|-----------------|
| plan-feature | `.agents/plans/[feature-name].md` |
| code-review | `.agents/code-reviews/[name].md` |
| execution-report | `.agents/execution-reports/[feature-name].md` |
| system-review | `.agents/system-reviews/[feature-name]-review.md` |
