import { Check, Loader2 } from 'lucide-react';
import { cn } from '../../../lib/utils';
import type { WorkflowStep } from '../../../types';

interface ProgressDisplayProps {
  currentStep: WorkflowStep;
}

const steps = [
  { key: 'uploading', label: 'Uploading PDF' },
  { key: 'uploaded', label: 'PDF Uploaded' },
  { key: 'converting', label: 'Converting Icons' },
  { key: 'converted', label: 'Conversion Complete' },
] as const;

function getStepStatus(
  stepKey: string,
  currentStep: WorkflowStep
): 'complete' | 'current' | 'pending' {
  const stepOrder = ['uploading', 'uploaded', 'converting', 'converted'];
  const currentIndex = stepOrder.indexOf(currentStep);
  const stepIndex = stepOrder.indexOf(stepKey);

  if (stepIndex < currentIndex) return 'complete';
  if (stepIndex === currentIndex) return 'current';
  return 'pending';
}

export function ProgressDisplay({ currentStep }: ProgressDisplayProps) {
  if (currentStep === 'idle' || currentStep === 'error') return null;

  return (
    <div className="py-4">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(step.key, currentStep);
          return (
            <div key={step.key} className="flex items-center">
              {/* Step indicator */}
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center transition-all',
                    status === 'complete' && 'bg-green-500',
                    status === 'current' && 'bg-primary-500',
                    status === 'pending' && 'bg-gray-200'
                  )}
                >
                  {status === 'complete' ? (
                    <Check className="h-5 w-5 text-white" />
                  ) : status === 'current' ? (
                    <Loader2 className="h-5 w-5 text-white animate-spin" />
                  ) : (
                    <span className="text-sm text-gray-500">{index + 1}</span>
                  )}
                </div>
                <span
                  className={cn(
                    'mt-2 text-xs font-medium text-center',
                    status === 'complete' && 'text-green-600',
                    status === 'current' && 'text-primary-600',
                    status === 'pending' && 'text-gray-400'
                  )}
                >
                  {step.label}
                </span>
              </div>
              {/* Connector line */}
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-1 mx-2 rounded',
                    status === 'complete' ? 'bg-green-500' : 'bg-gray-200'
                  )}
                  style={{ minWidth: '40px' }}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
