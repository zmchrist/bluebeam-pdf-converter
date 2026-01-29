"""Custom exception classes."""


class PDFConverterError(Exception):
    """Base exception for PDF converter errors."""

    pass


class InvalidFileTypeError(PDFConverterError):
    """Raised when uploaded file is not a valid PDF."""

    def __init__(self, message: str = "File is not a valid PDF"):
        self.message = message
        super().__init__(self.message)


class FileTooLargeError(PDFConverterError):
    """Raised when uploaded file exceeds size limit."""

    def __init__(self, message: str = "PDF file too large (max 50MB)"):
        self.message = message
        super().__init__(self.message)


class NoAnnotationsFoundError(PDFConverterError):
    """Raised when PDF contains no markup annotations."""

    def __init__(
        self,
        message: str = "No icon markup annotations found in PDF",
    ):
        self.message = message
        super().__init__(self.message)


class MultiPagePDFError(PDFConverterError):
    """Raised when PDF has multiple pages (MVP limitation)."""

    def __init__(
        self,
        message: str = "Multi-page PDFs not yet supported",
    ):
        self.message = message
        super().__init__(self.message)


class MappingNotFoundError(PDFConverterError):
    """Raised when bid icon subject not found in mapping.md."""

    def __init__(self, subject: str):
        self.subject = subject
        self.message = f"Unknown bid icon subject: {subject}"
        super().__init__(self.message)


class ConversionError(PDFConverterError):
    """Raised when PDF conversion fails."""

    def __init__(self, message: str = "Conversion failed"):
        self.message = message
        super().__init__(self.message)


class UploadNotFoundError(PDFConverterError):
    """Raised when upload session not found."""

    def __init__(
        self,
        message: str = "Upload session not found or expired",
    ):
        self.message = message
        super().__init__(self.message)


class FileNotFoundError(PDFConverterError):
    """Raised when converted file not found."""

    def __init__(
        self,
        message: str = "Converted file not found or expired",
    ):
        self.message = message
        super().__init__(self.message)
