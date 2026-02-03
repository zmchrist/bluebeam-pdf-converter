Run comprehensive validation of the Bluebeam PDF Converter project.

Execute the following commands in sequence and report results:

## 1. Backend Linting

```bash
cd backend && uv run ruff check .
```

**Expected:** "All checks passed!" or no output (clean)

## 2. Backend Tests

```bash
cd backend && uv run pytest -v
```

**Expected:** ~132 tests pass, 6 known failures in annotation_replacer (PyMuPDF/PyPDF2 incompatibility), 11 skipped

## 3. Backend Tests with Coverage

```bash
cd backend && uv run pytest --cov=app --cov-report=term-missing
```

**Expected:** Coverage >= 70% for core services

## 4. API Health Check

Start the server if not running:

```bash
cd backend && uv run uvicorn app.main:app --port 8000 &
sleep 2
```

Test health endpoint:

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

**Expected:** JSON with `status: "healthy"`, mapping count (~89), bid icons (70), deployment icons (118)

## 5. API Endpoint Validation

Test upload endpoint (requires sample PDF):

```bash
curl -s -X POST http://localhost:8000/api/upload \
  -F "file=@samples/maps/BidMap.pdf" | python -m json.tool
```

**Expected:** JSON with `upload_id`, `filename`, `annotation_count` (~402)

Test API docs availability:

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/docs
```

**Expected:** HTTP 200

## 6. End-to-End Conversion Test

Run the conversion test script:

```bash
cd backend && uv run python scripts/test_conversion.py
```

**Expected:**
- Upload: BidMap.pdf accepted
- Convert: ~376 annotations converted, ~26 skipped
- Download: Valid PDF output

## 7. Icon Rendering Test (Optional)

Test icon rendering for a specific icon:

```bash
cd backend && uv run python scripts/test_icon_render.py "AP - Cisco MR36H"
```

**Expected:** PDF created at `samples/maps/test_icon_output.pdf`

## 8. Frontend Build

> **Note:** Frontend not yet implemented. Skip this step.

```bash
# cd frontend && npm run build
```

## 9. Cleanup

Stop the server if started:

```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
```

## 10. Summary Report

After all validations complete, provide a summary report with:

| Check | Status | Notes |
|-------|--------|-------|
| Linting | PASS/FAIL | Any warnings |
| Unit Tests | X/Y passed | Known failures excluded |
| Coverage | X% | Target: 70%+ |
| Health Check | PASS/FAIL | Service dependencies |
| API Endpoints | PASS/FAIL | Upload, convert, download |
| E2E Conversion | PASS/FAIL | Annotations converted |
| Frontend | SKIPPED | Not implemented |

**Overall Health:** PASS/FAIL

### Known Issues to Ignore
- 6 test failures in `test_annotation_replacer.py` (PyMuPDF/PyPDF2 fixture incompatibility)
- 11 skipped tests (features not yet implemented)
- ~26 skipped annotations in conversion (legend items, measurements - expected)
