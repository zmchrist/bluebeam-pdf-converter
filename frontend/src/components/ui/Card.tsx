import { cn } from '../../lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn(
      'backdrop-blur-xl bg-white/60 dark:bg-gray-900/70',
      'rounded-2xl',
      'border border-white/60 dark:border-gray-700/50',
      'shadow-glass dark:shadow-glass-lg',
      'ring-1 ring-white/20 dark:ring-white/10',
      className
    )}>
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ children, className }: CardProps) {
  return (
    <div className={cn(
      'px-6 py-4 border-b border-gray-200/50 dark:border-gray-700/50',
      className
    )}>
      {children}
    </div>
  );
};

Card.Body = function CardBody({ children, className }: CardProps) {
  return (
    <div className={cn('px-6 py-4', className)}>
      {children}
    </div>
  );
};
