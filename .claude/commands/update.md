# Update: Sync Project Documentation

Update project documentation files (PRD.md, CLAUDE.md, README.md, memories.md) based on recent changes and current context.

## Philosophy

**Not every file needs updating every time.** Use judgment to determine which files have relevant new information:

- **CLAUDE.md** - Update when: project structure changes, new commands added, tech stack changes, code conventions evolve
- **README.md** - Update when: setup instructions change, new features added, architecture changes, API endpoints change
- **PRD.md** - Update when: requirements change, features completed/added, scope changes, implementation phases progress
- **memories.md** - Update when: significant work completed, key discoveries made, blockers encountered/resolved

## Process

### Step 1: Gather Context

Analyze the current state by checking:
1. `git status` - What files have changed?
2. `git log --oneline -10` - What was recently committed?
3. `git diff --stat HEAD~5` - Scope of recent changes
4. Read current versions of all documentation files

### Step 2: Determine What Needs Updating

For each file, ask:

**CLAUDE.md:**
- [ ] New services or modules added?
- [ ] Project structure changed?
- [ ] New commands or scripts?
- [ ] Tech stack additions/removals?
- [ ] Testing approach changed?
- [ ] Implementation status changed?

**README.md:**
- [ ] Setup instructions outdated?
- [ ] New features to highlight?
- [ ] Architecture diagram needs update?
- [ ] API endpoints changed?
- [ ] New prerequisites?

**PRD.md:**
- [ ] Implementation phase completed?
- [ ] New features in scope?
- [ ] Requirements clarified?
- [ ] Success criteria met?
- [ ] Technical approach changed?

**memories.md:**
- [ ] Session work not yet documented?
- [ ] Key decisions made?
- [ ] Blockers encountered or resolved?
- [ ] Files created/modified significantly?

### Step 3: Update Only What's Needed

For each file that needs updates:

1. Read the current file
2. Identify the specific sections that need changes
3. Make targeted edits (don't rewrite unchanged sections)
4. Preserve existing structure and formatting
5. Update timestamps/version info where applicable

### Step 4: Report Summary

After updates, provide a summary:
```
## Documentation Update Summary

### Files Updated:
- CLAUDE.md: [brief description of changes]
- README.md: [brief description of changes]

### Files Unchanged (no relevant updates):
- PRD.md: Requirements unchanged
- memories.md: Already current

### Key Changes Documented:
- [bullet list of main updates made]
```

## Update Guidelines

### CLAUDE.md Updates
- Keep it as the "single source of truth" for developers
- Update implementation status markers (Phase 1-4)
- Add new services to Project Structure
- Update test counts if significantly changed
- Add new scripts to Commands section

### README.md Updates
- Keep setup instructions accurate and tested
- Update feature list as features are completed
- Ensure architecture diagram matches reality
- Update API endpoint table as endpoints change

### PRD.md Updates
- Mark completed phases with checkmarks
- Update implementation status sections
- Add lessons learned to appropriate sections
- Keep scope clear (in/out of scope)

### memories.md Updates
- Add new session entry at top
- Update "Last Updated" date
- Mark resolved questions as answered
- Update "Next Steps" section

## When NOT to Update

Skip updating a file if:
- No changes relate to that file's purpose
- Only trivial changes occurred (typos, formatting)
- The file was just updated in the current session
- Changes are temporary/experimental

## Output

After completing updates, summarize:
1. Which files were updated and why
2. Which files were skipped and why
3. Any discrepancies found between docs and actual state
4. Suggestions for future documentation improvements
