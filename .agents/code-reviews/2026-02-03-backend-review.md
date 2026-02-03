# Backend Code Review

**Date:** 2026-02-03
**Scope:** `backend/` directory
**Reviewer:** Claude Code

---

## Stats

- Files Reviewed: 12
- Files Modified (in unpushed commits): 18
- Critical Issues: 0
- High Issues: 1
- Medium Issues: 3
- Low Issues: 3

---

## Issues Found

### Issue 1

```
severity: high
file: backend/app/utils/errors.py
line: 76-84
issue: Custom FileNotFoundError shadows built-in exception
detail: The custom FileNotFoundError class shadows Python's built-in FileNotFoundError exception. This can cause confusion and unexpected behavior when catching exceptions, as `except FileNotFoundError` may not behave as expected when imported from this module vs the builtin.
suggestion: Rename to FileExpiredError or ConvertedFileNotFoundError to avoid shadowing the builtin.
```

### Issue 2

```
severity: medium
file: backend/app/services/icon_renderer.py
line: 246
issue: Unused local variable 'height' assigned but never used
detail: Ruff linter reports F841 - the variable `height` is assigned on line 246 but never used. This is dead code that should be removed for clarity.
suggestion: Remove the unused variable assignment or use it as intended.
```

### Issue 3

```
severity: medium
file: backend/tests/test_annotation_replacer.py
line: 150-151
issue: Test expects outdated default color value
detail: Test `test_get_colors_default` expects the default fill color to be `(1.0, 0.5, 0.0)` (orange), but the actual implementation in annotation_replacer.py:37 uses `(0.22, 0.34, 0.65)` (navy blue). This test will always fail because it was not updated when the default color was changed.
suggestion: Update the test expectation to match the current implementation: `assert fill == (0.22, 0.34, 0.65)` and `assert stroke == (0.0, 0.0, 0.0)`.
```

### Issue 4

```
severity: medium
file: backend/app/config.py
line: 43-45
issue: Deprecated Pydantic V2 class-based config
detail: Using class-based `Config` is deprecated in Pydantic V2 and will be removed in V3. The warning shows: "Support for class-based `config` is deprecated, use ConfigDict instead."
suggestion: Replace the nested Config class with model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
```

### Issue 5

```
severity: low
file: backend/app/routers/convert.py
line: 89
issue: Hardcoded relative path for DeploymentMap.pdf
detail: The path `Path("samples/maps/DeploymentMap.pdf")` is a relative path that depends on the current working directory. This could fail if the server is started from a different directory.
suggestion: Use settings-based path or make it relative to project root like other paths in config.py.
```

### Issue 6

```
severity: low
file: backend/app/services/file_manager.py
line: 220-221
issue: Singleton pattern using module-level instance
detail: The `file_manager = FileManager()` singleton at module level means file metadata is stored in memory and lost on restart. This is fine for the current MVP but should be documented as a limitation.
suggestion: Add a comment documenting this limitation and consider persisting metadata to disk for production use.
```

### Issue 7

```
severity: low
file: backend/pyproject.toml
line: N/A
issue: PyPDF2 deprecation warning
detail: PyPDF2 shows a deprecation warning on import: "PyPDF2 is deprecated. Please move to the pypdf library instead." This library is no longer maintained.
suggestion: Consider migrating from PyPDF2 to pypdf (lowercase) in a future update. Note: The codebase primarily uses PyMuPDF for annotation work, so PyPDF2 usage may be limited.
```

---

## Verified Non-Issues

The following were checked but found to be acceptable:

1. **Path traversal in filename sanitization**: `file_manager._sanitize_filename()` properly sanitizes filenames by removing path components and problematic characters.

2. **File upload size validation**: Properly validates file size before storing.

3. **PDF magic number check**: Upload endpoint validates PDF magic bytes before processing.

4. **Error exposure to users**: Exception messages are appropriately generic in HTTP responses, with detailed logging server-side.

5. **CORS configuration**: Origins are configurable via settings, not hardcoded (except default for local dev).

---

## Test Summary

- **113 tests pass** (excluding annotation_replacer)
- **11 tests skipped** (features not yet implemented)
- **8 tests fail** in `test_annotation_replacer.py` (documented as known failures due to test expectations not matching implementation)

---

## Recommendations

### Must Fix (Before Production)
1. Fix Issue 1 (FileNotFoundError shadowing) - potential for subtle bugs
2. Fix Issue 3 (test expectation mismatch) - currently causing test failures

### Should Fix
3. Fix Issue 2 (unused variable) - code quality
4. Fix Issue 4 (Pydantic deprecation) - will break on Pydantic V3
5. Fix Issue 5 (hardcoded path) - maintainability

### Nice to Have
6. Document Issue 6 limitation
7. Plan migration from PyPDF2 (Issue 7)

---

## Code Quality Summary

Overall the backend code is well-structured with:
- Clear separation of concerns (services, routers, models)
- Comprehensive error handling with custom exception classes
- Good logging practices
- Type hints throughout
- Proper configuration management via pydantic-settings

The main issues are test maintenance (outdated expectations) and minor code quality items (unused variable, deprecated patterns).
