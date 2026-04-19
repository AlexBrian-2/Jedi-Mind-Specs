import { streamText } from 'ai';
import type { RunConfig, SpecDocument, Agent } from '@/lib/types';
import { AGENT_HIERARCHY, PROJECT_TYPE_LABELS } from '@/lib/types';

export const maxDuration = 60;

// Agent prompts for different roles
const AGENT_PROMPTS: Record<string, (config: RunConfig) => string> = {
  'wireframe': (config) => `You are a Wireframe & Layout Research Agent. Research wireframing patterns and layout best practices for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. Page layout structure and grid systems
2. Wireframe patterns for key screens
3. Responsive design considerations
4. Navigation flow and hierarchy
5. Content placement strategies

Output a comprehensive specification document in Markdown format with clear sections and actionable recommendations.`,

  'components': (config) => `You are a UI Components Library Research Agent. Research component libraries and UI patterns for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. Recommended component libraries (e.g., shadcn/ui, Material UI, Chakra)
2. Custom component requirements
3. Component architecture patterns
4. Accessibility considerations
5. Design token and theming approach

Output a comprehensive specification document in Markdown format.`,

  'style': (config) => `You are a Color & Style Research Agent. Research design systems and visual styling for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. Color palette selection and color theory application
2. Typography system (fonts, scales, hierarchy)
3. Spacing and rhythm systems
4. Visual design principles
5. Brand identity considerations

Output a comprehensive specification document in Markdown format.`,

  'ux': (config) => `You are a UX/UI Research Agent. Research user experience best practices for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. User journey mapping
2. Interaction design patterns
3. Micro-interactions and feedback
4. Accessibility (WCAG compliance)
5. Usability heuristics

Output a comprehensive specification document in Markdown format.`,

  'primary-backend': (config) => `You are a Backend Architecture Research Agent. Research backend architecture patterns for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. API design (REST, GraphQL, tRPC)
2. Server architecture patterns
3. Microservices vs monolith considerations
4. Error handling strategies
5. Performance optimization

Output a comprehensive specification document in Markdown format.`,

  'database': (config) => `You are a Database Research Agent. Research database options and schema patterns for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. Database technology selection (SQL vs NoSQL)
2. Schema design patterns
3. Data modeling best practices
4. Query optimization strategies
5. Data migration considerations

Output a comprehensive specification document in Markdown format.`,

  'auth': (config) => `You are an Authentication Research Agent. Research authentication and authorization patterns for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. Authentication methods (OAuth, JWT, sessions)
2. Authorization patterns (RBAC, ABAC)
3. Security best practices
4. Third-party auth providers
5. Session management

Output a comprehensive specification document in Markdown format.`,

  'tech-stack': (config) => `You are a Tech Stack Research Agent. Research and recommend technology choices for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and provide detailed recommendations for:
1. Frontend framework selection
2. Backend runtime/framework
3. Database technology
4. Deployment platform
5. Development tools and CI/CD

Output a comprehensive specification document in Markdown format with comparison tables.`,

  'planning': (config) => `You are a Project Planning Agent. Create a project timeline and milestones for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Create a detailed project plan including:
1. Phase breakdown (MVP, v1, future)
2. Sprint/milestone planning
3. Resource estimation
4. Risk assessment
5. Dependencies and critical path

Output a comprehensive planning document in Markdown format.`,

  'architecture': (config) => `You are a System Architecture Agent. Design the system architecture for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Design and document:
1. High-level system architecture
2. Component diagrams (described in text)
3. Data flow patterns
4. Integration points
5. Scalability considerations

Output a comprehensive architecture specification in Markdown format.`,

  'best-practices': (config) => `You are an Implementation Best Practices Agent. Research coding standards and patterns for a ${PROJECT_TYPE_LABELS[config.projectType]}.

Project: ${config.projectName}
Description: ${config.projectDescription}

Research and document:
1. Code organization patterns
2. Naming conventions
3. Testing strategies
4. Documentation standards
5. Code review guidelines

Output a comprehensive best practices specification in Markdown format.`,
};

// Get document title for agent
function getDocumentTitle(agentId: string): string {
  const titles: Record<string, string> = {
    'wireframe': 'Wireframe & Layout Specification',
    'components': 'UI Components Specification',
    'style': 'Color & Style Specification',
    'ux': 'UX/UI Specification',
    'primary-backend': 'Backend Architecture Specification',
    'database': 'Database Specification',
    'auth': 'Authentication Specification',
    'tech-stack': 'Technology Stack Specification',
    'planning': 'Project Planning Specification',
    'architecture': 'System Architecture Specification',
    'best-practices': 'Implementation Best Practices',
  };
  return titles[agentId] || 'Specification Document';
}

export async function POST(req: Request) {
  const { config, agentId }: { config: RunConfig; agentId: string } = await req.json();
  
  const agent = AGENT_HIERARCHY.find(a => a.id === agentId);
  if (!agent) {
    return Response.json({ error: 'Agent not found' }, { status: 404 });
  }
  
  const promptGenerator = AGENT_PROMPTS[agentId];
  if (!promptGenerator) {
    return Response.json({ error: 'No prompt configured for this agent' }, { status: 400 });
  }
  
  const systemPrompt = `You are an expert research agent in a hierarchical multi-agent system. Your output will be used as part of a comprehensive project specification. Be thorough, practical, and provide actionable recommendations.

Format your output as a well-structured Markdown document with:
- Clear section headings (## and ###)
- Bullet points for lists
- Code blocks where appropriate
- Tables for comparisons
- A "Sources Consulted" section at the end (list relevant documentation or resources you would reference)

Start your document with an "Executive Summary" section.
Include a confidence assessment (High/Medium/Low) with brief rationale.`;

  const result = streamText({
    model: config.model || 'openai/gpt-4o-mini',
    system: systemPrompt,
    prompt: promptGenerator(config),
    maxOutputTokens: 4000,
  });
  
  // Return streaming response with agent metadata
  return result.toTextStreamResponse({
    headers: {
      'X-Agent-Id': agentId,
      'X-Agent-Name': agent.name,
      'X-Document-Title': getDocumentTitle(agentId),
    },
  });
}
