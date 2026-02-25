/**
 * API client for the Icon Tuner endpoints.
 */

import axios, { AxiosError } from 'axios';
import type { IconConfig, GearImageInfo, CategoryInfo, ApplyToAllRequest, ApplyToAllResponse } from '../types/tuner';

const api = axios.create({
  baseURL: '',
  timeout: 30000,
});

function handleError(error: unknown): never {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail: string }>;
    const message = axiosError.response?.data?.detail || axiosError.message;
    throw new Error(message);
  }
  throw error;
}

function encodeSubject(subject: string): string {
  return encodeURIComponent(subject);
}

export async function fetchIcons(): Promise<IconConfig[]> {
  try {
    const response = await api.get<IconConfig[]>('/api/tuner/icons');
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function fetchIcon(subject: string): Promise<IconConfig> {
  try {
    const response = await api.get<IconConfig>(`/api/tuner/icons/${encodeSubject(subject)}`);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function saveIcon(subject: string, config: Partial<IconConfig>): Promise<IconConfig> {
  try {
    const response = await api.put<IconConfig>(
      `/api/tuner/icons/${encodeSubject(subject)}`,
      config,
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function createIcon(request: {
  subject: string;
  category: string;
  clone_from?: string;
}): Promise<IconConfig> {
  try {
    const response = await api.post<IconConfig>('/api/tuner/icons', request);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function deleteIcon(subject: string): Promise<void> {
  try {
    await api.delete(`/api/tuner/icons/${encodeSubject(subject)}`);
  } catch (error) {
    handleError(error);
  }
}

export async function fetchGearImages(category?: string): Promise<GearImageInfo[]> {
  try {
    const params = category ? { category } : {};
    const response = await api.get<GearImageInfo[]>('/api/tuner/gear-images', { params });
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function fetchCategories(): Promise<CategoryInfo[]> {
  try {
    const response = await api.get<CategoryInfo[]>('/api/tuner/categories');
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function applyToAll(request: ApplyToAllRequest): Promise<ApplyToAllResponse> {
  try {
    const response = await api.post<ApplyToAllResponse>('/api/tuner/icons/apply-to-all', request);
    return response.data;
  } catch (error) {
    handleError(error);
  }
}

export async function renderTestPdf(
  subject: string,
  idLabel: string = 'j100',
): Promise<Blob> {
  try {
    const response = await api.post(
      '/api/tuner/render-pdf',
      null,
      {
        params: { subject, id_label: idLabel },
        responseType: 'blob',
        timeout: 15000,
      },
    );
    return response.data;
  } catch (error) {
    handleError(error);
  }
}
