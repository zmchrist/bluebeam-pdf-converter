import { useEffect, useRef, useCallback } from 'react';
import type { IconConfig, CanvasState, LayerId } from '../../../types/tuner';
import { drawIcon } from '../utils/canvasDrawing';

export function useCanvasRenderer(
  canvasRef: React.RefObject<HTMLCanvasElement | null>,
  config: IconConfig | null,
  canvasState: CanvasState,
  layerVisibility: Record<LayerId, boolean>,
) {
  const gearImageRef = useRef<HTMLImageElement | null>(null);
  const gearImageUrlRef = useRef<string | null>(null);
  const animFrameRef = useRef<number>(0);

  // Load gear image when path changes
  useEffect(() => {
    if (!config?.image_path || config.no_image) {
      gearImageRef.current = null;
      gearImageUrlRef.current = null;
      return;
    }

    const imagePath = config.image_path;
    // Reuse if same path
    if (gearImageUrlRef.current === imagePath && gearImageRef.current) return;

    const img = new Image();
    img.crossOrigin = 'anonymous';
    // Load from gear-images directory via static serving or construct URL
    const url = `/api/tuner/gear-image-file/${encodeURIComponent(imagePath)}`;

    // Fallback: just try to load from the known path
    img.onload = () => {
      gearImageRef.current = img;
      gearImageUrlRef.current = imagePath;
      // Trigger re-render
      render();
    };
    img.onerror = () => {
      gearImageRef.current = null;
      gearImageUrlRef.current = null;
    };
    img.src = url;
  }, [config?.image_path, config?.no_image]); // eslint-disable-line react-hooks/exhaustive-deps

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !config) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    cancelAnimationFrame(animFrameRef.current);
    animFrameRef.current = requestAnimationFrame(() => {
      ctx.save();
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Background
      ctx.fillStyle = '#f3f4f6';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Apply zoom and pan
      ctx.translate(canvasState.panX, canvasState.panY);
      ctx.scale(canvasState.zoom, canvasState.zoom);

      // Draw icon
      drawIcon(ctx, config, gearImageRef.current, layerVisibility, canvasState.selectedElement);

      ctx.restore();
    });
  }, [canvasRef, config, canvasState, layerVisibility]);

  // Re-render on any state change
  useEffect(() => {
    render();
  }, [render]);

  return { render };
}
