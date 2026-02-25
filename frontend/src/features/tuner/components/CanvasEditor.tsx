import { useRef } from 'react';
import type { IconConfig, CanvasState, LayerId } from '../../../types/tuner';
import { useCanvasRenderer } from '../hooks/useCanvasRenderer';
import { useCanvasInteraction } from '../hooks/useCanvasInteraction';
import { CANVAS_WIDTH, CANVAS_HEIGHT } from '../utils/canvasDrawing';
import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';

interface CanvasEditorProps {
  config: IconConfig;
  canvasState: CanvasState;
  layerVisibility: Record<LayerId, boolean>;
  onCanvasStateChange: (state: CanvasState | ((prev: CanvasState) => CanvasState)) => void;
  onConfigChange: (updates: Partial<IconConfig>, description: string) => void;
}

export function CanvasEditor({
  config,
  canvasState,
  layerVisibility,
  onCanvasStateChange,
  onConfigChange,
}: CanvasEditorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useCanvasRenderer(canvasRef, config, canvasState, layerVisibility);
  const { onMouseDown, onMouseMove, onMouseUp, onWheel } = useCanvasInteraction(
    canvasRef,
    config,
    canvasState,
    onCanvasStateChange,
    onConfigChange,
  );

  const handleZoom = (factor: number) => {
    onCanvasStateChange(prev => ({
      ...prev,
      zoom: Math.max(0.5, Math.min(5, prev.zoom * factor)),
    }));
  };

  const handleFit = () => {
    onCanvasStateChange(prev => ({
      ...prev,
      zoom: 1,
      panX: 0,
      panY: 0,
    }));
  };

  return (
    <div className="relative bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <canvas
        ref={canvasRef}
        width={CANVAS_WIDTH}
        height={CANVAS_HEIGHT}
        className="w-full"
        style={{ maxHeight: '700px' }}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        onWheel={onWheel}
      />
      {/* Zoom controls */}
      <div className="absolute bottom-3 right-3 flex items-center gap-1 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-1">
        <button
          onClick={() => handleZoom(1.2)}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          title="Zoom in"
        >
          <ZoomIn className="h-4 w-4 text-gray-600 dark:text-gray-400" />
        </button>
        <span className="text-xs text-gray-500 dark:text-gray-400 px-1 min-w-[3rem] text-center">
          {Math.round(canvasState.zoom * 100)}%
        </span>
        <button
          onClick={() => handleZoom(0.8)}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          title="Zoom out"
        >
          <ZoomOut className="h-4 w-4 text-gray-600 dark:text-gray-400" />
        </button>
        <button
          onClick={handleFit}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          title="Fit to view"
        >
          <Maximize className="h-4 w-4 text-gray-600 dark:text-gray-400" />
        </button>
      </div>
    </div>
  );
}
