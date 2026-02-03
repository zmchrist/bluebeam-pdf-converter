import { ArrowRight } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { ConversionDirection } from '../../../types';

interface DirectionSelectorProps {
  value: ConversionDirection;
  onChange: (direction: ConversionDirection) => void;
  disabled?: boolean;
}

export function DirectionSelector({ value, onChange, disabled }: DirectionSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Conversion Direction</label>
      <div className="space-y-2">
        {/* Bid to Deployment - Enabled */}
        <label
          className={cn(
            'flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition-all',
            value === 'bid_to_deployment'
              ? 'border-purple-500 dark:border-purple-400 bg-purple-50 dark:bg-purple-900/30 ring-2 ring-purple-500 dark:ring-purple-400'
              : 'border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <input
            type="radio"
            name="direction"
            value="bid_to_deployment"
            checked={value === 'bid_to_deployment'}
            onChange={() => onChange('bid_to_deployment')}
            disabled={disabled}
            className="h-4 w-4 text-purple-600 focus:ring-purple-500 dark:focus:ring-purple-400"
          />
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900 dark:text-gray-200">Bid</span>
            <ArrowRight className="h-4 w-4 text-gray-400 dark:text-gray-500" />
            <span className="font-medium text-gray-900 dark:text-gray-200">Deployment</span>
          </div>
        </label>

        {/* Deployment to Bid - Disabled (Phase 2) */}
        <label
          className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-700 rounded-xl opacity-50 cursor-not-allowed"
          title="Coming in Phase 2"
        >
          <input
            type="radio"
            name="direction"
            value="deployment_to_bid"
            disabled
            className="h-4 w-4 text-gray-400"
          />
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-400 dark:text-gray-500">Deployment</span>
            <ArrowRight className="h-4 w-4 text-gray-300 dark:text-gray-600" />
            <span className="font-medium text-gray-400 dark:text-gray-500">As Built</span>
          </div>
          <span className="ml-auto text-xs text-gray-400 dark:text-gray-500">(Coming soon)</span>
        </label>
      </div>
    </div>
  );
}
