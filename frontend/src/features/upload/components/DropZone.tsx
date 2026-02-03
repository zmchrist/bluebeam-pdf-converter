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
        'border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200',
        'backdrop-blur-sm',
        isDragActive && !isDragReject && 'border-purple-500 bg-purple-500/10 dark:bg-purple-500/20',
        isDragReject && 'border-red-500 bg-red-500/10 dark:bg-red-500/20',
        !isDragActive && !error && 'border-gray-300 dark:border-gray-600 hover:border-purple-400 dark:hover:border-purple-500 bg-white/50 dark:bg-gray-800/50 hover:bg-purple-50/50 dark:hover:bg-purple-900/20',
        error && 'border-red-300 dark:border-red-700 bg-red-50/50 dark:bg-red-900/20',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        <div
          className={cn(
            'p-4 rounded-full',
            isDragActive && !isDragReject && 'bg-purple-100 dark:bg-purple-900/50',
            isDragReject && 'bg-red-100 dark:bg-red-900/50',
            !isDragActive && 'bg-gray-100 dark:bg-gray-800'
          )}
        >
          {isDragReject ? (
            <FileText className="h-10 w-10 text-red-500 dark:text-red-400" />
          ) : (
            <Upload
              className={cn(
                'h-10 w-10',
                isDragActive ? 'text-purple-600 dark:text-purple-400' : 'text-gray-400 dark:text-gray-500'
              )}
            />
          )}
        </div>
        <div>
          <p className="text-lg font-medium text-gray-700 dark:text-gray-200">
            {isDragActive
              ? isDragReject
                ? 'Invalid file type'
                : 'Drop your PDF here'
              : 'Drag & drop your bid map PDF'}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            or click to browse (max {formatFileSize(MAX_FILE_SIZE)})
          </p>
        </div>
        {error && (
          <p className="text-sm text-red-600 dark:text-red-400 font-medium">{error}</p>
        )}
      </div>
    </div>
  );
}
