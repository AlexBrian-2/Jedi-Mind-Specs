'use client';

import { useOrchestratorStore } from '@/lib/orchestrator-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Download, FileText, Clock, Zap, CheckCircle2, RotateCcw } from 'lucide-react';
import { PROJECT_TYPE_LABELS } from '@/lib/types';

function formatDuration(start: Date | null, end: Date | null): string {
  if (!start) return '--';
  const endTime = end || new Date();
  const duration = endTime.getTime() - start.getTime();
  const minutes = Math.floor(duration / 60000);
  const seconds = Math.floor((duration % 60000) / 1000);
  return `${minutes}m ${seconds}s`;
}

export function RunSummary() {
  const runContext = useOrchestratorStore((state) => state.runContext);
  
  if (!runContext || runContext.workflowState === 'idle') {
    return null;
  }
  
  const handleExportAll = () => {
    if (runContext.documents.length === 0) return;
    
    // Create a combined markdown file
    const combined = runContext.documents.map((doc) => {
      return `# ${doc.title}\n\n${doc.content}\n\n---\n\n`;
    }).join('');
    
    const blob = new Blob([combined], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${runContext.projectName.replace(/\s+/g, '_')}_specs.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const isComplete = runContext.workflowState === 'complete';
  
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
            <p className="font-medium truncate">{runContext.projectName}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Type</span>
            <p className="font-medium">{PROJECT_TYPE_LABELS[runContext.projectType]}</p>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">Duration</span>
              <p className="font-mono font-medium">
                {formatDuration(runContext.startTime, runContext.endTime)}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">API Calls</span>
              <p className="font-mono font-medium">{runContext.apiCallCount}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">Documents</span>
              <p className="font-mono font-medium">{runContext.documents.length}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-muted-foreground" />
            <div>
              <span className="text-muted-foreground">Cycles</span>
              <p className="font-mono font-medium">
                R:{runContext.reviewCycles} V:{runContext.validationCycles}
              </p>
            </div>
          </div>
        </div>
        
        {isComplete && runContext.documents.length > 0 && (
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
