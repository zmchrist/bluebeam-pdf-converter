import { useState } from 'react';
import { ChevronDown, ChevronRight, Copy } from 'lucide-react';
import type { IconConfig } from '../../../types/tuner';
import { ColorPicker } from './ColorPicker';
import { NumericInput } from './NumericInput';

interface FramePropertiesProps {
  config: IconConfig;
  onConfigChange: (updates: Partial<IconConfig>, description: string) => void;
  onApplyToAll?: (fieldGroup: 'circle' | 'id_box') => void;
}

export function FrameProperties({ config, onConfigChange, onApplyToAll }: FramePropertiesProps) {
  const [circleOpen, setCircleOpen] = useState(true);
  const [idBoxOpen, setIdBoxOpen] = useState(true);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white px-3 py-2 border-b border-gray-200 dark:border-gray-700">
        Frame Properties
      </h3>

      {/* Circle section */}
      <div className="border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center w-full">
          <button
            onClick={() => setCircleOpen(!circleOpen)}
            className="flex items-center gap-1.5 flex-1 px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50"
          >
            {circleOpen ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
            Circle
          </button>
          {onApplyToAll && (
            <button
              onClick={() => onApplyToAll('circle')}
              className="px-2 py-1 mr-1.5 text-[10px] text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded flex items-center gap-1 transition-colors"
              title="Apply circle settings to other icons"
            >
              <Copy className="h-3 w-3" />
              Apply to All
            </button>
          )}
        </div>
        {circleOpen && (
          <div className="px-3 pb-2 space-y-1.5">
            <ColorPicker
              label="Fill"
              value={config.circle_color}
              onChange={v => onConfigChange({ circle_color: v }, 'Change circle color')}
            />
            <ColorPicker
              label="Border"
              value={config.circle_border_color}
              onChange={v => onConfigChange({ circle_border_color: v }, 'Change circle border color')}
            />
            <NumericInput
              label="Border Width"
              value={config.circle_border_width}
              onChange={v => onConfigChange({ circle_border_width: v }, 'Change circle border width')}
              min={0}
              max={5}
              step={0.1}
            />
          </div>
        )}
      </div>

      {/* ID Box section */}
      <div>
        <div className="flex items-center w-full">
          <button
            onClick={() => setIdBoxOpen(!idBoxOpen)}
            className="flex items-center gap-1.5 flex-1 px-3 py-2 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50"
          >
            {idBoxOpen ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
            ID Box
          </button>
          {onApplyToAll && (
            <button
              onClick={() => onApplyToAll('id_box')}
              className="px-2 py-1 mr-1.5 text-[10px] text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded flex items-center gap-1 transition-colors"
              title="Apply ID box settings to other icons"
            >
              <Copy className="h-3 w-3" />
              Apply to All
            </button>
          )}
        </div>
        {idBoxOpen && (
          <div className="px-3 pb-2 space-y-1.5">
            <NumericInput
              label="Height"
              value={config.id_box_height}
              onChange={v => onConfigChange({ id_box_height: v }, 'Change ID box height')}
              min={1}
              max={10}
              step={0.1}
            />
            <NumericInput
              label="Width Ratio"
              value={config.id_box_width_ratio}
              onChange={v => onConfigChange({ id_box_width_ratio: v }, 'Change ID box width')}
              min={0.1}
              max={1}
              step={0.01}
            />
            <NumericInput
              label="Border Width"
              value={config.id_box_border_width}
              onChange={v => onConfigChange({ id_box_border_width: v }, 'Change ID box border')}
              min={0}
              max={3}
              step={0.05}
            />
            <NumericInput
              label="Font Size"
              value={config.id_font_size}
              onChange={v => onConfigChange({ id_font_size: v }, 'Change ID font size')}
              min={1}
              max={10}
              step={0.1}
            />
          </div>
        )}
      </div>
    </div>
  );
}
