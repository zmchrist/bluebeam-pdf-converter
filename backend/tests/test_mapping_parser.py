"""Tests for mapping parser."""

import pytest
from pathlib import Path
import tempfile
from app.services.mapping_parser import MappingParser


class TestMappingParser:
    """Test suite for MappingParser service."""

    def create_temp_mapping_file(self, content: str) -> Path:
        """Create a temporary mapping file with given content."""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    # Tests for load_mappings()

    def test_load_mappings_valid_file(self):
        """Test loading a valid mapping file."""
        content = """# Icon Mapping

| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
| Switch_Bid | Switch_Deployment | Switches |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            result = parser.load_mappings()

            assert result.total_mappings == 2
            assert result.mappings["AP_Bid"] == "AP_Deployment"
            assert result.mappings["Switch_Bid"] == "Switch_Deployment"
            assert result.categories["AP_Bid"] == "Access Points"
            assert result.categories["Switch_Bid"] == "Switches"
        finally:
            mapping_file.unlink()

    def test_load_mappings_with_extra_whitespace(self):
        """Test loading mapping file with extra whitespace."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
|  AP_Bid  |  AP_Deployment  |  Access Points  |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            result = parser.load_mappings()

            assert result.mappings["AP_Bid"] == "AP_Deployment"
            assert result.categories["AP_Bid"] == "Access Points"
        finally:
            mapping_file.unlink()

    def test_load_mappings_missing_file(self):
        """Test loading from non-existent file."""
        parser = MappingParser(Path("/nonexistent/mapping.md"))

        with pytest.raises(FileNotFoundError):
            parser.load_mappings()

    def test_load_mappings_no_table(self):
        """Test loading file with no markdown table."""
        content = """# Icon Mapping

This file has no table.
Just some text.
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)

            with pytest.raises(ValueError, match="No markdown table found"):
                parser.load_mappings()
        finally:
            mapping_file.unlink()

    def test_load_mappings_empty_table(self):
        """Test loading file with empty table (header only)."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)

            with pytest.raises(ValueError, match="No mapping data found"):
                parser.load_mappings()
        finally:
            mapping_file.unlink()

    def test_load_mappings_duplicate_bid_subject(self):
        """Test loading file with duplicate bid subjects."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
| AP_Bid | AP_Deployment_V2 | Access Points |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)

            with pytest.raises(ValueError, match="Duplicate bid subject"):
                parser.load_mappings()
        finally:
            mapping_file.unlink()

    # Tests for get_deployment_subject()

    def test_get_deployment_subject_found(self):
        """Test lookup of existing bid subject."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            parser.load_mappings()

            result = parser.get_deployment_subject("AP_Bid")
            assert result == "AP_Deployment"
        finally:
            mapping_file.unlink()

    def test_get_deployment_subject_not_found(self):
        """Test lookup of non-existent bid subject."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            parser.load_mappings()

            result = parser.get_deployment_subject("Unknown_Bid")
            assert result is None
        finally:
            mapping_file.unlink()

    def test_get_deployment_subject_before_load(self):
        """Test lookup before mappings are loaded."""
        parser = MappingParser(Path("dummy.md"))
        result = parser.get_deployment_subject("AP_Bid")
        assert result is None

    # Tests for get_category()

    def test_get_category_found(self):
        """Test category lookup for existing bid subject."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            parser.load_mappings()

            result = parser.get_category("AP_Bid")
            assert result == "Access Points"
        finally:
            mapping_file.unlink()

    def test_get_category_not_found(self):
        """Test category lookup for non-existent bid subject."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            parser.load_mappings()

            result = parser.get_category("Unknown_Bid")
            assert result is None
        finally:
            mapping_file.unlink()

    # Tests for validate_mappings()

    def test_validate_mappings_valid(self):
        """Test validation of valid mappings."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
| Switch_Bid | Switch_Deployment | Switches |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            parser.load_mappings()

            is_valid, errors = parser.validate_mappings()
            assert is_valid is True
            assert len(errors) == 0
        finally:
            mapping_file.unlink()

    def test_validate_mappings_no_mappings(self):
        """Test validation when no mappings loaded."""
        parser = MappingParser(Path("dummy.md"))

        is_valid, errors = parser.validate_mappings()
        assert is_valid is False
        assert "No mappings loaded" in errors

    # Tests for get_all_bid_subjects() and get_all_deployment_subjects()

    def test_get_all_bid_subjects(self):
        """Test getting all bid subjects."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
| Switch_Bid | Switch_Deployment | Switches |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            parser.load_mappings()

            subjects = parser.get_all_bid_subjects()
            assert "AP_Bid" in subjects
            assert "Switch_Bid" in subjects
            assert len(subjects) == 2
        finally:
            mapping_file.unlink()

    def test_get_all_deployment_subjects(self):
        """Test getting all deployment subjects."""
        content = """| Bid Icon Subject | Deployment Icon Subject | Category |
|------------------|------------------------|----------|
| AP_Bid | AP_Deployment | Access Points |
| Switch_Bid | Switch_Deployment | Switches |
"""
        mapping_file = self.create_temp_mapping_file(content)
        try:
            parser = MappingParser(mapping_file)
            parser.load_mappings()

            subjects = parser.get_all_deployment_subjects()
            assert "AP_Deployment" in subjects
            assert "Switch_Deployment" in subjects
            assert len(subjects) == 2
        finally:
            mapping_file.unlink()

    # Test with real mapping.md file

    def test_load_real_mapping_file(self):
        """Test loading the actual mapping.md file."""
        mapping_file = Path("backend/data/mapping.md")
        if not mapping_file.exists():
            pytest.skip("mapping.md not found")

        parser = MappingParser(mapping_file)
        result = parser.load_mappings()

        assert result.total_mappings > 0
        assert len(result.mappings) > 0

        # Validate all mappings are valid
        is_valid, errors = parser.validate_mappings()
        assert is_valid is True
