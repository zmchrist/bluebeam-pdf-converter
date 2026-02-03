import { FileText } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-100 rounded-lg">
            <FileText className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              Bluebeam PDF Map Converter
            </h1>
            <p className="text-sm text-gray-500">
              Convert bid maps to deployment maps
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
