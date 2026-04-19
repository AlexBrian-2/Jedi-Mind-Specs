'use client';

import { useOrchestratorStore } from '@/lib/orchestrator-store';
import { WORKFLOW_STATE_LABELS } from '@/lib/types';
import type { WorkflowState } from '@/lib/types';
import { cn } from '@/lib/utils';
import {
  FileSearch,
  Search,
  ClipboardCheck,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  Shield,
  FileText,
} from 'lucide-react';

const stateConfig: Record<WorkflowState, { icon: typeof FileSearch; color: string }> = {
  idle: { icon: FileText, color: 'text-muted-foreground' },
  parsing: { icon: FileSearch, color: 'text-chart-4' },
  research_phase: { icon: Search, color: 'text-status-active' },
  review_phase: { icon: ClipboardCheck, color: 'text-chart-2' },
  review_decision: { icon: AlertCircle, color: 'text-status-warning' },
  revision_phase: { icon: RotateCcw, color: 'text-chart-3' },
  validation_phase: { icon: Shield, color: 'text-primary' },
  validation_decision: { icon: AlertCircle, color: 'text-status-warning' },
  complete: { icon: CheckCircle2, color: 'text-status-complete' },
};

const WORKFLOW_ORDER: WorkflowState[] = [
  'parsing',
  'research_phase',
  'review_phase',
  'validation_phase',
  'complete',
];

export function WorkflowStatus() {
  const currentState = useOrchestratorStore((state) => state.runContext?.workflowState ?? 'idle');
  const reviewCycles = useOrchestratorStore((state) => state.runContext?.reviewCycles ?? 0);
  const maxReviewCycles = useOrchestratorStore((state) => state.runContext?.maxReviewCycles ?? 3);
  const validationCycles = useOrchestratorStore((state) => state.runContext?.validationCycles ?? 0);
  const maxValidationCycles = useOrchestratorStore((state) => state.runContext?.maxValidationCycles ?? 2);
  const hasRunContext = useOrchestratorStore((state) => !!state.runContext);
  const currentIndex = WORKFLOW_ORDER.indexOf(currentState);
  
  return (
    <div className="flex flex-col gap-3 p-4 border-b border-border">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Workflow Status
        </h3>
        {hasRunContext && (
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span>Review: {reviewCycles}/{maxReviewCycles}</span>
            <span>Validation: {validationCycles}/{maxValidationCycles}</span>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-1">
        {WORKFLOW_ORDER.map((state, index) => {
          const { icon: Icon, color } = stateConfig[state];
          const isActive = state === currentState;
          const isComplete = currentIndex > index;
          const isPending = currentIndex < index;
          
          return (
            <div key={state} className="flex items-center flex-1">
              <div
                className={cn(
                  'flex items-center justify-center gap-2 py-2 px-3 rounded-md flex-1 transition-colors',
                  isActive && 'bg-secondary',
                  isComplete && 'bg-status-complete/10',
                  isPending && 'opacity-40'
                )}
              >
                <Icon 
                  className={cn(
                    'w-4 h-4',
                    isActive && color,
                    isComplete && 'text-status-complete',
                    isPending && 'text-muted-foreground'
                  )} 
                />
                <span 
                  className={cn(
                    'text-xs font-medium truncate',
                    isActive && 'text-foreground',
                    isComplete && 'text-status-complete',
                    isPending && 'text-muted-foreground'
                  )}
                >
                  {WORKFLOW_STATE_LABELS[state]}
                </span>
              </div>
              
              {index < WORKFLOW_ORDER.length - 1 && (
                <div 
                  className={cn(
                    'w-4 h-0.5 mx-1',
                    isComplete ? 'bg-status-complete' : 'bg-border'
                  )} 
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
