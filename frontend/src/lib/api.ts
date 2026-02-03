/**
 * API client for Bluebeam PDF Converter backend.
 */

import axios, { AxiosError } from 'axios';
import type {
  PDFUploadResponse,
  ConversionRequest,
  ConversionResponse,
  HealthCheckResponse,
  APIError
} from '../types';

// Base URL is proxied by Vite in development
const api = axios.create({
  baseURL: '',
  timeout: 30000, // 30 seconds default
});

// Error handler to extract message from API response
function handleError(error: unknown): never {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<APIError>;
    const message = axiosError.response?.data?.detail || axiosError.message;
    throw new Error(message);
  }
  throw error;
}

/**
 * Upload a PDF file for conversion.
 */
export async function uploadPDF(file: File): Promise<PDFUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post<PDFUploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutes for large file uploads
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

/**
 * Convert an uploaded PDF from bid to deployment icons.
 */
export async function convertPDF(
  uploadId: string,
  direction: string = 'bid_to_deployment',
  outputFilename?: string
): Promise<ConversionResponse> {
  const request: ConversionRequest = { direction };
  if (outputFilename) {
    request.output_filename = outputFilename;
  }

  try {
    const response = await api.post<ConversionResponse>(
      `/api/convert/${uploadId}`,
      request,
      { timeout: 60000 } // 60 seconds for conversion
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

/**
 * Get download URL for converted PDF.
 * Returns the full URL path for download.
 */
export function getDownloadUrl(fileId: string): string {
  return `/api/download/${fileId}`;
}

/**
 * Check backend health status.
 */
export async function checkHealth(): Promise<HealthCheckResponse> {
  try {
    const response = await api.get<HealthCheckResponse>('/health', {
      timeout: 5000, // 5 seconds for health checks
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}
