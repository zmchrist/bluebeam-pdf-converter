import { useState, useMemo } from 'react';
import type { IconConfig } from '../../../types/tuner';
import { rgbToCSS } from '../utils/canvasDrawing';

interface IconSelectorProps {
  icons: IconConfig[];
  isLoading: boolean;
  currentSubject: string | null;
  onSelect: (subject: string) => void;
}

const ALL_CATEGORIES = ['All', 'APs', 'Switches', 'P2Ps', 'Hardlines', 'IoT', 'Cameras', 'Misc', 'Power', 'Boxes'];

export function IconSelector({ icons, isLoading, currentSubject, onSelect }: IconSelectorProps) {
  const [category, setCategory] = useState('All');

  const filtered = useMemo(() => {
    let result = icons;
    if (category !== 'All') {
      result = result.filter(i => i.category === category);
    }
    return result.sort((a, b) => a.subject.localeCompare(b.subject));
  }, [icons, category]);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <p className="text-sm text-gray-500">Loading icons...</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3">
      {/* Category tabs */}
      <div className="flex gap-1 flex-wrap">
        {ALL_CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => {
              setCategory(cat);
              // Auto-select first icon in the category
              const catIcons = cat === 'All'
                ? [...icons].sort((a, b) => a.subject.localeCompare(b.subject))
                : icons.filter(i => i.category === cat).sort((a, b) => a.subject.localeCompare(b.subject));
              if (catIcons.length > 0) {
                onSelect(catIcons[0].subject);
              }
            }}
            className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
              category === cat
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 font-medium'
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Icon list */}
      <div className="mt-2 flex gap-1 flex-wrap max-h-32 overflow-y-auto">
        {filtered.map(icon => (
          <button
            key={icon.subject}
            onClick={() => onSelect(icon.subject)}
            className={`flex items-center gap-1.5 px-2 py-1 text-xs rounded-md transition-colors ${
              currentSubject === icon.subject
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 ring-1 ring-blue-300'
                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            <span
              className="w-3 h-3 rounded-full border border-gray-300 dark:border-gray-600 shrink-0"
              style={{ backgroundColor: rgbToCSS(icon.circle_color) }}
            />
            <span className="truncate max-w-[200px]">{icon.subject}</span>
          </button>
        ))}
        {filtered.length === 0 && (
          <p className="text-xs text-gray-400 py-2">No icons in this category</p>
        )}
      </div>
    </div>
  );
}
