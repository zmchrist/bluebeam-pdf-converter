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
      className="inline-flex items-center justify-center w-full px-6 py-3 text-lg font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500"
    >
      <Download className="h-5 w-5 mr-2" />
      Download {fileName}
    </a>
  );
}
