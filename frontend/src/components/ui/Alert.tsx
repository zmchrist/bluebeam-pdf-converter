import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react';
import { cn } from '../../lib/utils';

interface AlertProps {
  variant: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  children: React.ReactNode;
  className?: string;
  onDismiss?: () => void;
}

const variantConfig = {
  success: {
    bg: 'bg-green-50/80 dark:bg-green-900/20',
    border: 'border-green-200/50 dark:border-green-700/50',
    text: 'text-green-800 dark:text-green-200',
    icon: CheckCircle,
    iconColor: 'text-green-500 dark:text-green-400',
  },
  error: {
    bg: 'bg-red-50/80 dark:bg-red-900/20',
    border: 'border-red-200/50 dark:border-red-700/50',
    text: 'text-red-800 dark:text-red-200',
    icon: XCircle,
    iconColor: 'text-red-500 dark:text-red-400',
  },
  warning: {
    bg: 'bg-yellow-50/80 dark:bg-yellow-900/20',
    border: 'border-yellow-200/50 dark:border-yellow-700/50',
    text: 'text-yellow-800 dark:text-yellow-200',
    icon: AlertCircle,
    iconColor: 'text-yellow-500 dark:text-yellow-400',
  },
  info: {
    bg: 'bg-blue-50/80 dark:bg-blue-900/20',
    border: 'border-blue-200/50 dark:border-blue-700/50',
    text: 'text-blue-800 dark:text-blue-200',
    icon: Info,
    iconColor: 'text-blue-500 dark:text-blue-400',
  },
};

export function Alert({ variant, title, children, className, onDismiss }: AlertProps) {
  const config = variantConfig[variant];
  const Icon = config.icon;

  return (
    <div
      role="alert"
      className={cn(
        'backdrop-blur-sm rounded-xl border p-4',
        config.bg,
        config.border,
        className
      )}
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <Icon className={cn('h-5 w-5', config.iconColor)} />
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={cn('text-sm font-medium', config.text)}>{title}</h3>
          )}
          <div className={cn('text-sm', config.text, title && 'mt-1')}>
            {children}
          </div>
        </div>
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              onClick={onDismiss}
              className={cn(
                'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
                config.text,
                'hover:bg-white/50 dark:hover:bg-black/20'
              )}
            >
              <span className="sr-only">Dismiss</span>
              <X className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
