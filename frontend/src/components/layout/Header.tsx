import { Link, useLocation } from 'react-router-dom';
import { FileText, Sliders } from 'lucide-react';

export function Header() {
  const location = useLocation();

  const navItems = [
    { to: '/', label: 'Converter', icon: FileText },
    { to: '/tuner', label: 'Icon Tuner', icon: Sliders },
  ];

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200/50 dark:border-gray-700/50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg shadow-purple-500/25">
              <FileText className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Bluebeam PDF Map Converter
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Convert bid maps and deployment maps
              </p>
            </div>
          </div>
          <nav className="flex gap-1">
            {navItems.map(({ to, label, icon: Icon }) => {
              const isActive = location.pathname === to;
              return (
                <Link
                  key={to}
                  to={to}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
