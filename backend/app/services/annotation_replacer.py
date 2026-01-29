"""
Annotation replacement service.

Replaces bid icon annotations with deployment icon annotations.
"""

from app.models.annotation import Annotation, AnnotationMapping


class AnnotationReplacer:
    """Service for replacing bid annotations with deployment annotations."""

    def __init__(self, mapping_parser, btx_loader):
        """
        Initialize annotation replacer.

        Args:
            mapping_parser: MappingParser instance
            btx_loader: BTXReferenceLoader instance
        """
        self.mapping_parser = mapping_parser
        self.btx_loader = btx_loader

    def replace_annotations(
        self, annotations: list[Annotation], pdf_object
    ) -> tuple[int, int, list[str]]:
        """
        Replace all bid annotations with deployment annotations.

        Args:
            annotations: List of bid annotations to replace
            pdf_object: PDF object to modify (from PDF library)

        Returns:
            Tuple of (converted_count, skipped_count, skipped_subjects)
        """
        # TODO: Implement annotation replacement
        # For each annotation:
        #   1. Extract bid icon subject
        #   2. Look up deployment subject in mapping
        #   3. Get deployment icon visual data from BTX
        #   4. Delete bid annotation from PDF
        #   5. Create deployment annotation with same coords/size
        #   6. Insert deployment annotation into PDF
        # Track converted and skipped counts
        raise NotImplementedError("Annotation replacement not yet implemented")

    def create_deployment_annotation(
        self, bid_annotation: Annotation, deployment_subject: str
    ) -> dict:
        """
        Create deployment annotation dictionary.

        Args:
            bid_annotation: Original bid annotation
            deployment_subject: Deployment icon subject name

        Returns:
            Annotation dictionary for PDF
        """
        # TODO: Implement annotation creation
        # Copy coordinates and size from bid annotation
        # Update subject field
        # Update visual appearance with deployment icon data
        raise NotImplementedError("Annotation creation not yet implemented")
