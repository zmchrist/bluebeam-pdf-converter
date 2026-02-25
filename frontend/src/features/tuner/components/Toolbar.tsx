import { useState, useCallback } from 'react';
import { Save, Undo2, Redo2, RotateCcw, Image, Plus, Loader2 } from 'lucide-react';
import type { IconConfig } from '../../../types/tuner';
import { renderTestPdf } from '../../../lib/tunerApi';
import { useCreateIcon } from '../hooks/useIconConfig';

interface ToolbarProps {
  currentSubject: string | null;
  isDirty: boolean;
  canUndo: boolean;
  canRedo: boolean;
  onSave: () => void;
  onUndo: () => void;
  onRedo: () => void;
  onReset: () => void;
  onSelectSubject: (subject: string) => void;
  isSaving: boolean;
  icons: IconConfig[];
  onError: (msg: string) => void;
}

export function Toolbar({
  currentSubject,
  isDirty,
  canUndo,
  canRedo,
  onSave,
  onUndo,
  onRedo,
  onReset,
  onSelectSubject,
  isSaving,
  icons,
  onError,
}: ToolbarProps) {
  const [showNewDialog, setShowNewDialog] = useState(false);
  const [newSubject, setNewSubject] = useState('');
  const [newCategory, setNewCategory] = useState('APs');
  const [cloneFrom, setCloneFrom] = useState('');
  const [isRendering, setIsRendering] = useState(false);
  const createIconMutation = useCreateIcon();

  const handleTestPdf = useCallback(async () => {
    if (!currentSubject) return;
    setIsRendering(true);
    try {
      const blob = await renderTestPdf(currentSubject);
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Render failed');
    } finally {
      setIsRendering(false);
    }
  }, [currentSubject, onError]);

  const handleCreateIcon = useCallback(async () => {
    if (!newSubject.trim()) return;
    try {
      await createIconMutation.mutateAsync({
        subject: newSubject.trim(),
        category: newCategory,
        clone_from: cloneFrom || undefined,
      });
      onSelectSubject(newSubject.trim());
      setShowNewDialog(false);
      setNewSubject('');
      setCloneFrom('');
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Create failed');
    }
  }, [newSubject, newCategory, cloneFrom, createIconMutation, onSelectSubject, onError]);

  const categories = ['APs', 'Switches', 'P2Ps', 'Hardlines', 'IoT', 'Cameras', 'Cables', 'Misc', 'Power', 'Boxes'];

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-2 flex items-center gap-2 flex-wrap">
        <button
          onClick={onSave}
          disabled={!isDirty || isSaving || !currentSubject}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
          Save
        </button>

        <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />

        <button
          onClick={onUndo}
          disabled={!canUndo}
          className="p-1.5 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded disabled:opacity-30"
          title="Undo (Ctrl+Z)"
        >
          <Undo2 className="h-4 w-4" />
        </button>
        <button
          onClick={onRedo}
          disabled={!canRedo}
          className="p-1.5 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded disabled:opacity-30"
          title="Redo (Ctrl+Y)"
        >
          <Redo2 className="h-4 w-4" />
        </button>

        <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />

        <button
          onClick={onReset}
          disabled={!currentSubject}
          className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg disabled:opacity-50"
          title="Reset to defaults"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reset
        </button>

        <button
          onClick={handleTestPdf}
          disabled={!currentSubject || isRendering}
          className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg disabled:opacity-50"
          title="Test in PDF"
        >
          {isRendering ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Image className="h-3.5 w-3.5" />}
          Test PDF
        </button>

        <div className="flex-1" />

        <button
          onClick={() => setShowNewDialog(true)}
          className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
        >
          <Plus className="h-3.5 w-3.5" />
          New Icon
        </button>
      </div>

      {/* New icon dialog */}
      {showNewDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full mx-4 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Create New Icon</h3>

            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Subject Name</label>
              <input
                type="text"
                value={newSubject}
                onChange={e => setNewSubject(e.target.value)}
                placeholder="e.g., AP - Custom Model"
                className="w-full mt-1 px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded-lg"
              />
            </div>

            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Category</label>
              <select
                value={newCategory}
                onChange={e => setNewCategory(e.target.value)}
                className="w-full mt-1 px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded-lg"
              >
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-gray-600 dark:text-gray-400">Clone From (optional)</label>
              <select
                value={cloneFrom}
                onChange={e => setCloneFrom(e.target.value)}
                className="w-full mt-1 px-3 py-1.5 text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded-lg"
              >
                <option value="">Category defaults</option>
                {icons.map(i => (
                  <option key={i.subject} value={i.subject}>{i.subject}</option>
                ))}
              </select>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => { setShowNewDialog(false); setNewSubject(''); setCloneFrom(''); }}
                className="px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateIcon}
                disabled={!newSubject.trim() || createIconMutation.isPending}
                className="px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {createIconMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
