"""Tests for BTX reference loader."""

import pytest
from pathlib import Path
import tempfile

from app.services.btx_loader import BTXReferenceLoader


class TestBTXReferenceLoader:
    """Test suite for BTXReferenceLoader service."""

    # Test decode_hex_zlib()

    def test_decode_hex_zlib_valid(self):
        """Test decoding valid hex-encoded zlib data."""
        # Real hex string from BTX file <Title> element
        hex_string = "789c73ca4c5108c9cfcf2956d030323032d304002a93047c"
        result = BTXReferenceLoader.decode_hex_zlib(hex_string)

        assert result is not None
        assert "Bid" in result or "Tool" in result
        # Result should be something like "Bid Tools (2026)"
        assert len(result) > 5

    def test_decode_hex_zlib_empty_string(self):
        """Test decoding empty string."""
        result = BTXReferenceLoader.decode_hex_zlib("")
        assert result is None

    def test_decode_hex_zlib_none(self):
        """Test decoding None value."""
        result = BTXReferenceLoader.decode_hex_zlib(None)
        assert result is None

    def test_decode_hex_zlib_invalid_hex(self):
        """Test decoding invalid hex string."""
        result = BTXReferenceLoader.decode_hex_zlib("not-valid-hex!")
        assert result is None

    def test_decode_hex_zlib_no_zlib_magic(self):
        """Test decoding hex without zlib magic number."""
        # Valid hex but not zlib compressed (doesn't start with 789c)
        result = BTXReferenceLoader.decode_hex_zlib("48656c6c6f")  # "Hello" in hex
        assert result is None

    def test_decode_hex_zlib_corrupted_zlib(self):
        """Test decoding corrupted zlib data."""
        # Starts with zlib magic but corrupted
        result = BTXReferenceLoader.decode_hex_zlib("789c00112233")
        assert result is None

    # Test is_hex_zlib()

    def test_is_hex_zlib_valid(self):
        """Test detection of valid zlib hex string."""
        assert BTXReferenceLoader.is_hex_zlib("789c73ca4c5108") is True
        assert BTXReferenceLoader.is_hex_zlib("789C73CA4C5108") is True  # uppercase

    def test_is_hex_zlib_invalid(self):
        """Test detection of non-zlib hex string."""
        assert BTXReferenceLoader.is_hex_zlib("48656c6c6f") is False
        assert BTXReferenceLoader.is_hex_zlib("") is False
        assert BTXReferenceLoader.is_hex_zlib(None) is False
        assert BTXReferenceLoader.is_hex_zlib("789") is False  # too short

    # Test _extract_subject_from_raw()

    def test_extract_subject_from_raw_valid(self):
        """Test extracting subject from valid Raw content."""
        raw_content = '<</IC[0.27]/RD[0.075]/Subj(INFRAS - Edge Switch)/TempNameID/ABC>>'
        result = BTXReferenceLoader._extract_subject_from_raw(raw_content)

        assert result == "INFRAS - Edge Switch"

    def test_extract_subject_from_raw_with_slash(self):
        """Test extracting subject with /Subj format."""
        raw_content = '<</IC[0.27]/Subj(My Test Subject)/Other/data>>'
        result = BTXReferenceLoader._extract_subject_from_raw(raw_content)

        assert result == "My Test Subject"

    def test_extract_subject_from_raw_empty(self):
        """Test extracting subject from empty content."""
        result = BTXReferenceLoader._extract_subject_from_raw("")
        assert result is None

        result = BTXReferenceLoader._extract_subject_from_raw(None)
        assert result is None

    def test_extract_subject_from_raw_no_subject(self):
        """Test extracting subject when none exists."""
        raw_content = '<</IC[0.27]/RD[0.075]/Other(data)>>'
        result = BTXReferenceLoader._extract_subject_from_raw(raw_content)

        assert result is None

    # Test _extract_category_from_filename()

    def test_extract_category_from_filename(self):
        """Test extracting category from BTX filename."""
        loader = BTXReferenceLoader(Path("toolchest"))

        assert loader._extract_category_from_filename(
            "CDS Bluebeam Access Points [01-01-2026].btx"
        ) == "Access Points"

        assert loader._extract_category_from_filename(
            "CDS Bluebeam Bid Tools [01-21-2026].btx"
        ) == "Bid Tools"

        assert loader._extract_category_from_filename(
            "CDS Bluebeam Point-to-Points [01-01-2026].btx"
        ) == "Point-to-Points"

    # Test initialization

    def test_init_default_state(self):
        """Test loader initialization state."""
        loader = BTXReferenceLoader(Path("toolchest"))

        assert loader.toolchest_dir == Path("toolchest")
        assert loader.bid_icons == {}
        assert loader.deployment_icons == {}
        assert loader.is_loaded() is False

    # Test helper methods before loading

    def test_get_counts_before_load(self):
        """Test count methods before loading."""
        loader = BTXReferenceLoader(Path("toolchest"))

        assert loader.get_bid_icon_count() == 0
        assert loader.get_deployment_icon_count() == 0
        assert loader.get_all_subjects() == []
        assert loader.get_bid_subjects() == []
        assert loader.get_deployment_subjects() == []

    def test_get_icon_data_before_load(self):
        """Test get_icon_data before loading."""
        loader = BTXReferenceLoader(Path("toolchest"))

        result = loader.get_icon_data("any_subject", "bid")
        assert result is None

        result = loader.get_icon_data("any_subject", "deployment")
        assert result is None

    # Test _parse_btx_file()

    def test_parse_btx_file_missing(self):
        """Test parsing non-existent BTX file."""
        loader = BTXReferenceLoader(Path("toolchest"))

        with pytest.raises(FileNotFoundError):
            loader._parse_btx_file(Path("/nonexistent/file.btx"))

    def test_parse_btx_file_invalid_xml(self):
        """Test parsing invalid XML file."""
        loader = BTXReferenceLoader(Path("toolchest"))

        # Create temp file with invalid XML
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".btx", delete=False, encoding="utf-8"
        ) as f:
            f.write("This is not valid XML <incomplete>")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Invalid XML"):
                loader._parse_btx_file(temp_path)
        finally:
            temp_path.unlink()

    # Test load_toolchest()

    def test_load_toolchest_missing_dir(self):
        """Test loading from non-existent directory."""
        loader = BTXReferenceLoader(Path("/nonexistent/toolchest"))

        with pytest.raises(FileNotFoundError):
            loader.load_toolchest()

    # Integration tests with real files

    def test_load_real_toolchest(self):
        """Test loading from actual toolchest directory."""
        # Try multiple possible paths
        possible_paths = [
            Path("../toolchest"),
            Path("toolchest"),
            Path(__file__).parent.parent.parent / "toolchest",
        ]

        toolchest_dir = None
        for path in possible_paths:
            if path.exists() and (path / "bidTools").exists():
                toolchest_dir = path
                break

        if toolchest_dir is None:
            pytest.skip("Toolchest directory not found")

        loader = BTXReferenceLoader(toolchest_dir)
        loader.load_toolchest()

        # Verify loading succeeded
        assert loader.is_loaded() is True
        assert loader.get_bid_icon_count() > 0
        assert loader.get_deployment_icon_count() > 0

        # Verify we can retrieve icon data
        bid_subjects = loader.get_bid_subjects()
        assert len(bid_subjects) > 0

        first_subject = bid_subjects[0]
        icon_data = loader.get_icon_data(first_subject, "bid")
        assert icon_data is not None
        assert icon_data.subject == first_subject
        assert icon_data.category != ""

    def test_parse_real_bid_btx(self):
        """Test parsing actual bid BTX file."""
        possible_paths = [
            Path("../toolchest/bidTools/CDS Bluebeam Bid Tools [01-21-2026].btx"),
            Path("toolchest/bidTools/CDS Bluebeam Bid Tools [01-21-2026].btx"),
        ]

        btx_path = None
        for path in possible_paths:
            if path.exists():
                btx_path = path
                break

        if btx_path is None:
            pytest.skip("Bid BTX file not found")

        loader = BTXReferenceLoader(btx_path.parent.parent)
        items = loader._parse_btx_file(btx_path)

        assert len(items) > 0

        # Verify item structure
        first_item = items[0]
        assert "name" in first_item
        assert "type" in first_item
        assert "raw" in first_item
        assert "resources" in first_item

        # Verify we can extract subject
        subject = loader._extract_subject_from_raw(first_item.get("raw", ""))
        assert subject is not None

    def test_get_icon_data_found(self):
        """Test retrieving existing icon data."""
        possible_paths = [
            Path("../toolchest"),
            Path("toolchest"),
        ]

        toolchest_dir = None
        for path in possible_paths:
            if path.exists() and (path / "bidTools").exists():
                toolchest_dir = path
                break

        if toolchest_dir is None:
            pytest.skip("Toolchest directory not found")

        loader = BTXReferenceLoader(toolchest_dir)
        loader.load_toolchest()

        # Get a known subject
        bid_subjects = loader.get_bid_subjects()
        if not bid_subjects:
            pytest.skip("No bid subjects loaded")

        subject = bid_subjects[0]
        result = loader.get_icon_data(subject, "bid")

        assert result is not None
        assert result.subject == subject
        assert result.category is not None
        assert result.metadata is not None
        assert "source_file" in result.metadata

    def test_get_icon_data_not_found(self):
        """Test retrieving non-existent icon data."""
        possible_paths = [
            Path("../toolchest"),
            Path("toolchest"),
        ]

        toolchest_dir = None
        for path in possible_paths:
            if path.exists() and (path / "bidTools").exists():
                toolchest_dir = path
                break

        if toolchest_dir is None:
            pytest.skip("Toolchest directory not found")

        loader = BTXReferenceLoader(toolchest_dir)
        loader.load_toolchest()

        result = loader.get_icon_data("NonExistent Subject XYZ", "bid")
        assert result is None

        result = loader.get_icon_data("NonExistent Subject XYZ", "deployment")
        assert result is None

    def test_reload_clears_previous_data(self):
        """Test that reloading clears previous data."""
        possible_paths = [
            Path("../toolchest"),
            Path("toolchest"),
        ]

        toolchest_dir = None
        for path in possible_paths:
            if path.exists() and (path / "bidTools").exists():
                toolchest_dir = path
                break

        if toolchest_dir is None:
            pytest.skip("Toolchest directory not found")

        loader = BTXReferenceLoader(toolchest_dir)

        # Load first time
        loader.load_toolchest()
        first_bid_count = loader.get_bid_icon_count()

        # Load again
        loader.load_toolchest()
        second_bid_count = loader.get_bid_icon_count()

        # Counts should be the same (not doubled)
        assert first_bid_count == second_bid_count
