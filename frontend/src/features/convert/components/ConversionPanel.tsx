import { useState, useEffect } from 'react';
import { Card } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { DirectionSelector } from './DirectionSelector';
import { ProgressDisplay } from './ProgressDisplay';
import type { ConversionDirection, WorkflowStep, PDFUploadResponse, ConversionResponse } from '../../../types';

interface ConversionPanelProps {
  uploadData: PDFUploadResponse;
  workflowStep: WorkflowStep;
  isConverting: boolean;
  conversionResult: ConversionResponse | null;
  onConvert: (direction: ConversionDirection, outputFilename: string) => void;
}

export function ConversionPanel({
  uploadData,
  workflowStep,
  isConverting,
  conversionResult,
  onConvert,
}: ConversionPanelProps) {
  const [direction, setDirection] = useState<ConversionDirection>('bid_to_deployment');
  const [outputFilename, setOutputFilename] = useState('');

  // Initialize output filename from upload data
  useEffect(() => {
    if (uploadData?.file_name) {
      const baseName = uploadData.file_name.replace(/\.pdf$/i, '');
      setOutputFilename(`${baseName}_deployment`);
    }
  }, [uploadData?.file_name]);

  const showConvertButton = workflowStep === 'uploaded';
  const showProgress = workflowStep === 'converting' || workflowStep === 'converted';

  return (
    <Card>
      <Card.Header>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Convert: {uploadData.file_name}
        </h2>
      </Card.Header>
      <Card.Body className="space-y-6">
        {/* Direction selector */}
        <DirectionSelector
          value={direction}
          onChange={setDirection}
          disabled={isConverting}
        />

        {/* Progress display */}
        {showProgress && <ProgressDisplay currentStep={workflowStep} />}

        {/* Conversion result summary */}
        {conversionResult && (
          <div className="p-4 bg-gray-100/50 dark:bg-gray-800/50 rounded-lg space-y-2">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              <span className="font-medium">Converted:</span>{' '}
              {conversionResult.annotations_converted} of {conversionResult.annotations_processed} annotations
            </p>
            {conversionResult.annotations_skipped > 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                <span className="font-medium">Skipped:</span>{' '}
                {conversionResult.annotations_skipped} (no mapping)
              </p>
            )}
            <p className="text-sm text-gray-500 dark:text-gray-400">
              <span className="font-medium">Processing time:</span>{' '}
              {(conversionResult.processing_time_ms / 1000).toFixed(1)}s
            </p>
          </div>
        )}

        {/* Output filename input */}
        <div className="space-y-2">
          <label
            htmlFor="output-filename"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Output Filename
          </label>
          <div className="flex items-center">
            <input
              type="text"
              id="output-filename"
              value={outputFilename}
              onChange={(e) => setOutputFilename(e.target.value)}
              disabled={isConverting || workflowStep === 'converted'}
              className="flex-1 rounded-l-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="Enter filename"
            />
            <span className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 rounded-r-lg">
              .pdf
            </span>
          </div>
        </div>

        {/* Convert button */}
        {showConvertButton && (
          <Button
            onClick={() => onConvert(direction, outputFilename)}
            isLoading={isConverting}
            className="w-full"
            size="lg"
          >
            Convert to Deployment Map
          </Button>
        )}
      </Card.Body>
    </Card>
  );
}
