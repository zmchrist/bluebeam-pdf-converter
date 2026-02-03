import { FileText } from 'lucide-react';

export function Header() {
  return (
    <header className="backdrop-blur-xl bg-white/70 dark:bg-gray-900/70 border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg shadow-purple-500/25">
            <FileText className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Bluebeam PDF Map Converter
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Convert bid maps to deployment maps
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
