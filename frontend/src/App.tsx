import { useState, useCallback } from 'react';
import { Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { Card } from './components/ui/Card';
import { Button } from './components/ui/Button';
import { Alert } from './components/ui/Alert';
import { DropZone, FileInfo, useUpload } from './features/upload';
import { ConversionPanel, useConvert } from './features/convert';
import { DownloadButton } from './features/download';
import { IconTunerPage } from './features/tuner';
import type { WorkflowStep, PDFUploadResponse, ConversionResponse, ConversionDirection } from './types';
import { RefreshCw } from 'lucide-react';

// Create QueryClient outside component to avoid recreation
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
    mutations: {
      retry: 0,
    },
  },
});

function PDFConverter() {
  // Workflow state
  const [workflowStep, setWorkflowStep] = useState<WorkflowStep>('idle');
  const [uploadData, setUploadData] = useState<PDFUploadResponse | null>(null);
  const [conversionResult, setConversionResult] = useState<ConversionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Mutations
  const uploadMutation = useUpload();
  const convertMutation = useConvert();

  // Handle file selection
  const handleFileSelect = useCallback(
    async (file: File) => {
      setError(null);
      setWorkflowStep('uploading');

      try {
        const result = await uploadMutation.mutateAsync(file);
        setUploadData(result);
        setWorkflowStep('uploaded');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Upload failed');
        setWorkflowStep('error');
      }
    },
    [uploadMutation]
  );

  // Handle conversion
  const handleConvert = useCallback(
    async (direction: ConversionDirection, outputFilename: string) => {
      if (!uploadData) return;

      setError(null);
      setWorkflowStep('converting');

      try {
        const result = await convertMutation.mutateAsync({
          uploadId: uploadData.upload_id,
          direction,
          outputFilename: outputFilename || undefined,
        });
        setConversionResult(result);
        setWorkflowStep('converted');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Conversion failed');
        setWorkflowStep('error');
      }
    },
    [uploadData, convertMutation]
  );

  // Reset to start new conversion
  const handleReset = useCallback(() => {
    setWorkflowStep('idle');
    setUploadData(null);
    setConversionResult(null);
    setError(null);
    uploadMutation.reset();
    convertMutation.reset();
  }, [uploadMutation, convertMutation]);

  const showDropZone = workflowStep === 'idle' || workflowStep === 'error';
  const showFileInfo = uploadData && workflowStep !== 'idle';
  const showConversionPanel = uploadData && (workflowStep === 'uploaded' || workflowStep === 'converting' || workflowStep === 'converted');
  const showDownload = conversionResult && workflowStep === 'converted';
  const showResetButton = workflowStep === 'converted' || workflowStep === 'error';

  return (
    <Layout>
      <div className="space-y-6">
        {/* Title and description */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Convert Your PDF Map
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Upload a PDF map to convert your bid map to a deployment map, or your deployment map to an as-built
          </p>
        </div>

        {/* Error display */}
        {error && (
          <Alert variant="error" title="Error" onDismiss={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Success message */}
        {workflowStep === 'converted' && conversionResult && (
          <Alert variant="success" title="Conversion Complete!">
            Successfully converted {conversionResult.annotations_converted} annotations.
            {conversionResult.annotations_skipped > 0 && (
              <> ({conversionResult.annotations_skipped} skipped due to missing mappings)</>
            )}
          </Alert>
        )}

        {/* Step 1: Upload */}
        {showDropZone && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Step 1: Upload PDF
              </h3>
            </Card.Header>
            <Card.Body>
              <DropZone
                onFileSelect={handleFileSelect}
                disabled={uploadMutation.isPending}
                error={workflowStep === 'error' ? error : null}
              />
            </Card.Body>
          </Card>
        )}

        {/* File info display */}
        {showFileInfo && <FileInfo uploadData={uploadData} />}

        {/* Step 2: Convert */}
        {showConversionPanel && (
          <ConversionPanel
            uploadData={uploadData}
            workflowStep={workflowStep}
            isConverting={convertMutation.isPending}
            conversionResult={conversionResult}
            onConvert={handleConvert}
          />
        )}

        {/* Step 3: Download */}
        {showDownload && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Step 3: Download
              </h3>
            </Card.Header>
            <Card.Body>
              <DownloadButton
                fileId={conversionResult.file_id}
                fileName={conversionResult.converted_file}
              />
            </Card.Body>
          </Card>
        )}

        {/* Reset button */}
        {showResetButton && (
          <div className="flex justify-center">
            <Button variant="outline" onClick={handleReset}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Convert Another PDF
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path="/" element={<PDFConverter />} />
        <Route path="/tuner" element={<IconTunerPage />} />
      </Routes>
    </QueryClientProvider>
  );
}
