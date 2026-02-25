import { useState, useMemo } from 'react';
import { X, Search } from 'lucide-react';
import { useGearImages } from '../hooks/useGearImages';

interface ImagePickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (path: string) => void;
}

const CATEGORIES = ['APs', 'Switches', 'P2Ps', 'Hardlines', 'Hardware', 'Misc'];

export function ImagePickerModal({ isOpen, onClose, onSelect }: ImagePickerModalProps) {
  const [category, setCategory] = useState('APs');
  const [search, setSearch] = useState('');
  const { data: images, isLoading } = useGearImages(category);

  const filtered = useMemo(() => {
    if (!images) return [];
    if (!search) return images;
    const lower = search.toLowerCase();
    return images.filter(img => img.filename.toLowerCase().includes(lower));
  }, [images, search]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Select Gear Image</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>

        {/* Category tabs + search */}
        <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700 space-y-2">
          <div className="flex gap-1 flex-wrap">
            {CATEGORIES.map(cat => (
              <button
                key={cat}
                onClick={() => setCategory(cat)}
                className={`px-2.5 py-1 text-xs rounded-md ${
                  category === cat
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
          <div className="relative">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-gray-400" />
            <input
              type="text"
              placeholder="Filter..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded-lg"
            />
          </div>
        </div>

        {/* Image grid */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <p className="text-sm text-gray-500 text-center py-8">Loading images...</p>
          ) : filtered.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-8">No images found</p>
          ) : (
            <div className="grid grid-cols-6 gap-3">
              {filtered.map(img => (
                <button
                  key={img.path}
                  onClick={() => { onSelect(img.path); onClose(); }}
                  className="flex flex-col items-center gap-1 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <img
                    src={`data:image/png;base64,${img.thumbnail}`}
                    alt={img.filename}
                    className="w-16 h-16 object-contain"
                  />
                  <span className="text-[10px] text-gray-500 dark:text-gray-400 truncate w-full text-center">
                    {img.filename.replace('.png', '')}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 flex justify-end">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
