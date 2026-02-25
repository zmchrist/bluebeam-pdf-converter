/**
 * TypeScript interfaces for the Icon Tuner feature.
 */

export interface IconConfig {
  subject: string;
  category: string;
  circle_color: [number, number, number];
  circle_border_width: number;
  circle_border_color: [number, number, number];
  id_box_height: number;
  id_box_width_ratio: number;
  id_box_border_width: number;
  id_font_size: number;
  img_scale_ratio: number;
  img_x_offset: number;
  img_y_offset: number;
  brand_text: string;
  brand_font_size: number;
  brand_y_offset: number;
  brand_x_offset: number;
  model_font_size: number;
  model_y_offset: number;
  model_x_offset: number;
  model_text_override: string | null;
  model_uppercase: boolean;
  font_name: string;
  text_color: [number, number, number];
  id_text_color: [number, number, number] | null;
  no_image: boolean;
  image_path: string | null;
  layer_order: LayerId[];
  source: 'python' | 'json_override' | 'custom';
}

export type LayerId = 'gear_image' | 'brand_text' | 'model_text';
export type FrameId = 'circle' | 'id_box';
export type SelectableElement = LayerId | FrameId;

export interface CanvasState {
  zoom: number;
  panX: number;
  panY: number;
  selectedElement: SelectableElement | null;
  isDragging: boolean;
}

export interface GearImageInfo {
  filename: string;
  category: string;
  path: string;
  thumbnail: string;
}

export interface CategoryInfo {
  name: string;
  icon_count: number;
  defaults: Partial<IconConfig>;
}

export interface HistoryEntry {
  config: IconConfig;
  description: string;
}

export interface ApplyToAllRequest {
  field_group: 'circle' | 'id_box' | 'gear_image' | 'brand_text' | 'model_text';
  scope: 'category' | 'all';
  source_subject: string;
  circle_color?: [number, number, number];
  circle_border_width?: number;
  circle_border_color?: [number, number, number];
  id_box_height?: number;
  id_box_width_ratio?: number;
  id_box_border_width?: number;
  id_font_size?: number;
  img_scale_ratio?: number;
  img_x_offset?: number;
  img_y_offset?: number;
  brand_text?: string;
  brand_font_size?: number;
  brand_x_offset?: number;
  brand_y_offset?: number;
  text_color?: [number, number, number];
  model_font_size?: number;
  model_x_offset?: number;
  model_y_offset?: number;
  model_uppercase?: boolean;
  model_text_override?: string | null;
}

export interface ApplyToAllResponse {
  affected_count: number;
  field_group: string;
  scope: string;
}
