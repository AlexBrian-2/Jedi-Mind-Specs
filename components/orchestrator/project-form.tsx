'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Slider } from '@/components/ui/slider';
import { useOrchestratorStore } from '@/lib/orchestrator-store';
import { useOrchestration } from '@/hooks/use-orchestration';
import type { ProjectType, RunConfig } from '@/lib/types';
import { PROJECT_TYPE_LABELS } from '@/lib/types';
import { ChevronDown, Play, Square, Settings } from 'lucide-react';
import { Spinner } from '@/components/ui/spinner';

const MODELS = [
  { value: 'openai/gpt-4o-mini', label: 'GPT-4o Mini (Recommended)' },
  { value: 'openai/gpt-4o', label: 'GPT-4o' },
  { value: 'anthropic/claude-sonnet-4', label: 'Claude Sonnet 4' },
  { value: 'anthropic/claude-opus-4.6', label: 'Claude Opus 4.6' },
];

export function ProjectForm() {
  const isRunning = useOrchestratorStore((state) => state.isRunning);
  const cancelRun = useOrchestratorStore((state) => state.cancelRun);
  const { runOrchestration } = useOrchestration();
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const [config, setConfig] = useState<RunConfig>({
    projectName: '',
    projectType: 'web_app',
    projectDescription: '',
    maxReviewCycles: 3,
    maxValidationCycles: 2,
    interCallDelay: 2000,
    model: 'openai/gpt-4o-mini',
  });
  
  const isValid = config.projectName.trim().length > 0 && 
                  config.projectDescription.trim().length >= 100;
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid && !isRunning) {
      await runOrchestration(config);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5 p-4">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground uppercase tracking-wider mb-2">
        <Settings className="w-4 h-4" />
        Project Configuration
      </div>
      
      <div className="flex flex-col gap-2">
        <Label htmlFor="projectName">Project Name</Label>
        <Input
          id="projectName"
          placeholder="My Awesome Project"
          value={config.projectName}
          onChange={(e) => setConfig({ ...config, projectName: e.target.value })}
          disabled={isRunning}
          className="bg-secondary border-border"
        />
      </div>
      
      <div className="flex flex-col gap-2">
        <Label htmlFor="projectType">Project Type</Label>
        <Select
          value={config.projectType}
          onValueChange={(value: ProjectType) => setConfig({ ...config, projectType: value })}
          disabled={isRunning}
        >
          <SelectTrigger id="projectType" className="bg-secondary border-border">
            <SelectValue placeholder="Select project type" />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(PROJECT_TYPE_LABELS).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="projectDescription">Project Description</Label>
          <span className={`text-xs ${config.projectDescription.length >= 100 ? 'text-status-complete' : 'text-muted-foreground'}`}>
            {config.projectDescription.length} / 100 min
          </span>
        </div>
        <Textarea
          id="projectDescription"
          placeholder="Describe your project in detail. Include the target audience, key features, technical requirements, and any specific constraints. The more context you provide, the better the research results will be..."
          value={config.projectDescription}
          onChange={(e) => setConfig({ ...config, projectDescription: e.target.value })}
          disabled={isRunning}
          className="bg-secondary border-border min-h-[160px] resize-none"
        />
        <p className="text-xs text-muted-foreground">
          Provide at least 100 characters for meaningful research results.
        </p>
      </div>
      
      <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            type="button"
            className="w-full justify-between text-muted-foreground hover:text-foreground"
          >
            Advanced Settings
            <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="flex flex-col gap-4 pt-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="model">Model</Label>
            <Select
              value={config.model}
              onValueChange={(value) => setConfig({ ...config, model: value })}
              disabled={isRunning}
            >
              <SelectTrigger id="model" className="bg-secondary border-border">
                <SelectValue placeholder="Select model" />
              </SelectTrigger>
              <SelectContent>
                {MODELS.map((model) => (
                  <SelectItem key={model.value} value={model.value}>
                    {model.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <Label>Max Review Cycles</Label>
              <span className="text-sm font-mono text-muted-foreground">{config.maxReviewCycles}</span>
            </div>
            <Slider
              value={[config.maxReviewCycles]}
              onValueChange={([value]) => setConfig({ ...config, maxReviewCycles: value })}
              min={1}
              max={5}
              step={1}
              disabled={isRunning}
              className="w-full"
            />
          </div>
          
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <Label>Inter-call Delay (ms)</Label>
              <span className="text-sm font-mono text-muted-foreground">{config.interCallDelay}</span>
            </div>
            <Slider
              value={[config.interCallDelay]}
              onValueChange={([value]) => setConfig({ ...config, interCallDelay: value })}
              min={500}
              max={5000}
              step={500}
              disabled={isRunning}
              className="w-full"
            />
          </div>
        </CollapsibleContent>
      </Collapsible>
      
      <div className="flex flex-col gap-2 mt-2">
        {isRunning ? (
          <Button 
            type="button" 
            variant="destructive" 
            onClick={cancelRun}
            className="w-full"
          >
            <Square className="w-4 h-4 mr-2" />
            Cancel Run
          </Button>
        ) : (
          <Button 
            type="submit" 
            disabled={!isValid}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
          >
            <Play className="w-4 h-4 mr-2" />
            Start Research Run
          </Button>
        )}
      </div>
    </form>
  );
}
