'use client';

import { useMemo, useState, useCallback } from 'react';
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
          
          {agent.status === 'active' && (
            <span className="text-xs font-mono text-status-active">
              ...
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

// Use a stable selector that only picks agent-specific data
function AgentNodeWithChildren({ agentId, depth }: { agentId: string; depth: number }) {
  // Select only the specific agent data needed
  const agentState = useOrchestratorStore(
    useCallback((state) => state.runContext?.agents[agentId], [agentId])
  );
  
  // Get static definition
  const agentDef = useMemo(
    () => AGENT_HIERARCHY.find((a) => a.id === agentId),
    [agentId]
  );
  
  if (!agentDef) return null;
  
  const agent: Agent = {
    ...agentDef,
    status: agentState?.status ?? 'idle',
    currentAction: agentState?.currentAction ?? null,
    startTime: agentState?.startTime ?? null,
  };
  
  // Get children definitions (static)
  const childDefs = useMemo(
    () => AGENT_HIERARCHY.filter((a) => a.parentId === agentId),
    [agentId]
  );
  
  // Get children states from store - use a selector that returns stable reference
  const childrenStates = useOrchestratorStore(
    useCallback((state) => {
      if (!state.runContext) return null;
      return childDefs.map((def) => state.runContext!.agents[def.id]);
    }, [childDefs])
  );
  
  const children: Agent[] = childDefs.map((def, i) => ({
    ...def,
    status: childrenStates?.[i]?.status ?? 'idle',
    currentAction: childrenStates?.[i]?.currentAction ?? null,
    startTime: childrenStates?.[i]?.startTime ?? null,
  }));
  
  return <AgentNode agent={agent} children={children.length > 0 ? children : undefined} depth={depth} />;
}

export function AgentTree() {
  // Use specific selectors to avoid unnecessary re-renders
  const agents = useOrchestratorStore((state) => state.runContext?.agents);
  
  // Get stats with a memoized calculation
  const stats = useMemo(() => {
    if (!agents) {
      return { total: 22, active: 0, complete: 0, pending: 22 };
    }
    
    const agentList = Object.values(agents);
    return {
      total: agentList.length,
      active: agentList.filter((a) => a.status === 'active').length,
      complete: agentList.filter((a) => a.status === 'complete').length,
      pending: agentList.filter((a) => a.status === 'idle').length,
    };
  }, [agents]);
  
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
