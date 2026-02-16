# Feature: Device ID Assignment System

The following plan should be complete, but its important that you validate documentation and codebase patterns and task sanity before you start implementing.

Pay special attention to naming of existing utils types and models. Import from the right files etc.

## Feature Description

Add automatic ID assignment to deployment icons during PDF conversion. Each device type gets a unique prefix letter with sequential numbering starting at 100. For example:
- First MR36H AP → `j100`, second → `j101`, third → `j102`
- First MV93X camera → `100a`, second → `101a` (number-first format)
- First Artist hardline → `bb100`, second → `bb101` (double-letter prefix)

The ID is displayed in the white ID box at the top of each icon in the converted PDF.

## User Story

As a deployment technician
I want each device on the converted map to have a unique sequential ID
So that I can easily reference specific devices during installation and documentation

## Problem Statement

Currently, all converted icons display a hardcoded "j100" ID label. This provides no differentiation between devices and doesn't follow the company's device identification standards where each device type has a specific prefix and sequential numbering.

## Solution Statement

Implement a configuration-driven ID assignment system that:
1. Maps deployment subjects to their ID prefix configuration
2. Tracks counters per device type during conversion
3. Generates sequential IDs following three formats: prefix-first (`j100`), number-first (`100a`), and double-letter (`aa100`)
4. Passes dynamic IDs to the icon renderer instead of hardcoded values

## Feature Metadata

**Feature Type**: New Capability
**Estimated Complexity**: Medium
**Primary Systems Affected**: icon_config.py, annotation_replacer.py
**Dependencies**: None (uses existing PyPDF2 rendering)

---

## CONTEXT REFERENCES

### Relevant Codebase Files - MUST READ BEFORE IMPLEMENTING

| File | Lines | Why Read |
|------|-------|----------|
| `backend/app/services/icon_config.py` | 1-674 | Contains ICON_CATEGORIES, CATEGORY_DEFAULTS, ICON_OVERRIDES patterns to mirror for ID config |
| `backend/app/services/annotation_replacer.py` | 120-148, 285-420 | Shows where "j100" is hardcoded (line 390), understand replacement flow |
| `backend/app/services/icon_renderer.py` | 158-217, 452-464 | Shows how id_label is rendered in PDF |
| `backend/tests/test_icon_renderer.py` | 19-169 | Test patterns for icon config (TestIconConfig class) |

### New Files to Create

None - all changes go in existing files.

### Files to Modify

| File | Changes |
|------|---------|
| `backend/app/services/icon_config.py` | Add `ID_PREFIX_CONFIG` dict, `IconIdAssigner` class, `get_id_prefix_config()` helper |
| `backend/app/services/annotation_replacer.py` | Import `IconIdAssigner`, create instance, use dynamic IDs |
| `backend/tests/test_icon_renderer.py` | Add `TestIconIdAssigner` class with ~15 tests |

### Patterns to Follow

**Configuration Dictionary Pattern** (from icon_config.py lines 36-144):
```python
ICON_CATEGORIES: dict[str, str] = {
    "AP - Cisco MR36H": "APs",
    # ... 87 entries
}
```

**Helper Function Pattern** (from icon_config.py lines 590-620):
```python
def get_icon_config(subject: str) -> dict:
    """Get merged configuration for an icon."""
    category = ICON_CATEGORIES.get(subject)
    if not category:
        return {}
    # ... merge defaults + overrides
    return config
```

**Test Class Pattern** (from test_icon_renderer.py lines 19-169):
```python
class TestIconConfig:
    """Tests for icon configuration retrieval."""

    def test_get_config_known_icon(self):
        config = get_icon_config("AP - Cisco MR36H")
        assert config is not None
        assert "category" in config
```

---

## IMPLEMENTATION PLAN

### Phase 1: Add ID Configuration

Add the ID prefix configuration dictionary and helper function to `icon_config.py`.

### Phase 2: Create IconIdAssigner Class

Add a class that tracks counters and generates sequential IDs during conversion.

### Phase 3: Integrate with Annotation Replacer

Modify `annotation_replacer.py` to use dynamic IDs instead of hardcoded "j100".

### Phase 4: Testing

Add comprehensive tests for the new ID assignment functionality.

---

## STEP-BY-STEP TASKS

### Task 1: ADD ID_PREFIX_CONFIG to `icon_config.py`

**IMPLEMENT**: Add new configuration dictionary after ICON_IMAGE_PATHS (around line 588)

```python
# ID prefix configuration for device types
# format: "prefix_first" = "j100", "number_first" = "100a"
ID_PREFIX_CONFIG: dict[str, dict] = {
    # === Access Points (prefix first: j100, k100, etc.) ===
    "AP - Cisco MR36H": {"prefix": "j", "start": 100},
    "AP - Cisco MR78": {"prefix": "k", "start": 100},
    "AP - Cisco 9166I": {"prefix": "l", "start": 100},
    "AP - Cisco 9166D": {"prefix": "m", "start": 100},
    "AP - Cisco 9120": {"prefix": "n", "start": 100},
    "AP - Cisco Marlin 4": {"prefix": "o", "start": 100},
    "AP - Cisco DB10": {"prefix": "p", "start": 100},

    # === Cameras (number first: 100a, 101a, etc.) ===
    "CCTV - Cisco MV93X": {"prefix": "a", "start": 100, "format": "number_first"},
    "CCTV - AXIS P5655-E": {"prefix": "b", "start": 100, "format": "number_first"},
    "CCTV - AXIS M5526-E": {"prefix": "c", "start": 100, "format": "number_first"},

    # === Hardlines (double letter prefix: aa100, bb100, etc.) ===
    "HL - Access Control": {"prefix": "aa", "start": 100},
    "HL - Artist": {"prefix": "bb", "start": 100},
    "HL - Audio": {"prefix": "cc", "start": 100},
    "HL - CCTV": {"prefix": "dd", "start": 100},
    "HL - Clair": {"prefix": "ee", "start": 100},
    "HL - Emergency Announce System": {"prefix": "ff", "start": 100},
    "HL - General Internet": {"prefix": "gg", "start": 100},
    "HL - IPTV": {"prefix": "hh", "start": 100},
    "HL - Lighting": {"prefix": "ii", "start": 100},
    "HL - Media": {"prefix": "jj", "start": 100},
    "HL - PoS": {"prefix": "kk", "start": 100},
    "HL - Production": {"prefix": "ll", "start": 100},
    "HL - Radios": {"prefix": "mm", "start": 100},
    "HL - Sponsor": {"prefix": "nn", "start": 100},
    "HL - Streaming": {"prefix": "oo", "start": 100},
    "HL - Video": {"prefix": "pp", "start": 100},

    # === P2Ps (single letter prefix: s100, t100, etc.) ===
    "P2P - Ubiquiti NanoBeam": {"prefix": "s", "start": 100},
    "P2P - Ubiquiti LiteAP": {"prefix": "t", "start": 100},
    "P2P - Ubiquiti Wave Nano": {"prefix": "u", "start": 100},
    "P2P - Ubiquiti Wave Pico": {"prefix": "v", "start": 100},
    "P2P - Ubiquiti Wave AP Micro": {"prefix": "w", "start": 100},
    "P2P - Ubiquiti GigaBeam": {"prefix": "x", "start": 100},
    "P2P - Ubiquiti GigaBeam LR": {"prefix": "y", "start": 100},

    # === Switches (single letter, various starts for independent counters) ===
    "SW - Cisco Micro 4P": {"prefix": "a", "start": 100},
    "SW - Fortinet 108F 8P": {"prefix": "b", "start": 100},
    "SW - Cisco 9200 12P": {"prefix": "c", "start": 100},
    "SW - Cisco 9300X 24X": {"prefix": "d", "start": 300},
    "SW - Cisco 9300 12X36M": {"prefix": "d", "start": 500},
    "SW - Cisco 9300X 24Y": {"prefix": "d", "start": 700},
    "SW - Cisco 9500 48Y4C": {"prefix": "d", "start": 900},

    # === IDFs (e prefix, various starts) ===
    "SW - IDF Cisco 9300 24X": {"prefix": "e", "start": 100},
    "SW - IDF Cisco 9300X 24X": {"prefix": "e", "start": 300},
    "SW - IDF Cisco 9300 12X36M": {"prefix": "e", "start": 500},
    "SW - IDF Cisco 9300X 24Y": {"prefix": "e", "start": 700},
    "SW - IDF Cisco 9500 48Y4C": {"prefix": "e", "start": 900},

    # === NOCs (all share f prefix, same counter) ===
    "DIST - Micro NOC": {"prefix": "f", "start": 100},
    "DIST - Mini NOC": {"prefix": "f", "start": 100},
    "DIST - Standard NOC": {"prefix": "f", "start": 100},
    "DIST - Mega NOC": {"prefix": "f", "start": 100},
    "DIST - Pelican NOC": {"prefix": "f", "start": 100},
}
```

**PATTERN**: Mirror ICON_CATEGORIES structure (lines 36-144)
**VALIDATE**: `python -c "from app.services.icon_config import ID_PREFIX_CONFIG; print(f'{len(ID_PREFIX_CONFIG)} prefixes configured')"`

---

### Task 2: ADD get_id_prefix_config helper to `icon_config.py`

**IMPLEMENT**: Add after get_brand_for_icon() function (after line 674)

```python
def get_id_prefix_config(subject: str) -> dict | None:
    """
    Get ID prefix configuration for a deployment subject.

    Args:
        subject: Deployment subject name (e.g., "AP - Cisco MR36H")

    Returns:
        Dict with prefix config or None if no ID configured.
        Example: {"prefix": "j", "start": 100, "format": "prefix_first"}
    """
    return ID_PREFIX_CONFIG.get(subject)
```

**PATTERN**: Mirror get_icon_config() signature (lines 590-620)
**VALIDATE**: `python -c "from app.services.icon_config import get_id_prefix_config; print(get_id_prefix_config('AP - Cisco MR36H'))"`

---

### Task 3: ADD IconIdAssigner class to `icon_config.py`

**IMPLEMENT**: Add after get_id_prefix_config() function

```python
class IconIdAssigner:
    """
    Assigns sequential IDs to icons during PDF conversion.

    Each device type has a unique prefix and starting number.
    Counters are tracked independently for each prefix+start combination.

    Example:
        assigner = IconIdAssigner()
        assigner.get_next_id("AP - Cisco MR36H")  # Returns "j100"
        assigner.get_next_id("AP - Cisco MR36H")  # Returns "j101"
        assigner.get_next_id("CCTV - Cisco MV93X")  # Returns "100a" (number-first format)
    """

    def __init__(self):
        """Initialize with empty counters."""
        self._counters: dict[str, int] = {}

    def get_next_id(self, deployment_subject: str) -> str | None:
        """
        Get next sequential ID for a deployment subject.

        Args:
            deployment_subject: Deployment subject name (e.g., "AP - Cisco MR36H")

        Returns:
            Sequential ID string (e.g., "j100", "100a", "aa100") or None if no ID configured.
        """
        config = ID_PREFIX_CONFIG.get(deployment_subject)
        if not config:
            return None

        prefix = config["prefix"]
        start = config["start"]
        format_type = config.get("format", "prefix_first")

        # Counter key includes start to handle d100/d300/d500 independently
        counter_key = f"{prefix}_{start}"

        if counter_key not in self._counters:
            self._counters[counter_key] = start
        else:
            self._counters[counter_key] += 1

        current_num = self._counters[counter_key]

        if format_type == "number_first":
            return f"{current_num}{prefix}"
        else:
            return f"{prefix}{current_num}"

    def reset(self):
        """Reset all counters for a new conversion."""
        self._counters.clear()

    def get_current_counts(self) -> dict[str, int]:
        """Get current counter values (for debugging/logging)."""
        return self._counters.copy()
```

**PATTERN**: Similar to how IconRenderer is structured (class with state)
**VALIDATE**:
```bash
python -c "
from app.services.icon_config import IconIdAssigner
a = IconIdAssigner()
print(a.get_next_id('AP - Cisco MR36H'))  # j100
print(a.get_next_id('AP - Cisco MR36H'))  # j101
print(a.get_next_id('CCTV - Cisco MV93X'))  # 100a
print(a.get_next_id('HL - Artist'))  # bb100
a.reset()
print(a.get_next_id('AP - Cisco MR36H'))  # j100 again
"
```

---

### Task 4: UPDATE AnnotationReplacer.__init__ in `annotation_replacer.py`

**IMPLEMENT**: Add IconIdAssigner initialization (after line 73)

**IMPORTS**: Add at top of file (around line 28):
```python
from app.services.icon_config import IconIdAssigner
```

**MODIFY** `__init__` method to add:
```python
def __init__(
    self,
    mapping_parser: MappingParser,
    btx_loader: BTXReferenceLoader,
    appearance_extractor: "AppearanceExtractor | None" = None,
    icon_renderer: "IconRenderer | None" = None,
):
    # ... existing code ...
    self.icon_renderer = icon_renderer
    self.id_assigner = IconIdAssigner()  # ADD THIS LINE
```

**PATTERN**: Mirror how icon_renderer is stored (line 73)
**VALIDATE**: `python -c "from app.services.annotation_replacer import AnnotationReplacer; print('Import OK')"`

---

### Task 5: UPDATE replace_annotations() to reset counter in `annotation_replacer.py`

**IMPLEMENT**: Add reset call at start of replace_annotations() (after line 304, before processing)

```python
def replace_annotations(
    self,
    input_pdf: Path,
    output_pdf: Path,
) -> tuple[int, int, list[str]]:
    """..."""
    converted_count = 0
    skipped_count = 0
    skipped_subjects: list[str] = []

    # Reset ID counters for new conversion
    self.id_assigner.reset()  # ADD THIS LINE

    if not input_pdf.exists():
        # ... rest of method
```

**PATTERN**: Clean state at start of each conversion
**GOTCHA**: Must reset before processing to ensure consistent IDs per PDF

---

### Task 6: UPDATE replace_annotations() to use dynamic IDs in `annotation_replacer.py`

**IMPLEMENT**: Replace hardcoded "j100" at line 390-391

**BEFORE** (line 389-391):
```python
# Try rich icon rendering first
appearance_ref = self._render_rich_icon(
    writer, deployment_subject, rect, id_label="j100"
)
```

**AFTER**:
```python
# Get dynamic ID for this device (or empty string if none configured)
id_label = self.id_assigner.get_next_id(deployment_subject) or ""

# Try rich icon rendering first
appearance_ref = self._render_rich_icon(
    writer, deployment_subject, rect, id_label=id_label
)
```

**GOTCHA**: Use `or ""` to handle None return (devices without IDs get empty label)
**VALIDATE**: Run conversion script and check output PDF for sequential IDs

---

### Task 7: ADD TestIconIdAssigner class to `test_icon_renderer.py`

**IMPLEMENT**: Add new test class after TestIconRendererIntegration (around line 400)

```python
class TestIconIdAssigner:
    """Tests for IconIdAssigner service."""

    def test_init_empty_counters(self):
        """Test assigner initializes with empty counters."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner._counters == {}

    def test_get_next_id_ap_prefix_first(self):
        """Test AP icons get j-prefix IDs."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("AP - Cisco MR36H") == "j100"
        assert assigner.get_next_id("AP - Cisco MR36H") == "j101"
        assert assigner.get_next_id("AP - Cisco MR36H") == "j102"

    def test_get_next_id_camera_number_first(self):
        """Test cameras get number-first format (100a, 101a)."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("CCTV - Cisco MV93X") == "100a"
        assert assigner.get_next_id("CCTV - Cisco MV93X") == "101a"
        assert assigner.get_next_id("CCTV - Cisco MV93X") == "102a"

    def test_get_next_id_hardline_double_letter(self):
        """Test hardlines get double-letter prefix (bb100)."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("HL - Artist") == "bb100"
        assert assigner.get_next_id("HL - Artist") == "bb101"

    def test_get_next_id_p2p_single_letter(self):
        """Test P2Ps get single-letter prefix."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("P2P - Ubiquiti NanoBeam") == "s100"
        assert assigner.get_next_id("P2P - Ubiquiti GigaBeam") == "x100"

    def test_get_next_id_switches_independent_counters(self):
        """Test switches with shared prefix but different starts increment independently."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        # d prefix with different starts
        assert assigner.get_next_id("SW - Cisco 9300X 24X") == "d300"
        assert assigner.get_next_id("SW - Cisco 9300 12X36M") == "d500"
        assert assigner.get_next_id("SW - Cisco 9300X 24X") == "d301"
        assert assigner.get_next_id("SW - Cisco 9300 12X36M") == "d501"

    def test_get_next_id_nocs_share_counter(self):
        """Test all NOCs share same f100 counter."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("DIST - Micro NOC") == "f100"
        assert assigner.get_next_id("DIST - Mini NOC") == "f101"
        assert assigner.get_next_id("DIST - Standard NOC") == "f102"

    def test_get_next_id_unknown_returns_none(self):
        """Test unknown device returns None."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("Unknown Device") is None
        assert assigner.get_next_id("PWR - EcoFlow Battery") is None  # No ID configured

    def test_reset_clears_counters(self):
        """Test reset clears all counters."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assigner.get_next_id("AP - Cisco MR36H")
        assigner.get_next_id("AP - Cisco MR36H")
        assigner.reset()
        assert assigner._counters == {}
        assert assigner.get_next_id("AP - Cisco MR36H") == "j100"

    def test_get_current_counts(self):
        """Test get_current_counts returns copy of counters."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assigner.get_next_id("AP - Cisco MR36H")
        counts = assigner.get_current_counts()
        assert counts == {"j_100": 100}
        # Verify it's a copy
        counts["j_100"] = 999
        assert assigner._counters["j_100"] == 100

    def test_multiple_device_types_independent(self):
        """Test different device types have independent counters."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("AP - Cisco MR36H") == "j100"
        assert assigner.get_next_id("AP - Cisco MR78") == "k100"
        assert assigner.get_next_id("AP - Cisco MR36H") == "j101"
        assert assigner.get_next_id("AP - Cisco MR78") == "k101"

    def test_idf_independent_counters(self):
        """Test IDF switches have independent e-prefix counters."""
        from app.services.icon_config import IconIdAssigner
        assigner = IconIdAssigner()
        assert assigner.get_next_id("SW - IDF Cisco 9300 24X") == "e100"
        assert assigner.get_next_id("SW - IDF Cisco 9300X 24X") == "e300"
        assert assigner.get_next_id("SW - IDF Cisco 9300 24X") == "e101"
```

**IMPORTS**: Add at top of test file:
```python
from app.services.icon_config import IconIdAssigner
```

**PATTERN**: Mirror TestIconConfig test structure (lines 19-169)
**VALIDATE**: `uv run pytest tests/test_icon_renderer.py::TestIconIdAssigner -v`

---

## TESTING STRATEGY

### Unit Tests (Task 7)

13 tests covering:
- Initialization
- Prefix-first format (APs, P2Ps, Switches)
- Number-first format (Cameras)
- Double-letter prefix (Hardlines)
- Independent counters for shared prefixes
- NOC shared counter
- Unknown device handling
- Reset functionality
- Current counts retrieval

### Integration Test

Run full conversion and verify IDs in output PDF:
```bash
uv run python scripts/test_conversion.py
# Open output PDF and verify:
# - First MR36H shows "j100"
# - Sequential MR36Hs show j101, j102, etc.
```

### Edge Cases

- Device with no ID config → empty ID label (graceful handling)
- Mixed device types → independent counters
- Reset between conversions → IDs start fresh

### Known Issues

- **5 pre-existing failures** in `test_annotation_replacer.py` (PyMuPDF/PyPDF2 fixture incompatibility) - do not block this feature
- **34 tests pass** in `test_icon_renderer.py` - our new tests will add to this

---

## VALIDATION COMMANDS

### Level 1: Syntax & Import Check

```bash
cd backend
python -c "from app.services.icon_config import ID_PREFIX_CONFIG, IconIdAssigner, get_id_prefix_config; print('Imports OK')"
python -c "from app.services.annotation_replacer import AnnotationReplacer; print('Replacer OK')"
```

### Level 2: Unit Tests

```bash
cd backend
uv run pytest tests/test_icon_renderer.py::TestIconIdAssigner -v
```

### Level 3: All Icon Tests

```bash
cd backend
uv run pytest tests/test_icon_renderer.py -v
```

### Level 4: Integration Test

```bash
cd backend
uv run python scripts/test_conversion.py
# Verify output shows sequential IDs in console log
```

### Level 5: Manual PDF Verification

1. Open `samples/maps/BidMap_deployment.pdf` (or output from test_conversion.py)
2. Verify first MR36H icon shows "j100"
3. Verify second MR36H icon shows "j101"
4. Verify cameras show "100a", "101a" format
5. Verify hardlines show "aa100", "bb100" format

---

## ACCEPTANCE CRITERIA

- [ ] ID_PREFIX_CONFIG contains all 55 device type mappings
- [ ] IconIdAssigner correctly generates sequential IDs
- [ ] Three formats work: prefix-first, number-first, double-letter
- [ ] Switches with shared prefix (d100, d300, d500) increment independently
- [ ] NOCs all share f100 counter
- [ ] Devices without ID config get empty label (no error)
- [ ] All 13+ new tests pass
- [ ] Existing 34 icon tests still pass
- [ ] Converted PDFs show correct sequential IDs
- [ ] IDs reset between PDF conversions

---

## COMPLETION CHECKLIST

- [ ] Task 1: ID_PREFIX_CONFIG added with 55 entries
- [ ] Task 2: get_id_prefix_config() helper added
- [ ] Task 3: IconIdAssigner class implemented
- [ ] Task 4: AnnotationReplacer imports and stores IconIdAssigner
- [ ] Task 5: reset() called at start of conversion
- [ ] Task 6: Dynamic ID passed instead of "j100"
- [ ] Task 7: 13 unit tests added and passing
- [ ] Level 1-4 validation commands pass
- [ ] Manual PDF verification confirms correct IDs

---

## NOTES

### Design Decisions

1. **Counter key uses prefix + start**: This ensures d100/d300/d500 switches have independent counters while NOCs (all f100) share one counter.

2. **None return for unconfigured devices**: Rather than error, we return None and use empty string. This gracefully handles hardware, batteries, and other devices that don't need IDs.

3. **Class in icon_config.py**: Keeping IconIdAssigner in icon_config.py (rather than new file) maintains cohesion with ID_PREFIX_CONFIG it depends on.

4. **Reset in replace_annotations()**: Each PDF conversion starts fresh. If batch processing is added later, the reset can be moved to a higher level.

### Future Considerations

- Phones (Yealink) - user mentioned adding these later
- Additional switch models if added to deployment set
- Potential for user-configurable starting numbers per project
