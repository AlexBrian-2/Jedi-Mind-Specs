'use client';

import { useEffect, useState } from 'react';
import { useOrchestratorStore } from '@/lib/orchestrator-store';
import { Progress } from '@/components/ui/progress';
import { Zap, Clock, Layers, Gauge } from 'lucide-react';

function formatTimeRemaining(resetTime: Date): string {
  const now = Date.now();
  const remaining = Math.max(0, resetTime.getTime() - now);
  const minutes = Math.floor(remaining / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);
  return `${minutes}m ${seconds.toString().padStart(2, '0')}s`;
}

export function RateLimitWidget() {
  const rateLimitState = useOrchestratorStore((state) => state.rateLimitState);
  const apiCallCount = useOrchestratorStore((state) => state.runContext?.apiCallCount ?? 0);
  const hasRunContext = useOrchestratorStore((state) => !!state.runContext);
  const [timeRemaining, setTimeRemaining] = useState('--:--');
  
  useEffect(() => {
    const interval = setInterval(() => {
      setTimeRemaining(formatTimeRemaining(rateLimitState.windowResetTime));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [rateLimitState.windowResetTime]);
  
  const usagePercent = (rateLimitState.requestsThisHour / rateLimitState.softLimit) * 100;
  const remaining = rateLimitState.softLimit - rateLimitState.requestsThisHour;
  
  return (
    <div className="flex items-center gap-6 px-4 py-2 bg-panel border-t border-border text-sm">
      {/* API Usage */}
      <div className="flex items-center gap-2">
        <Zap className="w-4 h-4 text-primary" />
        <span className="text-muted-foreground">API:</span>
        <span className="font-mono font-medium">
          {rateLimitState.requestsThisHour}/{rateLimitState.softLimit}
        </span>
        <Progress 
          value={usagePercent} 
          className="w-20 h-1.5" 
        />
      </div>
      
      {/* Remaining */}
      <div className="flex items-center gap-2">
        <Gauge className="w-4 h-4 text-chart-4" />
        <span className="text-muted-foreground">Remaining:</span>
        <span className="font-mono font-medium text-status-complete">{remaining}</span>
      </div>
      
      {/* Reset Timer */}
      <div className="flex items-center gap-2">
        <Clock className="w-4 h-4 text-chart-2" />
        <span className="text-muted-foreground">Reset:</span>
        <span className="font-mono font-medium">{timeRemaining}</span>
      </div>
      
      {/* Queue Depth */}
      <div className="flex items-center gap-2">
        <Layers className="w-4 h-4 text-chart-3" />
        <span className="text-muted-foreground">Queue:</span>
        <span className="font-mono font-medium">{rateLimitState.queueDepth}</span>
      </div>
      
      {/* Total API Calls */}
      {hasRunContext && (
        <div className="ml-auto flex items-center gap-2 text-muted-foreground">
          <span>Total calls this run:</span>
          <span className="font-mono font-medium text-foreground">{apiCallCount}</span>
        </div>
      )}
    </div>
  );
}
