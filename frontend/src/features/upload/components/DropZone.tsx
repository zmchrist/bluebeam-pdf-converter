import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText } from 'lucide-react';
import { cn, isPDFFile, isFileSizeValid, MAX_FILE_SIZE, formatFileSize } from '../../../lib/utils';

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  error?: string | null;
}

export function DropZone({ onFileSelect, disabled = false, error }: DropZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        if (!isPDFFile(file)) {
          return; // Will be handled by onDropRejected
        }
        if (!isFileSizeValid(file)) {
          return; // Will be handled by onDropRejected
        }
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: MAX_FILE_SIZE,
    maxFiles: 1,
    disabled,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all',
        isDragActive && !isDragReject && 'border-primary-500 bg-primary-50',
        isDragReject && 'border-red-500 bg-red-50',
        !isDragActive && !error && 'border-gray-300 hover:border-primary-400 hover:bg-gray-50',
        error && 'border-red-300 bg-red-50',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        <div
          className={cn(
            'p-4 rounded-full',
            isDragActive && !isDragReject && 'bg-primary-100',
            isDragReject && 'bg-red-100',
            !isDragActive && 'bg-gray-100'
          )}
        >
          {isDragReject ? (
            <FileText className="h-10 w-10 text-red-500" />
          ) : (
            <Upload
              className={cn(
                'h-10 w-10',
                isDragActive ? 'text-primary-600' : 'text-gray-400'
              )}
            />
          )}
        </div>
        <div>
          <p className="text-lg font-medium text-gray-700">
            {isDragActive
              ? isDragReject
                ? 'Invalid file type'
                : 'Drop your PDF here'
              : 'Drag & drop your bid map PDF'}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            or click to browse (max {formatFileSize(MAX_FILE_SIZE)})
          </p>
        </div>
        {error && (
          <p className="text-sm text-red-600 font-medium">{error}</p>
        )}
      </div>
    </div>
  );
}
