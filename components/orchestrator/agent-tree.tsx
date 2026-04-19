'use client';

import { useMemo } from 'react';
import { useOrchestratorStore } from '@/lib/orchestrator-store';
import type { Agent, AgentStatus } from '@/lib/types';
import { AGENT_HIERARCHY } from '@/lib/types';
import { cn } from '@/lib/utils';
import {
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  Circle,
  ChevronRight,
} from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { useState } from 'react';

const statusConfig: Record<AgentStatus, { icon: typeof Clock; className: string; label: string }> = {
  idle: { icon: Circle, className: 'text-status-idle', label: 'Idle' },
  active: { icon: Loader2, className: 'text-status-active animate-spin', label: 'Active' },
  complete: { icon: CheckCircle2, className: 'text-status-complete', label: 'Complete' },
  warning: { icon: AlertTriangle, className: 'text-status-warning', label: 'Warning' },
  error: { icon: XCircle, className: 'text-status-error', label: 'Error' },
};

interface AgentNodeProps {
  agent: Agent;
  children?: Agent[];
  depth: number;
}

function formatElapsedTime(startTime: number | null): string {
  if (!startTime) return '';
  const elapsed = Date.now() - startTime;
  const seconds = Math.floor(elapsed / 1000);
  const minutes = Math.floor(seconds / 60);
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

function AgentNode({ agent, children, depth }: AgentNodeProps) {
  const [isOpen, setIsOpen] = useState(true);
  const hasChildren = children && children.length > 0;
  const StatusIcon = statusConfig[agent.status].icon;
  
  const tierColors: Record<number, string> = {
    1: 'border-l-primary',
    2: 'border-l-chart-4',
    3: 'border-l-chart-2',
  };
  
  return (
    <div className="flex flex-col">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div
          className={cn(
            'flex items-center gap-2 py-2 px-3 rounded-md transition-colors',
            'hover:bg-secondary/50 cursor-pointer',
            'border-l-2',
            tierColors[agent.tier] || 'border-l-border',
            agent.status === 'active' && 'bg-status-active/10'
          )}
          style={{ marginLeft: depth * 16 }}
        >
          {hasChildren && (
            <CollapsibleTrigger asChild>
              <button className="p-0.5 hover:bg-secondary rounded">
                <ChevronRight
                  className={cn(
                    'w-3.5 h-3.5 text-muted-foreground transition-transform',
                    isOpen && 'rotate-90'
                  )}
                />
              </button>
            </CollapsibleTrigger>
          )}
          
          {!hasChildren && <div className="w-4" />}
          
          <div className="relative">
            <StatusIcon className={cn('w-4 h-4', statusConfig[agent.status].className)} />
            {agent.status === 'active' && (
              <span className="absolute inset-0 rounded-full bg-status-active/30 animate-ping" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm truncate">{agent.name}</span>
              <span className="text-xs px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">
                T{agent.tier}
              </span>
            </div>
            {agent.currentAction && (
              <p className="text-xs text-muted-foreground truncate mt-0.5">
                {agent.currentAction}
              </p>
            )}
          </div>
          
          {agent.status === 'active' && agent.startTime && (
            <span className="text-xs font-mono text-status-active">
              {formatElapsedTime(agent.startTime)}
            </span>
          )}
        </div>
        
        {hasChildren && (
          <CollapsibleContent>
            {children.map((child) => (
              <AgentNodeWithChildren key={child.id} agentId={child.id} depth={depth + 1} />
            ))}
          </CollapsibleContent>
        )}
      </Collapsible>
    </div>
  );
}

function AgentNodeWithChildren({ agentId, depth }: { agentId: string; depth: number }) {
  const runContext = useOrchestratorStore((state) => state.runContext);
  
  const agent = runContext?.agents[agentId] ?? AGENT_HIERARCHY.find((a) => a.id === agentId);
  if (!agent) return null;
  
  const fullAgent: Agent = {
    ...AGENT_HIERARCHY.find((a) => a.id === agentId)!,
    status: (agent as Agent).status ?? 'idle',
    currentAction: (agent as Agent).currentAction ?? null,
    startTime: (agent as Agent).startTime ?? null,
  };
  
  const children = AGENT_HIERARCHY.filter((a) => a.parentId === agentId).map((def) => {
    const state = runContext?.agents[def.id];
    return {
      ...def,
      status: state?.status ?? 'idle',
      currentAction: state?.currentAction ?? null,
      startTime: state?.startTime ?? null,
    } as Agent;
  });
  
  return <AgentNode agent={fullAgent} children={children} depth={depth} />;
}

export function AgentTree() {
  const runContext = useOrchestratorStore((state) => state.runContext);
  
  // Get stats
  const stats = useMemo(() => {
    if (!runContext) {
      return { total: 22, active: 0, complete: 0, pending: 22 };
    }
    
    const agents = Object.values(runContext.agents);
    return {
      total: agents.length,
      active: agents.filter((a) => a.status === 'active').length,
      complete: agents.filter((a) => a.status === 'complete').length,
      pending: agents.filter((a) => a.status === 'idle').length,
    };
  }, [runContext]);
  
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-3">
          Agent Hierarchy
        </h2>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div className="bg-secondary rounded p-2">
            <div className="text-lg font-semibold">{stats.total}</div>
            <div className="text-xs text-muted-foreground">Total</div>
          </div>
          <div className="bg-secondary rounded p-2">
            <div className="text-lg font-semibold text-status-active">{stats.active}</div>
            <div className="text-xs text-muted-foreground">Active</div>
          </div>
          <div className="bg-secondary rounded p-2">
            <div className="text-lg font-semibold text-status-complete">{stats.complete}</div>
            <div className="text-xs text-muted-foreground">Done</div>
          </div>
          <div className="bg-secondary rounded p-2">
            <div className="text-lg font-semibold text-status-idle">{stats.pending}</div>
            <div className="text-xs text-muted-foreground">Pending</div>
          </div>
        </div>
      </div>
      
      {/* Tree */}
      <div className="flex-1 overflow-auto p-2">
        <AgentNodeWithChildren agentId="master" depth={0} />
      </div>
    </div>
  );
}
