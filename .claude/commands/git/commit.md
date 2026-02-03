# Commit: Stage and Commit Changes

Stage relevant files and create a commit with a descriptive message.

## Process

1. Run `git status` to see all changed, staged, and untracked files
2. Run `git diff` to review unstaged changes
3. Stage appropriate files using `git add <files>` (prefer specific files over `git add .`)
4. Run `git diff --cached` to confirm what will be committed
5. Create commit with a concise message using conventional commit format

## Commit Message Format

```
<tag>: <short description>

<optional body with details>

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Tags

| Tag | Use When |
|-----|----------|
| `feat` | Adding new functionality |
| `fix` | Fixing a bug |
| `docs` | Documentation only changes |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks, dependencies, config |

## Guidelines

- **Be specific when staging** - prefer `git add file1.py file2.py` over `git add .`
- **Don't commit sensitive files** - skip `.env`, credentials, secrets
- **Keep commits atomic** - one logical change per commit
- **Write meaningful messages** - focus on "why" not just "what"
- **Review before committing** - always check `git diff --cached`
