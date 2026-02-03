import { useMutation } from '@tanstack/react-query';
import { convertPDF } from '../../../lib/api';
import type { ConversionResponse } from '../../../types';

interface ConvertParams {
  uploadId: string;
  direction: string;
}

export function useConvert() {
  return useMutation<ConversionResponse, Error, ConvertParams>({
    mutationFn: ({ uploadId, direction }) => convertPDF(uploadId, direction),
  });
}
