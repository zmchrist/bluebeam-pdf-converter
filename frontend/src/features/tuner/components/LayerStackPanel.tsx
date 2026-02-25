import { Eye, EyeOff, ChevronUp, ChevronDown, ChevronsUp, ChevronsDown } from 'lucide-react';
import type { IconConfig, LayerId, SelectableElement } from '../../../types/tuner';

interface LayerStackPanelProps {
  config: IconConfig;
  layerVisibility: Record<LayerId, boolean>;
  selectedElement: SelectableElement | null;
  onConfigChange: (updates: Partial<IconConfig>, description: string) => void;
  onVisibilityChange: (visibility: Record<LayerId, boolean>) => void;
  onSelectElement: (element: SelectableElement | null) => void;
}

const LAYER_LABELS: Record<LayerId, string> = {
  gear_image: 'Gear Image',
  brand_text: 'Brand Text',
  model_text: 'Model Text',
};

export function LayerStackPanel({
  config,
  layerVisibility,
  selectedElement,
  onConfigChange,
  onVisibilityChange,
  onSelectElement,
}: LayerStackPanelProps) {
  const layers = config.layer_order as LayerId[];

  const moveLayer = (layerId: LayerId, direction: 'up' | 'down' | 'top' | 'bottom') => {
    const index = layers.indexOf(layerId);
    if (index === -1) return;

    const newOrder = [...layers];
    newOrder.splice(index, 1);

    let newIndex: number;
    switch (direction) {
      case 'up':
        newIndex = Math.max(0, index - 1);
        break;
      case 'down':
        newIndex = Math.min(newOrder.length, index + 1);
        break;
      case 'top':
        newIndex = 0;
        break;
      case 'bottom':
        newIndex = newOrder.length;
        break;
    }

    newOrder.splice(newIndex, 0, layerId);
    onConfigChange({ layer_order: newOrder }, `Reorder ${LAYER_LABELS[layerId]}`);
  };

  const toggleVisibility = (layerId: LayerId) => {
    onVisibilityChange({
      ...layerVisibility,
      [layerId]: !layerVisibility[layerId],
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white px-3 py-2 border-b border-gray-200 dark:border-gray-700">
        Layers
      </h3>
      <div className="divide-y divide-gray-100 dark:divide-gray-700">
        {layers.map((layerId, index) => (
          <div
            key={layerId}
            className={`flex items-center gap-1 px-2 py-1.5 cursor-pointer transition-colors ${
              selectedElement === layerId
                ? 'bg-blue-50 dark:bg-blue-900/20'
                : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
            }`}
            onClick={() => onSelectElement(layerId)}
          >
            <button
              onClick={e => { e.stopPropagation(); toggleVisibility(layerId); }}
              className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              title={layerVisibility[layerId] ? 'Hide' : 'Show'}
            >
              {layerVisibility[layerId] ? (
                <Eye className="h-3.5 w-3.5 text-gray-500" />
              ) : (
                <EyeOff className="h-3.5 w-3.5 text-gray-400" />
              )}
            </button>
            <span className="text-xs text-gray-700 dark:text-gray-300 flex-1">
              {LAYER_LABELS[layerId]}
            </span>
            <div className="flex gap-0.5">
              <button
                onClick={e => { e.stopPropagation(); moveLayer(layerId, 'top'); }}
                disabled={index === 0}
                className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded disabled:opacity-30"
                title="Move to front"
              >
                <ChevronsUp className="h-3 w-3 text-gray-500" />
              </button>
              <button
                onClick={e => { e.stopPropagation(); moveLayer(layerId, 'up'); }}
                disabled={index === 0}
                className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded disabled:opacity-30"
                title="Move up"
              >
                <ChevronUp className="h-3 w-3 text-gray-500" />
              </button>
              <button
                onClick={e => { e.stopPropagation(); moveLayer(layerId, 'down'); }}
                disabled={index === layers.length - 1}
                className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded disabled:opacity-30"
                title="Move down"
              >
                <ChevronDown className="h-3 w-3 text-gray-500" />
              </button>
              <button
                onClick={e => { e.stopPropagation(); moveLayer(layerId, 'bottom'); }}
                disabled={index === layers.length - 1}
                className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded disabled:opacity-30"
                title="Move to back"
              >
                <ChevronsDown className="h-3 w-3 text-gray-500" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
