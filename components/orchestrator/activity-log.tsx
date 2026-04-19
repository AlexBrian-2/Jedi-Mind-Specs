'use client';

import { useEffect, useRef, useMemo } from 'react';
import { useOrchestratorStore } from '@/lib/orchestrator-store';
import type { LogEntry } from '@/lib/types';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Terminal, Info, AlertTriangle, XCircle, CheckCircle2 } from 'lucide-react';

// Stable empty array reference to prevent re-render loops
const EMPTY_LOGS: LogEntry[] = [];

const levelConfig: Record<LogEntry['level'], { icon: typeof Info; className: string }> = {
  info: { icon: Info, className: 'text-chart-4' },
  warning: { icon: AlertTriangle, className: 'text-status-warning' },
  error: { icon: XCircle, className: 'text-status-error' },
  success: { icon: CheckCircle2, className: 'text-status-complete' },
};

function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function LogEntryItem({ entry }: { entry: LogEntry }) {
  const { icon: Icon, className } = levelConfig[entry.level];
  
  return (
    <div className="flex items-start gap-2 py-1.5 px-2 hover:bg-secondary/30 rounded text-sm">
      <span className="text-muted-foreground font-mono text-xs shrink-0 mt-0.5">
        {formatTime(entry.timestamp)}
      </span>
      <Icon className={cn('w-3.5 h-3.5 shrink-0 mt-0.5', className)} />
      <span className="font-medium text-primary shrink-0">[{entry.agentName}]</span>
      <span className="text-foreground break-words">{entry.message}</span>
    </div>
  );
}

export function ActivityLog() {
  const logs = useOrchestratorStore((state) => state.runContext?.logs ?? EMPTY_LOGS);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs.length]);
  
  return (
    <div className="flex flex-col h-full border-t border-border">
      <div className="flex items-center gap-2 p-3 border-b border-border bg-panel-header">
        <Terminal className="w-4 h-4 text-muted-foreground" />
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Activity Log
        </h3>
        <span className="ml-auto text-xs text-muted-foreground">
          {logs.length} entries
        </span>
      </div>
      
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="p-2 font-mono">
          {logs.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm py-8">
              No activity yet. Start a research run to see agent logs.
            </div>
          ) : (
            logs.map((entry) => (
              <LogEntryItem key={entry.id} entry={entry} />
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
