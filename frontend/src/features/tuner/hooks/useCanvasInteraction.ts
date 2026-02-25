import { useCallback, useRef } from 'react';
import type { IconConfig, CanvasState, SelectableElement } from '../../../types/tuner';
import { getElementBounds, CANVAS_SCALE } from '../utils/canvasDrawing';

interface DragState {
  startX: number;
  startY: number;
  element: SelectableElement | null;
  startPanX: number;
  startPanY: number;
  startConfigValues: { x: number; y: number };
}

export function useCanvasInteraction(
  canvasRef: React.RefObject<HTMLCanvasElement | null>,
  config: IconConfig | null,
  canvasState: CanvasState,
  onCanvasStateChange: (state: CanvasState | ((prev: CanvasState) => CanvasState)) => void,
  onConfigChange: (updates: Partial<IconConfig>, description: string) => void,
) {
  const dragRef = useRef<DragState | null>(null);

  const screenToCanvas = useCallback(
    (screenX: number, screenY: number) => {
      const canvas = canvasRef.current;
      if (!canvas) return { x: 0, y: 0 };
      const rect = canvas.getBoundingClientRect();
      const x = (screenX - rect.left - canvasState.panX) / canvasState.zoom;
      const y = (screenY - rect.top - canvasState.panY) / canvasState.zoom;
      return { x, y };
    },
    [canvasRef, canvasState.panX, canvasState.panY, canvasState.zoom],
  );

  const hitTest = useCallback(
    (canvasX: number, canvasY: number): SelectableElement | null => {
      if (!config) return null;
      const bounds = getElementBounds(config);

      // Test in reverse draw order (top-most first)
      // Layers first (in reverse layer_order), then id_box, then circle
      const layerOrder = [...config.layer_order].reverse();
      for (const layerId of layerOrder) {
        const b = bounds[layerId];
        if (b && canvasX >= b.x && canvasX <= b.x + b.w && canvasY >= b.y && canvasY <= b.y + b.h) {
          return layerId as SelectableElement;
        }
      }
      // ID box
      if (bounds.id_box) {
        const b = bounds.id_box;
        if (canvasX >= b.x && canvasX <= b.x + b.w && canvasY >= b.y && canvasY <= b.y + b.h) {
          return 'id_box';
        }
      }
      // Circle
      if (bounds.circle) {
        const b = bounds.circle;
        const cx = b.x + b.w / 2;
        const cy = b.y + b.h / 2;
        const r = b.w / 2;
        const dist = Math.sqrt((canvasX - cx) ** 2 + (canvasY - cy) ** 2);
        if (dist <= r) return 'circle';
      }
      return null;
    },
    [config],
  );

  const getConfigOffsets = useCallback(
    (element: SelectableElement): { x: number; y: number; xKey: string; yKey: string } => {
      switch (element) {
        case 'gear_image':
          return {
            x: config?.img_x_offset ?? 0,
            y: config?.img_y_offset ?? 0,
            xKey: 'img_x_offset',
            yKey: 'img_y_offset',
          };
        case 'brand_text':
          return {
            x: config?.brand_x_offset ?? 0,
            y: config?.brand_y_offset ?? 0,
            xKey: 'brand_x_offset',
            yKey: 'brand_y_offset',
          };
        case 'model_text':
          return {
            x: config?.model_x_offset ?? 0,
            y: config?.model_y_offset ?? 0,
            xKey: 'model_x_offset',
            yKey: 'model_y_offset',
          };
        default:
          return { x: 0, y: 0, xKey: '', yKey: '' };
      }
    },
    [config],
  );

  const onMouseDown = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const { x, y } = screenToCanvas(e.clientX, e.clientY);
      const element = hitTest(x, y);

      onCanvasStateChange(prev => ({
        ...prev,
        selectedElement: element,
        isDragging: true,
      }));

      if (element && element !== 'circle' && element !== 'id_box') {
        // Draggable layer
        const offsets = getConfigOffsets(element);
        dragRef.current = {
          startX: e.clientX,
          startY: e.clientY,
          element,
          startPanX: canvasState.panX,
          startPanY: canvasState.panY,
          startConfigValues: { x: offsets.x, y: offsets.y },
        };
      } else {
        // Pan mode
        dragRef.current = {
          startX: e.clientX,
          startY: e.clientY,
          element: null,
          startPanX: canvasState.panX,
          startPanY: canvasState.panY,
          startConfigValues: { x: 0, y: 0 },
        };
      }
    },
    [screenToCanvas, hitTest, onCanvasStateChange, canvasState, getConfigOffsets],
  );

  const onMouseMove = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!dragRef.current) {
        // Update cursor based on hover
        const { x, y } = screenToCanvas(e.clientX, e.clientY);
        const element = hitTest(x, y);
        const canvas = canvasRef.current;
        if (canvas) {
          if (element && element !== 'circle' && element !== 'id_box') {
            canvas.style.cursor = 'move';
          } else if (element) {
            canvas.style.cursor = 'pointer';
          } else {
            canvas.style.cursor = 'grab';
          }
        }
        return;
      }

      const dx = e.clientX - dragRef.current.startX;
      const dy = e.clientY - dragRef.current.startY;

      if (dragRef.current.element && config) {
        // Dragging a layer - convert pixel delta to PDF units
        const pdfDx = dx / (CANVAS_SCALE * canvasState.zoom);
        const pdfDy = -dy / (CANVAS_SCALE * canvasState.zoom); // Flip Y for PDF coords
        const offsets = getConfigOffsets(dragRef.current.element);
        const updates: Partial<IconConfig> = {};
        if (offsets.xKey) {
          (updates as Record<string, number>)[offsets.xKey] =
            Math.round((dragRef.current.startConfigValues.x + pdfDx) * 10) / 10;
        }
        if (offsets.yKey) {
          (updates as Record<string, number>)[offsets.yKey] =
            Math.round((dragRef.current.startConfigValues.y + pdfDy) * 10) / 10;
        }
        onConfigChange(updates, `Move ${dragRef.current.element}`);
      } else {
        // Panning
        onCanvasStateChange(prev => ({
          ...prev,
          panX: dragRef.current!.startPanX + dx,
          panY: dragRef.current!.startPanY + dy,
        }));
      }
    },
    [screenToCanvas, hitTest, canvasRef, config, canvasState.zoom, onCanvasStateChange, onConfigChange, getConfigOffsets],
  );

  const onMouseUp = useCallback(() => {
    dragRef.current = null;
    onCanvasStateChange(prev => ({ ...prev, isDragging: false }));
  }, [onCanvasStateChange]);

  const onWheel = useCallback(
    (e: React.WheelEvent<HTMLCanvasElement>) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      onCanvasStateChange(prev => ({
        ...prev,
        zoom: Math.max(0.5, Math.min(5, prev.zoom * delta)),
      }));
    },
    [onCanvasStateChange],
  );

  return { onMouseDown, onMouseMove, onMouseUp, onWheel };
}
