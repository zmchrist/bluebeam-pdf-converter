import { Download } from 'lucide-react';
import { getDownloadUrl } from '../../../lib/api';

interface DownloadButtonProps {
  fileId: string;
  fileName: string;
}

export function DownloadButton({ fileId, fileName }: DownloadButtonProps) {
  const downloadUrl = getDownloadUrl(fileId);

  // Style anchor directly as button to avoid nested interactive elements
  return (
    <a
      href={downloadUrl}
      download={fileName}
      className="inline-flex items-center justify-center w-full px-6 py-3 text-lg font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 focus:ring-purple-500 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40"
    >
      <Download className="h-5 w-5 mr-2" />
      Download {fileName}
    </a>
  );
}
