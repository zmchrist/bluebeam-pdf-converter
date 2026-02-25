"""
Layer manager service for PDF Optional Content Groups (OCG).

Clones the full layer structure from a reference PDF (EVENT26) into
the converted output, and provides a subject → OCG reference lookup
so each deployment annotation can be assigned to its device layer.
"""

import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject, NameObject

logger = logging.getLogger(__name__)


class LayerManager:
    """
    Manages PDF layer (OCG) structure for converted PDFs.

    Reads a reference PDF containing the full layer hierarchy,
    clones it into the output writer, and provides a lookup
    from deployment subject names to their OCG indirect objects.
    """

    def __init__(self, reference_pdf_path: Path):
        """
        Initialize with path to the reference PDF containing layers.

        Args:
            reference_pdf_path: Path to EVENT26 reference PDF with OCG structure.
        """
        self._reference_path = reference_pdf_path
        self._name_to_ref: dict[str, IndirectObject] = {}
        self._applied = False
        self._layer_count = 0

    @property
    def is_loaded(self) -> bool:
        """Whether layers have been successfully applied to a writer."""
        return self._applied

    @property
    def layer_count(self) -> int:
        """Number of OCG layers cloned into the writer."""
        return self._layer_count

    def apply_to_writer(self, writer: PdfWriter) -> bool:
        """
        Clone the full OCProperties structure from the reference PDF into the writer.

        This copies all 169 OCG objects, the /D default config (with /Order
        hierarchy and /AS activation states), preserving internal references.

        Args:
            writer: PdfWriter to receive the layer structure.

        Returns:
            True on success, False on any failure (graceful degradation).
        """
        if not self._reference_path.exists():
            logger.warning(f"Layer reference PDF not found: {self._reference_path}")
            return False

        try:
            reader = PdfReader(str(self._reference_path))
            catalog = reader.trailer["/Root"]
            oc_props_ref = catalog.get("/OCProperties")

            if oc_props_ref is None:
                logger.warning("Reference PDF has no /OCProperties")
                return False

            oc_props = oc_props_ref.get_object()

            # Clone entire OCProperties structure into writer
            cloned = oc_props.clone(writer)
            writer._root_object[NameObject("/OCProperties")] = cloned

            # Build name → IndirectObject lookup from cloned OCGs
            cloned_obj = cloned.get_object() if hasattr(cloned, "get_object") else cloned
            ocgs = cloned_obj.get("/OCGs")
            if not ocgs:
                logger.warning("Cloned OCProperties has no /OCGs array")
                return False

            self._name_to_ref.clear()
            for ref in ocgs:
                obj = ref.get_object()
                name = str(obj.get("/Name", ""))
                if name:
                    self._name_to_ref[name] = ref

            self._layer_count = len(ocgs)
            self._applied = True

            logger.info(
                f"Applied {self._layer_count} OCG layers from reference PDF "
                f"({len(self._name_to_ref)} unique names)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to apply layers from reference PDF: {e}")
            self._applied = False
            return False

    def get_ocg_ref(self, deployment_subject: str) -> IndirectObject | None:
        """
        Look up the OCG indirect object for a deployment subject.

        Args:
            deployment_subject: Deployment subject name (e.g., "AP - Cisco MR36H").

        Returns:
            IndirectObject reference to the OCG, or None if not loaded
            or no matching layer exists.
        """
        if not self._applied:
            return None
        return self._name_to_ref.get(deployment_subject)
