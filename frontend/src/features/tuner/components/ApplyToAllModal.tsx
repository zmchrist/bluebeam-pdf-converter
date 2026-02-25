import { AlertTriangle, X } from 'lucide-react';

interface ApplyToAllModalProps {
  isOpen: boolean;
  fieldGroup: 'circle' | 'id_box' | 'gear_image' | 'brand_text' | 'model_text';
  categoryName: string;
  categoryCount: number;
  totalCount: number;
  isPending: boolean;
  onConfirm: (scope: 'category' | 'all') => void;
  onClose: () => void;
}

const FIELD_GROUP_LABELS: Record<string, string> = {
  circle: 'Circle',
  id_box: 'ID Box',
  gear_image: 'Gear Image',
  brand_text: 'Brand Text',
  model_text: 'Model Text',
};

export function ApplyToAllModal({
  isOpen,
  fieldGroup,
  categoryName,
  categoryCount,
  totalCount,
  isPending,
  onConfirm,
  onClose,
}: ApplyToAllModalProps) {
  if (!isOpen) return null;

  const label = FIELD_GROUP_LABELS[fieldGroup] || fieldGroup;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-sm w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              Apply {label} to Multiple Icons
            </h3>
          </div>
          <button
            onClick={onClose}
            disabled={isPending}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>

        {/* Body */}
        <div className="px-4 py-4 space-y-3">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            This will overwrite existing {label.toLowerCase()} values for all target icons.
          </p>

          <div className="space-y-2">
            <button
              onClick={() => onConfirm('category')}
              disabled={isPending}
              className="w-full px-3 py-2 text-sm text-left rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700/50 disabled:opacity-50"
            >
              <span className="font-medium text-gray-900 dark:text-white">
                This category only
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                {categoryName} ({categoryCount} icons)
              </span>
            </button>

            <button
              onClick={() => onConfirm('all')}
              disabled={isPending}
              className="w-full px-3 py-2 text-sm text-left rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700/50 disabled:opacity-50"
            >
              <span className="font-medium text-gray-900 dark:text-white">All icons</span>
              <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                ({totalCount} icons)
              </span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <button
            onClick={onClose}
            disabled={isPending}
            className="px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
