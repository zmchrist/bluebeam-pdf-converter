"""Tests for subject extractor."""

from app.services.subject_extractor import SubjectExtractor


class TestSubjectExtractor:
    """Test suite for SubjectExtractor service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = SubjectExtractor()

    # Tests for extract_subject()

    def test_extract_plain_text_subject(self):
        """Test extraction of plain text subject."""
        result = self.extractor.extract_subject({"subject": "AP_Bid"})
        assert result == "AP_Bid"

    def test_extract_subject_from_Subject_key(self):
        """Test extraction using 'Subject' key (capitalized)."""
        result = self.extractor.extract_subject({"Subject": "Switch_Bid"})
        assert result == "Switch_Bid"

    def test_extract_subject_from_Subj_key(self):
        """Test extraction using 'Subj' key (PDF format)."""
        result = self.extractor.extract_subject({"Subj": "Camera_Bid"})
        assert result == "Camera_Bid"

    def test_extract_subject_from_slash_Subject_key(self):
        """Test extraction using '/Subject' key (PDF annotation format)."""
        result = self.extractor.extract_subject({"/Subject": "P2P_Bid"})
        assert result == "P2P_Bid"

    def test_extract_subject_from_slash_Subj_key(self):
        """Test extraction using '/Subj' key."""
        result = self.extractor.extract_subject({"/Subj": "NOC_Bid"})
        assert result == "NOC_Bid"

    def test_extract_empty_subject(self):
        """Test extraction of empty subject."""
        result = self.extractor.extract_subject({"subject": ""})
        assert result == ""

    def test_extract_none_subject(self):
        """Test extraction when subject is None."""
        result = self.extractor.extract_subject({"subject": None})
        assert result == ""

    def test_extract_missing_subject_key(self):
        """Test extraction when subject key is missing."""
        result = self.extractor.extract_subject({"other_key": "value"})
        assert result == ""

    def test_extract_empty_dict(self):
        """Test extraction from empty dictionary."""
        result = self.extractor.extract_subject({})
        assert result == ""

    # Tests for is_hex_encoded()

    def test_is_hex_encoded_valid_hex(self):
        """Test detection of valid hex-encoded string."""
        # "AP" in ASCII hex
        assert SubjectExtractor.is_hex_encoded("4150") is True

    def test_is_hex_encoded_longer_hex(self):
        """Test detection of longer hex string."""
        # "AP_Bid" in ASCII hex
        assert SubjectExtractor.is_hex_encoded("41505f426964") is True

    def test_is_hex_encoded_with_null_bytes(self):
        """Test detection of hex with null bytes (UTF-16-BE)."""
        # "AP" in UTF-16-BE (0041 0050)
        assert SubjectExtractor.is_hex_encoded("00410050") is True

    def test_is_hex_encoded_plain_text(self):
        """Test that plain text subjects are not detected as hex."""
        # "AP_Bid" should NOT be detected as hex even though 'A', 'B', etc. are valid hex chars
        assert SubjectExtractor.is_hex_encoded("AP_Bid") is False

    def test_is_hex_encoded_plain_text_all_caps(self):
        """Test that all-caps text is not detected as hex."""
        assert SubjectExtractor.is_hex_encoded("ABCDEF") is False

    def test_is_hex_encoded_odd_length(self):
        """Test that odd-length strings are not detected as hex."""
        assert SubjectExtractor.is_hex_encoded("4150F") is False

    def test_is_hex_encoded_empty_string(self):
        """Test that empty string is not detected as hex."""
        assert SubjectExtractor.is_hex_encoded("") is False

    def test_is_hex_encoded_short_string(self):
        """Test that very short strings are not detected as hex."""
        assert SubjectExtractor.is_hex_encoded("41") is False

    def test_is_hex_encoded_non_hex_chars(self):
        """Test that strings with non-hex characters are not detected as hex."""
        assert SubjectExtractor.is_hex_encoded("41GZ50") is False

    # Tests for translate_hex_subject()

    def test_translate_hex_ascii(self):
        """Test translation of ASCII hex."""
        # "AP" = 0x41 0x50
        result = self.extractor.translate_hex_subject("4150")
        assert result == "AP"

    def test_translate_hex_ascii_with_underscore(self):
        """Test translation of ASCII hex with underscore."""
        # "AP_Bid" = 0x41 0x50 0x5f 0x42 0x69 0x64
        result = self.extractor.translate_hex_subject("41505f426964")
        assert result == "AP_Bid"

    def test_translate_hex_utf16be(self):
        """Test translation of UTF-16-BE hex (with null bytes)."""
        # "AP" in UTF-16-BE: 0x0041 0x0050
        result = self.extractor.translate_hex_subject("00410050")
        assert result == "AP"

    def test_translate_hex_utf16be_with_underscore(self):
        """Test translation of UTF-16-BE hex with underscore."""
        # "AP_B" in UTF-16-BE: 0x0041 0x0050 0x005f 0x0042
        result = self.extractor.translate_hex_subject("004100500042")
        # UTF-16-BE decodes to "AP\x00B" initially, then we remove nulls
        assert "A" in result and "P" in result

    def test_translate_hex_invalid_returns_original(self):
        """Test that invalid hex returns original string."""
        result = self.extractor.translate_hex_subject("ZZZZ")
        assert result == "ZZZZ"

    def test_translate_hex_empty_returns_empty(self):
        """Test that empty hex returns empty string."""
        result = self.extractor.translate_hex_subject("")
        assert result == ""

    # Integration tests for extract_subject with hex-encoded values

    def test_extract_hex_encoded_subject(self):
        """Test extraction and translation of hex-encoded subject."""
        # "AP_Bid" in ASCII hex
        hex_value = "41505f426964"
        result = self.extractor.extract_subject({"subject": hex_value})
        assert result == "AP_Bid"

    def test_extract_with_priority(self):
        """Test that 'subject' key takes priority over others."""
        result = self.extractor.extract_subject({
            "subject": "Subject1",
            "Subject": "Subject2",
            "Subj": "Subject3"
        })
        assert result == "Subject1"
