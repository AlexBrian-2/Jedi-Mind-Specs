'use client';

import { ProjectForm } from './project-form';
import { AgentTree } from './agent-tree';
import { ActivityLog } from './activity-log';
import { RateLimitWidget } from './rate-limit-widget';
import { WorkflowStatus } from './workflow-status';
import { ResultsViewer } from './results-viewer';
import { RunSummary } from './run-summary';
import { useOrchestratorStore } from '@/lib/orchestrator-store';
import { cn } from '@/lib/utils';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';
import { Cpu, GitBranch, FileText } from 'lucide-react';

function PanelHeader({ 
  icon: Icon, 
  title, 
  badge 
}: { 
  icon: typeof Cpu; 
  title: string; 
  badge?: string;
}) {
  return (
    <div className="flex items-center gap-2 p-3 bg-panel-header border-b border-border">
      <Icon className="w-4 h-4 text-primary" />
      <span className="font-medium text-sm">{title}</span>
      {badge && (
        <span className="ml-auto text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">
          {badge}
        </span>
      )}
    </div>
  );
}

export function OrchestratorDashboard() {
  const runContext = useOrchestratorStore((state) => state.runContext);
  const isRunning = useOrchestratorStore((state) => state.isRunning);
  
  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-border bg-panel">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded bg-primary/20">
            <Cpu className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="font-semibold text-lg">Research Orchestrator</h1>
            <p className="text-xs text-muted-foreground">
              Hierarchical Multi-Agent System
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {runContext && (
            <>
              <div className="text-sm">
                <span className="text-muted-foreground">Project: </span>
                <span className="font-medium">{runContext.projectName}</span>
              </div>
              <div className={cn(
                'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium',
                isRunning 
                  ? 'bg-status-active/20 text-status-active' 
                  : 'bg-status-complete/20 text-status-complete'
              )}>
                <span className={cn(
                  'w-2 h-2 rounded-full',
                  isRunning ? 'bg-status-active animate-pulse' : 'bg-status-complete'
                )} />
                {isRunning ? 'Running' : 'Ready'}
              </div>
            </>
          )}
        </div>
      </header>
      
      {/* Workflow Status Bar */}
      {runContext && <WorkflowStatus />}
      
      {/* Main Content */}
      <ResizablePanelGroup direction="horizontal" className="flex-1">
        {/* Left Panel - Project Form */}
        <ResizablePanel defaultSize={20} minSize={15} maxSize={30}>
          <div className="flex flex-col h-full bg-panel border-r border-border overflow-hidden">
            <PanelHeader icon={GitBranch} title="Configuration" />
            <div className="flex-1 overflow-auto">
              <ProjectForm />
              <div className="p-4">
                <RunSummary />
              </div>
            </div>
          </div>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        {/* Center Panel - Agent Tree & Activity */}
        <ResizablePanel defaultSize={35} minSize={25}>
          <ResizablePanelGroup direction="vertical">
            <ResizablePanel defaultSize={60} minSize={30}>
              <div className="h-full bg-card border-r border-border overflow-hidden">
                <AgentTree />
              </div>
            </ResizablePanel>
            
            <ResizableHandle withHandle />
            
            <ResizablePanel defaultSize={40} minSize={20}>
              <div className="h-full bg-card border-r border-border overflow-hidden">
                <ActivityLog />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </ResizablePanel>
        
        <ResizableHandle withHandle />
        
        {/* Right Panel - Results Viewer */}
        <ResizablePanel defaultSize={45} minSize={30}>
          <div className="flex flex-col h-full bg-card overflow-hidden">
            <PanelHeader 
              icon={FileText} 
              title="Spec Documents" 
              badge={runContext ? `${runContext.documents.length} docs` : undefined}
            />
            <div className="flex-1 overflow-hidden">
              <ResultsViewer />
            </div>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
      
      {/* Bottom Status Bar */}
      <RateLimitWidget />
    </div>
  );
}
