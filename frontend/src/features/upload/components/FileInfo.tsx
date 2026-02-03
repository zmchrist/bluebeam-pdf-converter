import { FileText, Check, Layers, MapPin } from 'lucide-react';
import { Card } from '../../../components/ui/Card';
import { formatFileSize } from '../../../lib/utils';
import type { PDFUploadResponse } from '../../../types';

interface FileInfoProps {
  uploadData: PDFUploadResponse;
}

export function FileInfo({ uploadData }: FileInfoProps) {
  return (
    <Card className="bg-green-50 border-green-200">
      <Card.Body>
        <div className="flex items-start gap-4">
          <div className="p-3 bg-green-100 rounded-lg">
            <FileText className="h-8 w-8 text-green-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 truncate">
                {uploadData.file_name}
              </h3>
              <Check className="h-5 w-5 text-green-600 flex-shrink-0" />
            </div>
            <div className="mt-2 flex flex-wrap gap-4 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                {formatFileSize(uploadData.file_size)}
              </span>
              <span className="flex items-center gap-1">
                <Layers className="h-4 w-4" />
                {uploadData.page_count} page{uploadData.page_count !== 1 ? 's' : ''}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {uploadData.annotation_count} annotations
              </span>
            </div>
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}
