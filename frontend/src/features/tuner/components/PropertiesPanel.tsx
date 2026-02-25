import { Copy } from 'lucide-react';
import type { IconConfig, SelectableElement, LayerId } from '../../../types/tuner';
import { ColorPicker } from './ColorPicker';
import { NumericInput } from './NumericInput';

interface PropertiesPanelProps {
  config: IconConfig;
  selectedElement: SelectableElement | null;
  onConfigChange: (updates: Partial<IconConfig>, description: string) => void;
  onSelectElement: (element: SelectableElement | null) => void;
  onApplyToAll?: (fieldGroup: 'gear_image' | 'brand_text' | 'model_text') => void;
}

export function PropertiesPanel({
  config,
  selectedElement,
  onConfigChange,
  onApplyToAll,
}: PropertiesPanelProps) {
  const renderGearImageProps = () => (
    <div className="space-y-1.5">
      <NumericInput
        label="Scale Ratio"
        value={config.img_scale_ratio}
        onChange={v => onConfigChange({ img_scale_ratio: v }, 'Change image scale')}
        min={0.1}
        max={3}
        step={0.02}
      />
      <NumericInput
        label="X Offset"
        value={config.img_x_offset}
        onChange={v => onConfigChange({ img_x_offset: v }, 'Change image X offset')}
        step={0.1}
      />
      <NumericInput
        label="Y Offset"
        value={config.img_y_offset}
        onChange={v => onConfigChange({ img_y_offset: v }, 'Change image Y offset')}
        step={0.1}
      />
      {config.image_path && (
        <div className="text-xs text-gray-500 dark:text-gray-400 truncate pt-1">
          Image: {config.image_path}
        </div>
      )}
    </div>
  );

  const renderBrandTextProps = () => (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-2">
        <label className="text-xs text-gray-600 dark:text-gray-400">Text</label>
        <input
          type="text"
          value={config.brand_text}
          onChange={e => onConfigChange({ brand_text: e.target.value }, 'Change brand text')}
          className="w-24 text-xs bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded px-2 py-0.5"
        />
      </div>
      <NumericInput
        label="Font Size"
        value={config.brand_font_size}
        onChange={v => onConfigChange({ brand_font_size: v }, 'Change brand font size')}
        min={0.5}
        max={8}
        step={0.1}
      />
      <NumericInput
        label="X Offset"
        value={config.brand_x_offset}
        onChange={v => onConfigChange({ brand_x_offset: v }, 'Change brand X offset')}
        step={0.1}
      />
      <NumericInput
        label="Y Offset"
        value={config.brand_y_offset}
        onChange={v => onConfigChange({ brand_y_offset: v }, 'Change brand Y offset')}
        step={0.1}
      />
      <ColorPicker
        label="Text Color"
        value={config.text_color}
        onChange={v => onConfigChange({ text_color: v }, 'Change text color')}
      />
    </div>
  );

  const renderModelTextProps = () => (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-2">
        <label className="text-xs text-gray-600 dark:text-gray-400">Override</label>
        <input
          type="text"
          value={config.model_text_override || ''}
          onChange={e => onConfigChange(
            { model_text_override: e.target.value || null },
            'Change model text override',
          )}
          placeholder="Auto-detect"
          className="w-24 text-xs bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded px-2 py-0.5"
        />
      </div>
      <NumericInput
        label="Font Size"
        value={config.model_font_size}
        onChange={v => onConfigChange({ model_font_size: v }, 'Change model font size')}
        min={0.5}
        max={8}
        step={0.1}
      />
      <NumericInput
        label="X Offset"
        value={config.model_x_offset}
        onChange={v => onConfigChange({ model_x_offset: v }, 'Change model X offset')}
        step={0.1}
      />
      <NumericInput
        label="Y Offset"
        value={config.model_y_offset}
        onChange={v => onConfigChange({ model_y_offset: v }, 'Change model Y offset')}
        step={0.1}
      />
      <div className="flex items-center justify-between gap-2">
        <label className="text-xs text-gray-600 dark:text-gray-400">Uppercase</label>
        <input
          type="checkbox"
          checked={config.model_uppercase}
          onChange={e => onConfigChange({ model_uppercase: e.target.checked }, 'Toggle uppercase')}
          className="rounded"
        />
      </div>
      <ColorPicker
        label="Text Color"
        value={config.text_color}
        onChange={v => onConfigChange({ text_color: v }, 'Change text color')}
      />
    </div>
  );

  if (!selectedElement || selectedElement === 'circle' || selectedElement === 'id_box') {
    return null;
  }

  const title = {
    gear_image: 'Gear Image',
    brand_text: 'Brand Text',
    model_text: 'Model Text',
  }[selectedElement];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          {title} Properties
        </h3>
        {onApplyToAll && (
          <button
            onClick={() => onApplyToAll(selectedElement as LayerId)}
            className="p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title={`Apply ${title} settings to all icons`}
          >
            <Copy className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
      <div className="px-3 py-2">
        {selectedElement === 'gear_image' && renderGearImageProps()}
        {selectedElement === 'brand_text' && renderBrandTextProps()}
        {selectedElement === 'model_text' && renderModelTextProps()}
      </div>
    </div>
  );
}
