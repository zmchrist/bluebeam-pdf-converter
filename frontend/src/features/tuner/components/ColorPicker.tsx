import { rgbToHex, hexToRgb } from '../utils/canvasDrawing';

interface ColorPickerProps {
  label: string;
  value: [number, number, number];
  onChange: (value: [number, number, number]) => void;
}

export function ColorPicker({ label, value, onChange }: ColorPickerProps) {
  return (
    <div className="flex items-center justify-between gap-2">
      <label className="text-xs text-gray-600 dark:text-gray-400 whitespace-nowrap">
        {label}
      </label>
      <div className="flex items-center gap-2">
        <div
          className="w-6 h-6 rounded border border-gray-300 dark:border-gray-600"
          style={{ backgroundColor: rgbToHex(value) }}
        />
        <input
          type="color"
          value={rgbToHex(value)}
          onChange={e => onChange(hexToRgb(e.target.value))}
          className="w-8 h-6 cursor-pointer border-0 p-0 bg-transparent"
        />
      </div>
    </div>
  );
}
