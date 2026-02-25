/**
 * Canvas 2D drawing functions that mirror icon_renderer.py logic.
 *
 * PDF coordinate system: Y=0 at bottom, Y increases upward.
 * Canvas coordinate system: Y=0 at top, Y increases downward.
 * We use a virtual PDF coordinate space [0,0,25,30] scaled up by CANVAS_SCALE.
 */

import type { IconConfig, LayerId } from '../../../types/tuner';

// Scale factor: PDF units to canvas pixels
export const CANVAS_SCALE = 20;
export const PDF_WIDTH = 25;
export const PDF_HEIGHT = 30;
export const CANVAS_WIDTH = PDF_WIDTH * CANVAS_SCALE;  // 500
export const CANVAS_HEIGHT = PDF_HEIGHT * CANVAS_SCALE; // 600

export function rgbToCSS(color: [number, number, number]): string {
  const [r, g, b] = color;
  return `rgb(${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)})`;
}

export function rgbToHex(color: [number, number, number]): string {
  const toHex = (v: number) => Math.round(v * 255).toString(16).padStart(2, '0');
  return `#${toHex(color[0])}${toHex(color[1])}${toHex(color[2])}`;
}

export function hexToRgb(hex: string): [number, number, number] {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return [0, 0, 0];
  return [
    parseInt(result[1], 16) / 255,
    parseInt(result[2], 16) / 255,
    parseInt(result[3], 16) / 255,
  ];
}

// Convert PDF Y (bottom-up) to canvas Y (top-down)
function flipY(pdfY: number): number {
  return PDF_HEIGHT - pdfY;
}

// Scale PDF coordinate to canvas pixel
function toCanvasX(pdfX: number): number {
  return pdfX * CANVAS_SCALE;
}

function toCanvasY(pdfY: number): number {
  return flipY(pdfY) * CANVAS_SCALE;
}

function toCanvasSize(pdfSize: number): number {
  return pdfSize * CANVAS_SCALE;
}

export interface LayoutResult {
  cx: number; // Canvas X center of circle
  cy: number; // Canvas Y center of circle
  radius: number; // Canvas radius
  idBox: { x: number; y: number; width: number; height: number };
  image: { x: number; y: number; width: number; height: number } | null;
  brandText: { x: number; y: number } | null;
  modelText: { x: number; y: number; lines: string[] } | null;
}

export function calculateLayout(
  config: IconConfig,
  modelText: string,
  imageSize?: { w: number; h: number },
): LayoutResult {
  // Mirror _create_appearance_stream layout logic
  const rect = [0, 0, PDF_WIDTH, PDF_HEIGHT]; // [x1, y1, x2, y2]
  const x1 = rect[0], y1 = rect[1], x2 = rect[2], y2 = rect[3];
  const width = x2 - x1;

  const idBoxHeight = config.id_box_height;
  const idBoxWidthRatio = config.id_box_width_ratio;
  const idBoxWidth = width * idBoxWidthRatio;
  const pdfCx = (x1 + x2) / 2;
  const idBoxYOffset = config.id_box_y_offset || 0;
  const idBoxX1 = pdfCx - idBoxWidth / 2;
  const idBoxY1 = y2 - idBoxHeight + idBoxYOffset; // PDF Y of bottom of ID box

  // Circle overlaps into ID box by 2 PDF units
  const circleTop = idBoxY1 + 2;
  const circleBottom = y1;
  const circleAreaHeight = circleTop - circleBottom;
  const radius = Math.min(width, circleAreaHeight) / 2 - 0.3;
  const pdfCy = circleTop - radius;

  // Convert to canvas
  const cx = toCanvasX(pdfCx);
  const cy = toCanvasY(pdfCy);
  const canvasRadius = toCanvasSize(radius);

  // ID box (note: PDF y1 is bottom, but in canvas it flips)
  const idBox = {
    x: toCanvasX(idBoxX1),
    y: toCanvasY(idBoxY1 + idBoxHeight), // Top of box in canvas coords
    width: toCanvasSize(idBoxWidth),
    height: toCanvasSize(idBoxHeight),
  };

  // Image - match PDF renderer's aspect-ratio-aware scaling
  let image: LayoutResult['image'] = null;
  if (config.image_path && !config.no_image) {
    const imgScaleRatio = config.img_scale_ratio;
    const imgXOffset = config.img_x_offset || 0;
    const imgYOffset = config.img_y_offset || 0;

    let imgDrawW: number;
    let imgDrawH: number;
    if (imageSize && imageSize.w > 0 && imageSize.h > 0) {
      // Use actual aspect ratio (matches icon_renderer.py lines 284-286)
      const imgScale = (radius * imgScaleRatio) / Math.max(imageSize.w, imageSize.h);
      imgDrawW = toCanvasSize(imageSize.w * imgScale);
      imgDrawH = toCanvasSize(imageSize.h * imgScale);
    } else {
      // Fallback: assume square
      const imgSize = radius * imgScaleRatio;
      imgDrawW = toCanvasSize(imgSize);
      imgDrawH = toCanvasSize(imgSize);
    }

    image = {
      x: cx - imgDrawW / 2 + toCanvasSize(imgXOffset),
      y: cy - imgDrawH / 2 - toCanvasSize(imgYOffset), // Flip Y offset
      width: imgDrawW,
      height: imgDrawH,
    };
  }

  // Brand text position
  let brandText: LayoutResult['brandText'] = null;
  if (config.brand_text) {
    const brandXOffset = config.brand_x_offset || 0;
    const brandYOffset = config.brand_y_offset || 0;
    // In PDF: text_y_brand = cy + radius + brand_y_offset (cy is bottom-up)
    // brand_y_offset is typically negative (moves text down from top of circle)
    brandText = {
      x: cx + toCanvasSize(brandXOffset),
      y: toCanvasY(pdfCy + radius + brandYOffset),
    };
  }

  // Model text
  let modelTextResult: LayoutResult['modelText'] = null;
  if (modelText) {
    const modelXOffset = config.model_x_offset || 0;
    const modelYOffset = config.model_y_offset || 0;
    const lines = modelText.split('\n').slice(0, 3);
    // In PDF: base_y = cy - radius + model_y_offset
    modelTextResult = {
      x: cx + toCanvasSize(modelXOffset),
      y: toCanvasY(pdfCy - radius + modelYOffset),
      lines,
    };
  }

  return { cx, cy, radius: canvasRadius, idBox, image, brandText, modelText: modelTextResult };
}

export function getModelText(config: IconConfig): string {
  if (config.model_text_override) return config.model_text_override;
  const subject = config.subject;
  if (subject.includes(' - ')) {
    const parts = subject.split(' - ');
    const modelPart = parts[parts.length - 1];
    const brands = ['Cisco ', 'Ubiquiti ', 'Axis ', 'Yealink ', 'BrightSign ',
      'Fortinet ', 'Meraki ', 'EcoFlow ', 'Liebert ', 'Netgear ', 'Netonix '];
    for (const brand of brands) {
      if (modelPart.startsWith(brand)) return modelPart.slice(brand.length);
    }
    return modelPart;
  }
  return subject;
}

export function drawIcon(
  ctx: CanvasRenderingContext2D,
  config: IconConfig,
  gearImage: HTMLImageElement | null,
  layerVisibility: Record<LayerId, boolean>,
  selectedElement: string | null,
) {
  const modelText = getModelText(config);
  const displayModel = config.model_uppercase ? modelText.toUpperCase() : modelText;
  const imageSize = gearImage && gearImage.naturalWidth > 0
    ? { w: gearImage.naturalWidth, h: gearImage.naturalHeight }
    : undefined;
  const layout = calculateLayout(config, displayModel, imageSize);

  // 1. Draw circle
  ctx.beginPath();
  ctx.arc(layout.cx, layout.cy, layout.radius, 0, Math.PI * 2);
  ctx.fillStyle = rgbToCSS(config.circle_color);
  ctx.fill();
  if (config.circle_border_width > 0) {
    ctx.strokeStyle = rgbToCSS(config.circle_border_color);
    ctx.lineWidth = toCanvasSize(config.circle_border_width);
    ctx.stroke();
  }

  // Selection highlight for circle
  if (selectedElement === 'circle') {
    ctx.beginPath();
    ctx.arc(layout.cx, layout.cy, layout.radius + 3, 0, Math.PI * 2);
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 3]);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // 2. Draw ID box (unless hidden)
  if (!config.no_id_box) {
    const { idBox } = layout;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(idBox.x, idBox.y, idBox.width, idBox.height);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = toCanvasSize(config.id_box_border_width);
    ctx.strokeRect(idBox.x, idBox.y, idBox.width, idBox.height);

    // ID box text
    const idTextColor = config.id_text_color || config.circle_color;
    ctx.fillStyle = rgbToCSS(idTextColor);
    ctx.font = `bold ${toCanvasSize(config.id_font_size)}px Helvetica, Arial, sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(config.id_preview || 'j100', idBox.x + idBox.width / 2, idBox.y + idBox.height / 2);

    // Selection highlight for ID box
    if (selectedElement === 'id_box') {
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 3]);
      ctx.strokeRect(idBox.x - 3, idBox.y - 3, idBox.width + 6, idBox.height + 6);
      ctx.setLineDash([]);
    }
  }

  // 3. Draw layers in configured order
  const layerDrawers: Record<LayerId, () => void> = {
    gear_image: () => {
      if (!layerVisibility.gear_image || !layout.image || !gearImage) return;
      ctx.drawImage(gearImage, layout.image.x, layout.image.y, layout.image.width, layout.image.height);
      if (selectedElement === 'gear_image') {
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 3]);
        ctx.strokeRect(layout.image.x - 2, layout.image.y - 2, layout.image.width + 4, layout.image.height + 4);
        ctx.setLineDash([]);
      }
    },
    brand_text: () => {
      if (!layerVisibility.brand_text || !config.brand_text || !layout.brandText) return;
      const fontSize = toCanvasSize(config.brand_font_size);
      ctx.fillStyle = rgbToCSS(config.text_color);
      ctx.font = `bold ${fontSize}px Helvetica, Arial, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(config.brand_text, layout.brandText.x, layout.brandText.y);
      if (selectedElement === 'brand_text') {
        const tw = ctx.measureText(config.brand_text).width;
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 3]);
        ctx.strokeRect(layout.brandText.x - tw / 2 - 4, layout.brandText.y - fontSize / 2 - 4, tw + 8, fontSize + 8);
        ctx.setLineDash([]);
      }
    },
    model_text: () => {
      if (!layerVisibility.model_text || !layout.modelText) return;
      const fontSize = toCanvasSize(config.model_font_size);
      const lineHeight = fontSize * 1.2;
      const { lines } = layout.modelText;
      ctx.fillStyle = rgbToCSS(config.text_color);
      ctx.font = `bold ${fontSize}px Helvetica, Arial, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      // Adjust base Y for multi-line centering
      let baseY = layout.modelText.y;
      if (lines.length > 1) {
        baseY -= ((lines.length - 1) * lineHeight) / 2;
      }

      for (let i = 0; i < lines.length; i++) {
        ctx.fillText(lines[i], layout.modelText.x, baseY + i * lineHeight);
      }
      if (selectedElement === 'model_text') {
        const maxWidth = Math.max(...lines.map(l => ctx.measureText(l).width));
        const totalHeight = lines.length * lineHeight;
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 3]);
        ctx.strokeRect(
          layout.modelText.x - maxWidth / 2 - 4,
          baseY - fontSize / 2 - 4,
          maxWidth + 8,
          totalHeight + 8,
        );
        ctx.setLineDash([]);
      }
    },
  };

  for (const layerId of config.layer_order) {
    const drawer = layerDrawers[layerId as LayerId];
    if (drawer) drawer();
  }
}

/** Get bounding rects for hit testing */
export function getElementBounds(config: IconConfig): Record<string, { x: number; y: number; w: number; h: number }> {
  const modelText = getModelText(config);
  const displayModel = config.model_uppercase ? modelText.toUpperCase() : modelText;
  const layout = calculateLayout(config, displayModel);

  const bounds: Record<string, { x: number; y: number; w: number; h: number }> = {};

  bounds.circle = {
    x: layout.cx - layout.radius,
    y: layout.cy - layout.radius,
    w: layout.radius * 2,
    h: layout.radius * 2,
  };

  bounds.id_box = {
    x: layout.idBox.x,
    y: layout.idBox.y,
    w: layout.idBox.width,
    h: layout.idBox.height,
  };

  if (layout.image) {
    bounds.gear_image = {
      x: layout.image.x,
      y: layout.image.y,
      w: layout.image.width,
      h: layout.image.height,
    };
  }

  if (layout.brandText && config.brand_text) {
    const fontSize = toCanvasSize(config.brand_font_size);
    const approxWidth = config.brand_text.length * fontSize * 0.55;
    bounds.brand_text = {
      x: layout.brandText.x - approxWidth / 2,
      y: layout.brandText.y - fontSize / 2,
      w: approxWidth,
      h: fontSize,
    };
  }

  if (layout.modelText) {
    const fontSize = toCanvasSize(config.model_font_size);
    const lines = layout.modelText.lines;
    const maxWidth = Math.max(...lines.map(l => l.length * fontSize * 0.52));
    const totalHeight = lines.length * fontSize * 1.2;
    bounds.model_text = {
      x: layout.modelText.x - maxWidth / 2,
      y: layout.modelText.y - fontSize / 2,
      w: maxWidth,
      h: totalHeight,
    };
  }

  return bounds;
}
