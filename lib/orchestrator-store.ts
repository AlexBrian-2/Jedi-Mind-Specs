import { create } from 'zustand';
import type {
  RunContext,
  RunConfig,
  Agent,
  AgentStatus,
  WorkflowState,
  SpecDocument,
  LogEntry,
  RateLimitState,
} from './types';
import { createRunContext } from './types';

interface OrchestratorState {
  // Run context
  runContext: RunContext | null;
  isRunning: boolean;
  
  // Rate limit state
  rateLimitState: RateLimitState;
  
  // Selected document for viewing
  selectedDocumentId: string | null;
  
  // Actions
  startRun: (config: RunConfig) => void;
  cancelRun: () => void;
  
  // Agent updates
  updateAgentStatus: (agentId: string, status: AgentStatus, currentAction?: string | null) => void;
  setAgentComplete: (agentId: string) => void;
  
  // Workflow updates
  setWorkflowState: (state: WorkflowState) => void;
  
  // Document management
  addDocument: (document: SpecDocument) => void;
  selectDocument: (documentId: string | null) => void;
  
  // Logging
  addLog: (agentId: string, agentName: string, message: string, level: LogEntry['level']) => void;
  
  // Rate limit updates
  updateRateLimitState: (state: Partial<RateLimitState>) => void;
  incrementApiCallCount: () => void;
  
  // URL tracking
  addVisitedUrl: (url: string) => void;
  hasVisitedUrl: (url: string) => boolean;
  
  // Review/Validation cycles
  incrementReviewCycles: () => void;
  incrementValidationCycles: () => void;
}

const initialRateLimitState: RateLimitState = {
  requestsThisHour: 0,
  softLimit: 180,
  hardLimit: 200,
  windowResetTime: new Date(Date.now() + 3600000),
  queueDepth: 0,
  tokensAvailable: 10,
  maxBurst: 10,
};

export const useOrchestratorStore = create<OrchestratorState>((set, get) => ({
  runContext: null,
  isRunning: false,
  rateLimitState: initialRateLimitState,
  selectedDocumentId: null,
  
  startRun: (config: RunConfig) => {
    const runContext = createRunContext(config);
    runContext.startTime = new Date();
    runContext.workflowState = 'parsing';
    
    set({
      runContext,
      isRunning: true,
      rateLimitState: {
        ...initialRateLimitState,
        windowResetTime: new Date(Date.now() + 3600000),
      },
    });
    
    // Add initial log
    get().addLog('master', 'Master Agent', `Starting research run for "${config.projectName}"`, 'info');
  },
  
  cancelRun: () => {
    const { runContext } = get();
    if (runContext) {
      set({
        runContext: {
          ...runContext,
          workflowState: 'idle',
          endTime: new Date(),
        },
        isRunning: false,
      });
      get().addLog('master', 'Master Agent', 'Run cancelled by user', 'warning');
    }
  },
  
  updateAgentStatus: (agentId: string, status: AgentStatus, currentAction?: string | null) => {
    const { runContext } = get();
    if (!runContext) return;
    
    const agent = runContext.agents[agentId];
    if (!agent) return;
    
    set({
      runContext: {
        ...runContext,
        agents: {
          ...runContext.agents,
          [agentId]: {
            ...agent,
            status,
            currentAction: currentAction ?? agent.currentAction,
            startTime: status === 'active' ? Date.now() : agent.startTime,
          },
        },
      },
    });
  },
  
  setAgentComplete: (agentId: string) => {
    get().updateAgentStatus(agentId, 'complete', null);
  },
  
  setWorkflowState: (state: WorkflowState) => {
    const { runContext } = get();
    if (!runContext) return;
    
    set({
      runContext: {
        ...runContext,
        workflowState: state,
        endTime: state === 'complete' ? new Date() : runContext.endTime,
      },
      isRunning: state !== 'complete' && state !== 'idle',
    });
  },
  
  addDocument: (document: SpecDocument) => {
    const { runContext } = get();
    if (!runContext) return;
    
    set({
      runContext: {
        ...runContext,
        documents: [...runContext.documents, document],
      },
    });
    
    // Auto-select first document
    if (runContext.documents.length === 0) {
      set({ selectedDocumentId: document.id });
    }
  },
  
  selectDocument: (documentId: string | null) => {
    set({ selectedDocumentId: documentId });
  },
  
  addLog: (agentId: string, agentName: string, message: string, level: LogEntry['level']) => {
    const { runContext } = get();
    if (!runContext) return;
    
    const logEntry: LogEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date(),
      agentId,
      agentName,
      message,
      level,
    };
    
    set({
      runContext: {
        ...runContext,
        logs: [...runContext.logs, logEntry],
      },
    });
  },
  
  updateRateLimitState: (state: Partial<RateLimitState>) => {
    set({
      rateLimitState: {
        ...get().rateLimitState,
        ...state,
      },
    });
  },
  
  incrementApiCallCount: () => {
    const { runContext, rateLimitState } = get();
    if (!runContext) return;
    
    set({
      runContext: {
        ...runContext,
        apiCallCount: runContext.apiCallCount + 1,
      },
      rateLimitState: {
        ...rateLimitState,
        requestsThisHour: rateLimitState.requestsThisHour + 1,
        tokensAvailable: Math.max(0, rateLimitState.tokensAvailable - 1),
      },
    });
  },
  
  addVisitedUrl: (url: string) => {
    const { runContext } = get();
    if (!runContext) return;
    
    const newVisitedUrls = new Set(runContext.visitedUrls);
    newVisitedUrls.add(url);
    
    set({
      runContext: {
        ...runContext,
        visitedUrls: newVisitedUrls,
      },
    });
  },
  
  hasVisitedUrl: (url: string) => {
    const { runContext } = get();
    return runContext?.visitedUrls.has(url) ?? false;
  },
  
  incrementReviewCycles: () => {
    const { runContext } = get();
    if (!runContext) return;
    
    set({
      runContext: {
        ...runContext,
        reviewCycles: runContext.reviewCycles + 1,
      },
    });
  },
  
  incrementValidationCycles: () => {
    const { runContext } = get();
    if (!runContext) return;
    
    set({
      runContext: {
        ...runContext,
        validationCycles: runContext.validationCycles + 1,
      },
    });
  },
}));
