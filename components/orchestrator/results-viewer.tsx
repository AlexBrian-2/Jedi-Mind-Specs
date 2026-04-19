'use client';

import { useOrchestratorStore } from '@/lib/orchestrator-store';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import ReactMarkdown from 'react-markdown';
import { Copy, Download, FileText, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState } from 'react';
import type { SpecDocument } from '@/lib/types';

// Stable empty array reference to prevent re-render loops
const EMPTY_DOCUMENTS: SpecDocument[] = [];

const confidenceColors = {
  high: 'bg-status-complete/20 text-status-complete border-status-complete/30',
  medium: 'bg-status-warning/20 text-status-warning border-status-warning/30',
  low: 'bg-status-error/20 text-status-error border-status-error/30',
};

export function ResultsViewer() {
  const documents = useOrchestratorStore((state) => state.runContext?.documents ?? EMPTY_DOCUMENTS);
  const selectedDocumentId = useOrchestratorStore((state) => state.selectedDocumentId);
  const selectDocument = useOrchestratorStore((state) => state.selectDocument);
  const [copied, setCopied] = useState(false);
  const selectedDocument = documents.find((d) => d.id === selectedDocumentId);
  
  const handleCopy = async () => {
    if (selectedDocument) {
      await navigator.clipboard.writeText(selectedDocument.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };
  
  const handleDownload = () => {
    if (selectedDocument) {
      const blob = new Blob([selectedDocument.content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedDocument.type}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };
  
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
          <FileText className="w-8 h-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">No Documents Yet</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Start a research run to generate specification documents. Each agent will produce a detailed spec that appears here.
        </p>
      </div>
    );
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* Document Tabs */}
      <Tabs
        value={selectedDocumentId ?? undefined}
        onValueChange={selectDocument}
        className="flex flex-col h-full"
      >
        <div className="border-b border-border px-2 pt-2 overflow-x-auto">
          <TabsList className="bg-transparent h-auto p-0 gap-1">
            {documents.map((doc) => (
              <TabsTrigger
                key={doc.id}
                value={doc.id}
                className={cn(
                  'data-[state=active]:bg-secondary data-[state=active]:shadow-none',
                  'rounded-t-md rounded-b-none border-b-2',
                  'data-[state=active]:border-b-primary data-[state=inactive]:border-b-transparent',
                  'px-4 py-2'
                )}
              >
                <span className="truncate max-w-[120px]">{doc.title}</span>
              </TabsTrigger>
            ))}
          </TabsList>
        </div>
        
        {documents.map((doc) => (
          <TabsContent key={doc.id} value={doc.id} className="flex-1 flex flex-col m-0">
            {/* Document Header */}
            <div className="flex items-center justify-between p-4 border-b border-border bg-panel-header">
              <div className="flex items-center gap-3">
                <h2 className="font-semibold">{doc.title}</h2>
                <Badge 
                  variant="outline" 
                  className={cn('capitalize', confidenceColors[doc.confidence])}
                >
                  {doc.confidence} confidence
                </Badge>
                <span className="text-xs text-muted-foreground">
                  by {doc.agentName}
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopy}
                  className="gap-2"
                >
                  {copied ? (
                    <CheckCircle2 className="w-4 h-4 text-status-complete" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                  {copied ? 'Copied!' : 'Copy'}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDownload}
                  className="gap-2"
                >
                  <Download className="w-4 h-4" />
                  Save As
                </Button>
              </div>
            </div>
            
            {/* Document Content */}
            <ScrollArea className="flex-1">
              <div className="p-6 prose prose-invert prose-sm max-w-none">
                <ReactMarkdown
                  components={{
                    h1: ({ children }) => (
                      <h1 className="text-2xl font-bold mt-8 mb-4 first:mt-0">{children}</h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-xl font-semibold mt-6 mb-3 text-primary">{children}</h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-lg font-medium mt-4 mb-2">{children}</h3>
                    ),
                    p: ({ children }) => (
                      <p className="text-foreground/90 leading-relaxed mb-4">{children}</p>
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc list-inside space-y-1 mb-4 text-foreground/90">{children}</ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal list-inside space-y-1 mb-4 text-foreground/90">{children}</ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-foreground/90">{children}</li>
                    ),
                    code: ({ className, children }) => {
                      const isInline = !className;
                      if (isInline) {
                        return (
                          <code className="bg-secondary px-1.5 py-0.5 rounded text-sm font-mono text-primary">
                            {children}
                          </code>
                        );
                      }
                      return (
                        <code className="block bg-secondary p-4 rounded-md overflow-x-auto font-mono text-sm">
                          {children}
                        </code>
                      );
                    },
                    pre: ({ children }) => (
                      <pre className="bg-secondary p-4 rounded-md overflow-x-auto mb-4">
                        {children}
                      </pre>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-2 border-primary pl-4 italic text-muted-foreground mb-4">
                        {children}
                      </blockquote>
                    ),
                    a: ({ href, children }) => (
                      <a 
                        href={href} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary underline hover:text-primary/80"
                      >
                        {children}
                      </a>
                    ),
                    table: ({ children }) => (
                      <div className="overflow-x-auto mb-4">
                        <table className="w-full border-collapse border border-border">
                          {children}
                        </table>
                      </div>
                    ),
                    th: ({ children }) => (
                      <th className="border border-border bg-secondary px-4 py-2 text-left font-medium">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="border border-border px-4 py-2">{children}</td>
                    ),
                    hr: () => <hr className="border-border my-6" />,
                  }}
                >
                  {doc.content}
                </ReactMarkdown>
                
                {/* Sources Section */}
                {doc.sources.length > 0 && (
                  <div className="mt-8 pt-6 border-t border-border">
                    <h3 className="text-lg font-medium mb-4">Sources Consulted</h3>
                    <ul className="space-y-2">
                      {doc.sources.map((source, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-muted-foreground">{index + 1}.</span>
                          <div>
                            <a 
                              href={source.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-primary hover:underline"
                            >
                              {source.url}
                            </a>
                            <span className="text-muted-foreground"> — {source.description}</span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
