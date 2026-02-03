import { useMutation } from '@tanstack/react-query';
import { uploadPDF } from '../../../lib/api';
import type { PDFUploadResponse } from '../../../types';

export function useUpload() {
  return useMutation<PDFUploadResponse, Error, File>({
    mutationFn: uploadPDF,
  });
}
