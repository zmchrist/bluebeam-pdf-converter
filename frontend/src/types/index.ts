/**
 * TypeScript interfaces matching backend Pydantic models.
 * See: backend/app/models/pdf_file.py
 */

// Response from POST /api/upload
export interface PDFUploadResponse {
  upload_id: string;
  file_name: string;
  file_size: number;
  status: string;
  page_count: number;
  annotation_count: number;
  message: string;
}

// Request body for POST /api/convert/{upload_id}
export interface ConversionRequest {
  direction: string;
  output_filename?: string;
}

// Response from POST /api/convert/{upload_id}
export interface ConversionResponse {
  upload_id: string;
  file_id: string;
  status: string;
  original_file: string;
  converted_file: string;
  direction: string;
  annotations_processed: number;
  annotations_converted: number;
  annotations_skipped: number;
  skipped_subjects: string[];
  processing_time_ms: number;
  download_url: string;
  message: string;
}

// Response from GET /health
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  timestamp: string;
  mapping_loaded: boolean;
  mapping_count: number;
  toolchest_bid_icons: number;
  toolchest_deployment_icons: number;
  error?: string;
}

// API error response format
export interface APIError {
  detail: string;
  error_code?: string;
}

// Workflow step for progress display
export type WorkflowStep =
  | 'idle'
  | 'uploading'
  | 'uploaded'
  | 'converting'
  | 'converted'
  | 'error';

/**
 * Conversion direction options.
 * MVP supports bid_to_deployment only.
 * Phase 2 will add: 'deployment_to_bid'
 */
export type ConversionDirection = 'bid_to_deployment';
