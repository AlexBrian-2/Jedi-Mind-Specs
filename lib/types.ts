// Agent status types
export type AgentStatus = 'idle' | 'active' | 'complete' | 'warning' | 'error';

// Message types for inter-agent communication
export type MessageType = 'task_assignment' | 'result_submission' | 'status_update' | 'escalation';

// Workflow states
export type WorkflowState = 
  | 'idle'
  | 'parsing'
  | 'research_phase'
  | 'review_phase'
  | 'review_decision'
  | 'revision_phase'
  | 'validation_phase'
  | 'validation_decision'
  | 'complete';

// Project types
export type ProjectType = 
  | 'web_app'
  | 'mobile_app'
  | 'desktop_app'
  | 'api_backend'
  | 'cli_tool'
  | 'data_pipeline'
  | 'ml_system'
  | 'other';

export const PROJECT_TYPE_LABELS: Record<ProjectType, string> = {
  web_app: 'Web Application',
  mobile_app: 'Mobile Application',
  desktop_app: 'Desktop Application',
  api_backend: 'API / Backend Service',
  cli_tool: 'CLI Tool',
  data_pipeline: 'Data Pipeline',
  ml_system: 'ML / AI System',
  other: 'Other',
};

// Agent tier
export type AgentTier = 1 | 2 | 3;

// Agent definition
export interface Agent {
  id: string;
  name: string;
  role: string;
  tier: AgentTier;
  parentId: string | null;
  status: AgentStatus;
  currentAction: string | null;
  startTime: number | null;
  outputArtifact: string | null;
  tools: string[];
}

// Agent message
export interface AgentMessage {
  id: string;
  senderId: string;
  recipientId: string;
  messageType: MessageType;
  payload: unknown;
  runId: string;
  timestamp: Date;
}

// Spec document
export interface SpecDocument {
  id: string;
  type: string;
  title: string;
  agentId: string;
  agentName: string;
  content: string;
  confidence: 'high' | 'medium' | 'low';
  confidenceRationale: string;
  sources: { url: string; description: string }[];
  generatedAt: Date;
}

// Run context - single source of truth for a research run
export interface RunContext {
  id: string;
  projectName: string;
  projectType: ProjectType;
  projectDescription: string;
  workflowState: WorkflowState;
  agents: Record<string, Agent>;
  documents: SpecDocument[];
  visitedUrls: Set<string>;
  apiCallCount: number;
  reviewCycles: number;
  validationCycles: number;
  maxReviewCycles: number;
  maxValidationCycles: number;
  startTime: Date | null;
  endTime: Date | null;
  logs: LogEntry[];
}

// Log entry
export interface LogEntry {
  id: string;
  timestamp: Date;
  agentId: string;
  agentName: string;
  message: string;
  level: 'info' | 'warning' | 'error' | 'success';
}

// Rate limiter state
export interface RateLimitState {
  requestsThisHour: number;
  softLimit: number;
  hardLimit: number;
  windowResetTime: Date;
  queueDepth: number;
  tokensAvailable: number;
  maxBurst: number;
}

// Research run configuration
export interface RunConfig {
  projectName: string;
  projectType: ProjectType;
  projectDescription: string;
  maxReviewCycles: number;
  maxValidationCycles: number;
  interCallDelay: number;
  model: string;
}

// Agent hierarchy definition (used to build the tree)
export const AGENT_HIERARCHY: Omit<Agent, 'status' | 'currentAction' | 'startTime'>[] = [
  // Tier 1 - Master Agent
  {
    id: 'master',
    name: 'Master Agent',
    role: 'Orchestrates all; sole user-facing interface; no research',
    tier: 1,
    parentId: null,
    outputArtifact: 'Final report + all spec docs',
    tools: ['Task decomposition', 'Result aggregation'],
  },
  
  // Tier 2 - Frontend Lead
  {
    id: 'frontend-lead',
    name: 'Frontend Lead',
    role: 'Delegates UI/UX research; synthesizes Tier-3 outputs',
    tier: 2,
    parentId: 'master',
    outputArtifact: 'Frontend spec summary',
    tools: ['Sub-agent management'],
  },
  // Tier 3 - Frontend Specialists
  {
    id: 'wireframe',
    name: 'Wireframe & Layout',
    role: 'Researches wireframing patterns for the project type',
    tier: 3,
    parentId: 'frontend-lead',
    outputArtifact: 'wireframe_spec.md',
    tools: ['Web search', 'Layout analysis'],
  },
  {
    id: 'components',
    name: 'UI Components Library',
    role: 'Researches component libraries relevant to project',
    tier: 3,
    parentId: 'frontend-lead',
    outputArtifact: 'components_spec.md',
    tools: ['Web search'],
  },
  {
    id: 'style',
    name: 'Color & Style',
    role: 'Researches design systems and color theory',
    tier: 3,
    parentId: 'frontend-lead',
    outputArtifact: 'style_spec.md',
    tools: ['Web search'],
  },
  {
    id: 'ux',
    name: 'Overall UX/UI/GUI',
    role: 'Synthesizes UX best practices across sources',
    tier: 3,
    parentId: 'frontend-lead',
    outputArtifact: 'ux_spec.md',
    tools: ['Web search', 'Synthesis'],
  },
  
  // Tier 2 - Backend Lead
  {
    id: 'backend-lead',
    name: 'Backend Lead',
    role: 'Delegates backend research; synthesizes Tier-3 outputs',
    tier: 2,
    parentId: 'master',
    outputArtifact: 'Backend spec summary',
    tools: ['Sub-agent management'],
  },
  // Tier 3 - Backend Specialists
  {
    id: 'primary-backend',
    name: 'Primary Backend',
    role: 'Researches backend architecture patterns',
    tier: 3,
    parentId: 'backend-lead',
    outputArtifact: 'backend_spec.md',
    tools: ['Web search'],
  },
  {
    id: 'database',
    name: 'Database',
    role: 'Researches DB options and schema patterns',
    tier: 3,
    parentId: 'backend-lead',
    outputArtifact: 'database_spec.md',
    tools: ['Web search'],
  },
  {
    id: 'auth',
    name: 'Auth',
    role: 'Researches auth patterns and libraries',
    tier: 3,
    parentId: 'backend-lead',
    outputArtifact: 'auth_spec.md',
    tools: ['Web search'],
  },
  
  // Tier 2 - Specs Lead
  {
    id: 'specs-lead',
    name: 'Specs Lead',
    role: 'Delegates documentation; synthesizes all spec docs',
    tier: 2,
    parentId: 'master',
    outputArtifact: 'All spec documents',
    tools: ['Sub-agent management'],
  },
  // Tier 3 - Specs Specialists
  {
    id: 'spec-documents',
    name: 'Spec Documents',
    role: 'Compiles and formats all spec docs into master',
    tier: 3,
    parentId: 'specs-lead',
    outputArtifact: 'master_spec.md',
    tools: ['Document generation'],
  },
  {
    id: 'tech-stack',
    name: 'Tech Stack',
    role: 'Researches and recommends technology choices',
    tier: 3,
    parentId: 'specs-lead',
    outputArtifact: 'techstack_spec.md',
    tools: ['Web search', 'Comparison'],
  },
  {
    id: 'planning',
    name: 'Planning',
    role: 'Creates project timeline and milestones',
    tier: 3,
    parentId: 'specs-lead',
    outputArtifact: 'planning_spec.md',
    tools: ['Analysis'],
  },
  {
    id: 'architecture',
    name: 'Architecture',
    role: 'Designs system architecture',
    tier: 3,
    parentId: 'specs-lead',
    outputArtifact: 'architecture_spec.md',
    tools: ['Web search', 'Diagramming'],
  },
  {
    id: 'best-practices',
    name: 'Best Practices',
    role: 'Researches coding standards and patterns',
    tier: 3,
    parentId: 'specs-lead',
    outputArtifact: 'bestpractices_spec.md',
    tools: ['Web search'],
  },
  
  // Tier 2 - Review Lead
  {
    id: 'review-lead',
    name: 'Review Lead',
    role: 'Coordinates 3 review agents; manages consensus',
    tier: 2,
    parentId: 'master',
    outputArtifact: 'Review report',
    tools: ['Consensus management'],
  },
  // Tier 3 - Review Agents
  {
    id: 'review-1',
    name: 'Review Agent #1',
    role: 'Independent quality review pass',
    tier: 3,
    parentId: 'review-lead',
    outputArtifact: 'review1_report.md',
    tools: ['Analysis', 'Scoring'],
  },
  {
    id: 'review-2',
    name: 'Review Agent #2',
    role: 'Independent quality review pass',
    tier: 3,
    parentId: 'review-lead',
    outputArtifact: 'review2_report.md',
    tools: ['Analysis', 'Scoring'],
  },
  {
    id: 'review-3',
    name: 'Review Agent #3',
    role: 'Independent quality review pass',
    tier: 3,
    parentId: 'review-lead',
    outputArtifact: 'review3_report.md',
    tools: ['Analysis', 'Scoring'],
  },
  
  // Tier 2 - Validation Lead
  {
    id: 'validation-lead',
    name: 'Validation Lead',
    role: 'Coordinates 2 validation agents; final gate',
    tier: 2,
    parentId: 'master',
    outputArtifact: 'Validation report',
    tools: ['Final gate management'],
  },
  // Tier 3 - Validation Agents
  {
    id: 'validation-1',
    name: 'Validation Agent #1',
    role: 'Final validation check',
    tier: 3,
    parentId: 'validation-lead',
    outputArtifact: 'validation1_report.md',
    tools: ['Analysis'],
  },
  {
    id: 'validation-2',
    name: 'Validation Agent #2',
    role: 'Final validation check',
    tier: 3,
    parentId: 'validation-lead',
    outputArtifact: 'validation2_report.md',
    tools: ['Analysis'],
  },
];

// Helper to initialize agents with default status
export function initializeAgents(): Record<string, Agent> {
  const agents: Record<string, Agent> = {};
  for (const def of AGENT_HIERARCHY) {
    agents[def.id] = {
      ...def,
      status: 'idle',
      currentAction: null,
      startTime: null,
    };
  }
  return agents;
}

// Helper to create initial run context
export function createRunContext(config: RunConfig): RunContext {
  return {
    id: crypto.randomUUID(),
    projectName: config.projectName,
    projectType: config.projectType,
    projectDescription: config.projectDescription,
    workflowState: 'idle',
    agents: initializeAgents(),
    documents: [],
    visitedUrls: new Set(),
    apiCallCount: 0,
    reviewCycles: 0,
    validationCycles: 0,
    maxReviewCycles: config.maxReviewCycles,
    maxValidationCycles: config.maxValidationCycles,
    startTime: null,
    endTime: null,
    logs: [],
  };
}

// Workflow state labels
export const WORKFLOW_STATE_LABELS: Record<WorkflowState, string> = {
  idle: 'Ready',
  parsing: 'Analyzing Request',
  research_phase: 'Research Phase',
  review_phase: 'Review Phase',
  review_decision: 'Review Decision',
  revision_phase: 'Revision Phase',
  validation_phase: 'Validation Phase',
  validation_decision: 'Validation Decision',
  complete: 'Complete',
};
