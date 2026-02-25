import { Minus, Plus } from 'lucide-react';

interface NumericInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
}

export function NumericInput({
  label,
  value,
  onChange,
  min = -50,
  max = 50,
  step = 0.1,
  disabled = false,
}: NumericInputProps) {
  const roundedValue = Math.round(value * 100) / 100;

  return (
    <div className={`flex items-center justify-between gap-2${disabled ? ' opacity-50 pointer-events-none' : ''}`}>
      <label className="text-xs text-gray-600 dark:text-gray-400 whitespace-nowrap">
        {label}
      </label>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onChange(Math.max(min, roundedValue - step))}
          disabled={disabled}
          className="p-0.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
        >
          <Minus className="h-3 w-3 text-gray-500" />
        </button>
        <input
          type="number"
          value={roundedValue}
          onChange={e => {
            const v = parseFloat(e.target.value);
            if (!isNaN(v)) onChange(Math.max(min, Math.min(max, v)));
          }}
          step={step}
          disabled={disabled}
          className="w-16 text-xs text-center bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded px-1 py-0.5"
        />
        <button
          onClick={() => onChange(Math.min(max, roundedValue + step))}
          disabled={disabled}
          className="p-0.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
        >
          <Plus className="h-3 w-3 text-gray-500" />
        </button>
      </div>
    </div>
  );
}
