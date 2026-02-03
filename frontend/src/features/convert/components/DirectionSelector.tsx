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
      <label className="text-sm font-medium text-gray-700">Conversion Direction</label>
      <div className="space-y-2">
        {/* Bid to Deployment - Enabled */}
        <label
          className={cn(
            'flex items-center gap-3 p-4 border rounded-lg cursor-pointer transition-all',
            value === 'bid_to_deployment'
              ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-500'
              : 'border-gray-200 hover:border-primary-300',
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
            className="h-4 w-4 text-primary-600 focus:ring-primary-500"
          />
          <div className="flex items-center gap-2">
            <span className="font-medium">Bid</span>
            <ArrowRight className="h-4 w-4 text-gray-400" />
            <span className="font-medium">Deployment</span>
          </div>
        </label>

        {/* Deployment to Bid - Disabled (Phase 2) */}
        <label
          className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg opacity-50 cursor-not-allowed"
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
            <span className="font-medium text-gray-400">Deployment</span>
            <ArrowRight className="h-4 w-4 text-gray-300" />
            <span className="font-medium text-gray-400">Bid</span>
          </div>
          <span className="ml-auto text-xs text-gray-400">(Coming soon)</span>
        </label>
      </div>
    </div>
  );
}
