import { useState, useCallback, useEffect, useMemo } from 'react';
import { Layout } from '../../../components/layout/Layout';
import { Alert } from '../../../components/ui/Alert';
import type { IconConfig, CanvasState, SelectableElement, LayerId, ApplyToAllRequest } from '../../../types/tuner';
import { IconSelector } from '../components/IconSelector';
import { CanvasEditor } from '../components/CanvasEditor';
import { PropertiesPanel } from '../components/PropertiesPanel';
import { FrameProperties } from '../components/FrameProperties';
import { LayerStackPanel } from '../components/LayerStackPanel';
import { ApplyToAllModal } from '../components/ApplyToAllModal';
import { Toolbar } from '../components/Toolbar';
import { useIconList, useIconConfig, useSaveIcon } from '../hooks/useIconConfig';
import { useHistory } from '../hooks/useHistory';
import { useApplyToAll } from '../hooks/useApplyToAll';

export function IconTunerPage() {
  const [currentSubject, setCurrentSubject] = useState<string | null>(null);
  const [config, setConfig] = useState<IconConfig | null>(null);
  const [savedConfig, setSavedConfig] = useState<IconConfig | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [layerVisibility, setLayerVisibility] = useState<Record<LayerId, boolean>>({
    gear_image: true,
    brand_text: true,
    model_text: true,
  });
  const [canvasState, setCanvasState] = useState<CanvasState>({
    zoom: 1,
    panX: 0,
    panY: 0,
    selectedElement: null,
    isDragging: false,
  });

  const history = useHistory();
  const iconListQuery = useIconList();
  const iconConfigQuery = useIconConfig(currentSubject);
  const saveIconMutation = useSaveIcon();
  const applyToAllMutation = useApplyToAll();

  const [applyModalOpen, setApplyModalOpen] = useState(false);
  const [applyFieldGroup, setApplyFieldGroup] = useState<'circle' | 'id_box' | 'gear_image' | 'brand_text' | 'model_text'>('circle');

  // Load config when subject changes
  useEffect(() => {
    if (iconConfigQuery.data) {
      setConfig(iconConfigQuery.data);
      setSavedConfig(iconConfigQuery.data);
      history.reset(iconConfigQuery.data);
    }
  }, [iconConfigQuery.data]); // eslint-disable-line react-hooks/exhaustive-deps

  const isDirty = config && savedConfig
    ? JSON.stringify(config) !== JSON.stringify(savedConfig)
    : false;

  const updateConfig = useCallback((updates: Partial<IconConfig>, description: string) => {
    setConfig(prev => {
      if (!prev) return prev;
      const next = { ...prev, ...updates };
      history.push(next, description);
      return next;
    });
  }, [history]);

  const handleSelectElement = useCallback((element: SelectableElement | null) => {
    setCanvasState(prev => ({ ...prev, selectedElement: element }));
  }, []);

  const handleSave = useCallback(async () => {
    if (!config || !currentSubject) return;
    try {
      const result = await saveIconMutation.mutateAsync({
        subject: currentSubject,
        config,
      });
      setSavedConfig(result);
      setSuccessMessage('Icon configuration saved successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Save failed');
    }
  }, [config, currentSubject, saveIconMutation]);

  const handleReset = useCallback(() => {
    if (!currentSubject || !savedConfig) return;
    setConfig(savedConfig);
    history.reset(savedConfig);
    setSuccessMessage('Reset to last saved state');
    setTimeout(() => setSuccessMessage(null), 3000);
  }, [currentSubject, savedConfig, history]);

  const handleUndo = useCallback(() => {
    const prev = history.undo();
    if (prev) setConfig(prev);
  }, [history]);

  const handleRedo = useCallback(() => {
    const next = history.redo();
    if (next) setConfig(next);
  }, [history]);

  const handleOpenApplyModal = useCallback((fieldGroup: 'circle' | 'id_box' | 'gear_image' | 'brand_text' | 'model_text') => {
    setApplyFieldGroup(fieldGroup);
    setApplyModalOpen(true);
  }, []);

  const handleConfirmApply = useCallback(async (scope: 'category' | 'all') => {
    if (!config || !currentSubject) return;
    const request: ApplyToAllRequest = {
      field_group: applyFieldGroup,
      scope,
      source_subject: currentSubject,
    };
    if (applyFieldGroup === 'circle') {
      request.circle_color = config.circle_color;
      request.circle_border_width = config.circle_border_width;
      request.circle_border_color = config.circle_border_color;
    } else if (applyFieldGroup === 'id_box') {
      request.id_box_height = config.id_box_height;
      request.id_box_width_ratio = config.id_box_width_ratio;
      request.id_box_border_width = config.id_box_border_width;
      request.id_box_y_offset = config.id_box_y_offset;
      request.no_id_box = config.no_id_box;
      request.id_font_size = config.id_font_size;
    } else if (applyFieldGroup === 'gear_image') {
      request.img_scale_ratio = config.img_scale_ratio;
      request.img_x_offset = config.img_x_offset;
      request.img_y_offset = config.img_y_offset;
    } else if (applyFieldGroup === 'brand_text') {
      request.brand_text = config.brand_text;
      request.brand_font_size = config.brand_font_size;
      request.brand_x_offset = config.brand_x_offset;
      request.brand_y_offset = config.brand_y_offset;
      request.text_color = config.text_color;
    } else if (applyFieldGroup === 'model_text') {
      request.model_font_size = config.model_font_size;
      request.model_x_offset = config.model_x_offset;
      request.model_y_offset = config.model_y_offset;
      request.model_uppercase = config.model_uppercase;
      request.model_text_override = config.model_text_override;
    }
    try {
      const result = await applyToAllMutation.mutateAsync(request);
      setApplyModalOpen(false);
      const groupLabels: Record<string, string> = {
        circle: 'circle', id_box: 'ID box', gear_image: 'gear image',
        brand_text: 'brand text', model_text: 'model text',
      };
      setSuccessMessage(
        `Applied ${groupLabels[applyFieldGroup] || applyFieldGroup} settings to ${result.affected_count} icons`,
      );
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Apply failed');
    }
  }, [config, currentSubject, applyFieldGroup, applyToAllMutation]);

  const { categoryCount, totalCount, categoryName } = useMemo(() => {
    const icons = iconListQuery.data || [];
    const currentCategory = config?.category || '';
    return {
      categoryName: currentCategory,
      categoryCount: icons.filter(i => i.category === currentCategory).length,
      totalCount: icons.length,
    };
  }, [iconListQuery.data, config?.category]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
      } else if (mod && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        handleRedo();
      } else if (mod && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [handleUndo, handleRedo, handleSave]);

  // Warn before navigating away with unsaved changes
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [isDirty]);

  return (
    <Layout wide>
      <div className="space-y-4">
        {/* Messages */}
        {successMessage && (
          <Alert variant="success" title="Success" onDismiss={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}
        {errorMessage && (
          <Alert variant="error" title="Error" onDismiss={() => setErrorMessage(null)}>
            {errorMessage}
          </Alert>
        )}

        {/* Toolbar */}
        <Toolbar
          currentSubject={currentSubject}
          isDirty={isDirty}
          canUndo={history.canUndo}
          canRedo={history.canRedo}
          onSave={handleSave}
          onUndo={handleUndo}
          onRedo={handleRedo}
          onReset={handleReset}
          onSelectSubject={setCurrentSubject}
          isSaving={saveIconMutation.isPending}
          icons={iconListQuery.data || []}
          onError={setErrorMessage}
        />

        {/* Icon Selector */}
        <IconSelector
          icons={iconListQuery.data || []}
          isLoading={iconListQuery.isLoading}
          currentSubject={currentSubject}
          onSelect={setCurrentSubject}
        />

        {/* Main Content: Canvas + Sidebar */}
        {config ? (
          <div className="flex gap-4">
            {/* Canvas */}
            <div className="flex-1 min-w-0">
              <CanvasEditor
                config={config}
                canvasState={canvasState}
                layerVisibility={layerVisibility}
                onCanvasStateChange={setCanvasState}
                onConfigChange={updateConfig}
              />
            </div>

            {/* Right Sidebar */}
            <div className="w-80 space-y-4 shrink-0">
              <FrameProperties
                config={config}
                onConfigChange={updateConfig}
                onApplyToAll={handleOpenApplyModal}
              />
              <PropertiesPanel
                config={config}
                selectedElement={canvasState.selectedElement}
                onConfigChange={updateConfig}
                onSelectElement={handleSelectElement}
                onApplyToAll={handleOpenApplyModal}
              />
              <LayerStackPanel
                config={config}
                layerVisibility={layerVisibility}
                selectedElement={canvasState.selectedElement}
                onConfigChange={updateConfig}
                onVisibilityChange={setLayerVisibility}
                onSelectElement={handleSelectElement}
              />
            </div>
          </div>
        ) : (
          <div className="text-center py-20 text-gray-500 dark:text-gray-400">
            <p className="text-lg">Select an icon from the list above to start editing</p>
          </div>
        )}
      </div>

      <ApplyToAllModal
        isOpen={applyModalOpen}
        fieldGroup={applyFieldGroup}
        categoryName={categoryName}
        categoryCount={categoryCount}
        totalCount={totalCount}
        isPending={applyToAllMutation.isPending}
        onConfirm={handleConfirmApply}
        onClose={() => setApplyModalOpen(false)}
      />
    </Layout>
  );
}
