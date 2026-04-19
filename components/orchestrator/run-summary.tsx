'use client';

import { useCallback } from 'react';
import { useOrchestratorStore } from '@/lib/orchestrator-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Download, FileText, Clock, Zap, CheckCircle2, RotateCcw } from 'lucide-react';
import { PROJECT_TYPE_LABELS, type SpecDocument } from '@/lib/types';

function formatDuration(start: Date | null, end: Date | null): string {
  if (!start) return '--';
  if (!end) return 'Running...';
  const duration = end.getTime() - start.getTime();
  const minutes = Math.floor(duration / 60000);
  const seconds = Math.floor((duration % 60000) / 1000);
  return `${minutes}m ${seconds}s`;
}

export function RunSummary() {
  // Use specific selectors to avoid re-render loops
  const workflowState = useOrchestratorStore((state) => state.runContext?.workflowState ?? 'idle');
  const projectName = useOrchestratorStore((state) => state.runContext?.projectName ?? '');
  const projectType = useOrchestratorStore((state) => state.runContext?.projectType ?? 'web_app');
  const startTime = useOrchestratorStore((state) => state.runContext?.startTime ?? null);
  const endTime = useOrchestratorStore((state) => state.runContext?.endTime ?? null);
  const apiCallCount = useOrchestratorStore((state) => state.runContext?.apiCallCount ?? 0);
  const documentsCount = useOrchestratorStore((state) => state.runContext?.documents.length ?? 0);
  const reviewCycles = useOrchestratorStore((state) => state.runContext?.reviewCycles ?? 0);
  const validationCycles = useOrchestratorStore((state) => state.runContext?.validationCycles ?? 0);
  
  // Get documents array reference for export
  const getDocuments = useCallback(() => {
    return useOrchestratorStore.getState().runContext?.documents ?? [];
  }, []);
  
  if (workflowState === 'idle') {
    return null;
  }
  
  const handleExportAll = () => {
    const documents = getDocuments();
    if (documents.length === 0) return;
    
    // Create a combined markdown file
    const combined = documents.map((doc: SpecDocument) => {
      return `# ${doc.title}\n\n${doc.content}\n\n---\n\n`;
    }).join('');
    
    const blob = new Blob([combined], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName.replace(/\s+/g, '_')}_specs.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const isComplete = workflowState === 'complete';
  
  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary" />
          Run Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">Project</span>
            <p className="font-medium truncate">{projectName}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Type</span>
            <p className="font-medium">{PROJECT_TYPE_LABELS[projectType]}</p>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">Duration</span>
              <p className="font-mono font-medium">
                {formatDuration(startTime, endTime)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">API Calls</span>
              <p className="font-mono font-medium">{apiCallCount}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">Documents</span>
              <p className="font-mono font-medium">{documentsCount}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">Cycles</span>
              <p className="font-mono font-medium">
                R:{reviewCycles} V:{validationCycles}
              </p>
            </div>
          </div>
        </div>
        
        {isComplete && documentsCount > 0 && (
          <Button
            onClick={handleExportAll}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
          >
            <Download className="w-4 h-4 mr-2" />
            Export All Documents
          </Button>
        )}
        
        {isComplete && (
          <div className="flex items-center justify-center gap-2 text-status-complete text-sm">
            <CheckCircle2 className="w-4 h-4" />
            Research run complete
          </div>
        )}
      </CardContent>
    </Card>
  );
}
