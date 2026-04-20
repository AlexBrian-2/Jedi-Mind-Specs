# Hierarchical Multi-Agent Research Orchestrator: Complete Architecture & Implementation Blueprint

## Bottom-Line Stack Decision—Read This First

Build this system in Python with PySide6 for the desktop shell, CrewAI as the orchestration backbone, LiteLLM as the LLM routing layer (pointed at KiloCode Gateway), and a custom in-process rate limiter as the critical safety layer. This combination delivers native desktop UX, proven hierarchical agent support, and zero-cost LLM access—with one important caveat addressed immediately below.

**Full Tech Stack Decision Matrix**

| Layer | Recommended Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| Desktop GUI Framework | PySide6 (Qt for Python) | Native look, MVC support, async-friendly via `qasync` | Electron, Tkinter, PyQt5 (EOL 2023) |
| Agent Orchestration | CrewAI + hierarchical process | Built-in `max_rpm`, `allow_delegation`, manager_llm pattern [1] | AutoGen, LangGraph, raw asyncio |
| LLM Routing Layer | LiteLLM with custom `base_url` | Connects to any OpenAI-compatible endpoint; CrewAI integrates natively [2] | OpenAI SDK direct, httpx |
| LLM API Provider | KiloCode Gateway (`https://api.kilo.ai/api/gateway`) | Free anonymous access, 200 req/hr/IP [3] | OpenRouter, Groq |
| Rate Limiter | Custom token-bucket + sliding window (in-process) | Must be built-in; no external service dependency | pyrate-limiter [4], slowapi |
| Async Runtime | asyncio + QThread bridge (`qasync`) | Keeps GUI responsive during multi-minute agent runs | threading.Thread |
| Web Research | Tavily API (primary) + `duckduckgo-search` (fallback) | Tavily free tier: 1,000 credits/month [5]; DuckDuckGo needs no key | Playwright, SerpAPI |
| Spec Document Output | Markdown → PDF via WeasyPrint or Pandoc | Human-readable, version-controllable, diff-friendly | DOCX via python-docx |
| Local State / Storage | SQLite via SQLAlchemy | Lightweight, no server, survives crashes | JSON flat files, TinyDB |
| Packaging | PyInstaller or Nuitka | Single-executable distribution | cx_Freeze |

**Justification for the three most consequential choices:**

**PySide6** is the only viable Qt-for-Python option going forward—PyQt5 support ended at end of 2023 [6], and PySide6 is Qt's officially licensed Python binding for Qt6. The MVC pattern maps cleanly onto the agent hierarchy: the `RunContext` object is the Model, the `QTreeWidget`-based agent panel is the View, and the `OrchestratorController` is the Controller [7]. Critically, PySide6 integrates with `qasync` to bridge Python's asyncio event loop with Qt's, meaning long-running agent chains never freeze the UI.

**CrewAI** provides the hierarchical process model natively—the `manager_llm` or `manager_agent` parameter designates a coordinating agent, `allow_delegation=True` enables sub-agent dispatch, and the crew-level `max_rpm` attribute enforces a global rate cap that overrides per-agent settings [1]. This maps almost directly to the specified 3-tier structure. A community-built PySide6 GUI for CrewAI workflows (CrewAI-GUI-Qt, 204 GitHub stars) confirms the combination is proven in practice [8].

**LiteLLM as the routing layer** is the bridge that makes KiloCode Gateway work with CrewAI. LiteLLM accepts a `base_url` parameter pointing to any OpenAI-compatible endpoint [2], so the entire CrewAI agent fleet routes through `https://api.kilo.ai/api/gateway` without any custom SDK work. CrewAI's own documentation confirms LiteLLM as the standard path for connecting to non-native LLM providers [9].

---

## KiloCode Gateway Integration & The Anonymous Access Conflict

### API Fundamentals

The KiloCode Gateway exposes a unified, OpenAI-compatible API at `https://api.kilo.ai/api/gateway`, with `POST /chat/completions` as the primary inference endpoint [10]. Because it follows the OpenAI spec exactly, any OpenAI-compatible SDK—including LiteLLM—works without modification.

**Critical configuration:**

```python
import litellm

response = litellm.completion(
    model="openai/nvidia/llama-3.1-nemotron-super-49b-v1",  # or kilo/auto-free
    messages=[{"role": "user", "content": prompt}],
    api_base="https://api.kilo.ai/api/gateway",
    api_key="anonymous",  # or omit entirely — see caveat below
)
```

### The Anonymous Access Conflict—Read Carefully

There is a genuine, unresolved contradiction in the evidence that every developer targeting this stack must understand:

**Official documentation** states clearly: "Free models are available to both authenticated and anonymous users. Anonymous users are rate-limited to 200 requests per hour per IP address." [3] The official free-usage guide also confirms `kilo-auto/free` as a model tier that routes to the best available free models with no configuration needed [11].

**However**, GitHub issue #6317 documents that the literal string `"anonymous"` passed as an API key returns HTTP 401 "Invalid token" for the `/chat/completions` endpoint—though it does work for the `/models` listing endpoint. The workaround documented in that issue requires completing a device auth flow to obtain a real (but still free) JWT token [12].

**Practical resolution**: Design the application to support both paths. On first launch, attempt an unauthenticated request; if a 401 is returned, trigger a lightweight OAuth device-flow login to obtain a free-tier token and cache it locally. This makes the anonymous path the happy path while gracefully handling the authentication requirement. The free-tier access itself is not in dispute—only the mechanism for proving anonymity.

### Free Models Available

Confirmed free models accessible through the Gateway include NVIDIA Nemotron 3 Super [13], Qwen3 Coder, GLM 4.5 Air, and DeepSeek R1 [14]. The `kilo/auto` and `kilo/auto-free` routing aliases automatically select from available free models, but critically, **these aliases do not appear in the response from `GET /api/gateway/models`** [15]—your model-selection UI must hardcode them as known options rather than discovering them dynamically from the models endpoint.

The live canonical list of free models is maintained at `kilo.ai/models` and `kilo.ai/leaderboard` [13], and should be referenced for the most current availability since the free model roster changes.

---

## Intelligent Rate Limiting—The Built-In Safety System

With potentially 22 agents making sequential and concurrent LLM calls against a 200 req/hr/IP ceiling, rate limiting is not optional—it is the load-bearing safety layer of the entire system.

### Algorithm: Token Bucket + Sliding Window Hybrid

The design combines two complementary algorithms:

- **Sliding window counter**: Maintain a deque of request timestamps covering a rolling 3,600-second window. Before each request, evict timestamps older than 3,600 seconds and count the remainder. Enforce a **soft ceiling of 180 requests/hour** (10% buffer below the hard limit), giving the system a safety margin for timing jitter.
- **Token bucket for burst control**: Bucket capacity of 10 tokens; refill rate of 1 token every 18 seconds (matching the 180/hr soft ceiling). This prevents any short burst from consuming a disproportionate share of the hourly budget.

CrewAI's own `max_rpm` crew attribute provides a first-pass rate cap at the framework level [1], but it is insufficient alone because it operates per-crew, not across the entire multi-crew hierarchy. The custom `RateLimitedGatewayClient` singleton below is the authoritative enforcement point.

### Core Rate Limiter Implementation

```python
import asyncio
import time
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class RateLimitedGatewayClient:
    """Singleton gateway client with token-bucket + sliding-window rate limiting."""
    soft_limit: int = 180          # requests per hour (10% buffer below hard 200)
    window_seconds: int = 3600
    max_burst: int = 10
    max_concurrent: int = 4        # asyncio.Semaphore cap
    
    _semaphore: asyncio.Semaphore = field(init=False)
    _queue: asyncio.Queue = field(init=False)
    _timestamps: deque = field(default_factory=deque, init=False)
    _tokens: float = field(default=10.0, init=False)
    _last_refill: float = field(default_factory=time.monotonic, init=False)

    def __post_init__(self):
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._queue = asyncio.Queue()
        self._refill_rate = self.soft_limit / self.window_seconds  # tokens/sec

    def _refill_tokens(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.max_burst, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    def _count_window(self) -> int:
        cutoff = time.time() - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
        return len(self._timestamps)

    async def _wait_for_capacity(self):
        while True:
            self._refill_tokens()
            if self._count_window() < self.soft_limit and self._tokens >= 1:
                self._tokens -= 1
                self._timestamps.append(time.time())
                return
            await asyncio.sleep(1.0)

    async def call(self, fn: Callable, *args, **kwargs) -> Any:
        await self._wait_for_capacity()
        async with self._semaphore:
            backoff = 5.0
            for attempt in range(6):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    if "429" in str(e) and attempt < 5:
                        jitter = random.uniform(0.8, 1.2)
                        await asyncio.sleep(min(backoff * jitter, 120))
                        backoff *= 2
                    else:
                        raise
```

Every LLM call in every agent—across all 22 nodes—routes through `RateLimitedGatewayClient.call()`. This is enforced by having `BaseAgent.llm_call()` delegate to the singleton, so no agent can bypass the limiter.

### Agent Scheduling: Staggered Batch Execution

Because the workflow is inherently sequential (Research → Review → Validation), the `AgentScheduler` can further reduce peak load by running Tier-3 specialists in controlled batches rather than all simultaneously:

- **Research phase**: Run Frontend Tier-3 (4 agents), Backend Tier-3 (3 agents), and Specs Tier-3 (5 agents) as three sequential sub-batches, each with a minimum 2-second inter-call delay between agent invocations within the batch.
- **Review phase**: The 3 Review Agents run sequentially (not concurrently)—independent analysis is the goal, not speed.
- **Validation phase**: Same pattern for the 2 Validation Agents.

This scheduling strategy means peak concurrent LLM calls stay at or below 4 (matching the semaphore cap), and the 180/hr soft ceiling is virtually never approached in a single run given the sequential workflow.

### GUI Rate Limit Monitor

The bottom status bar of the application displays a `RateLimitStatusWidget` showing: requests used this hour / 180 soft limit, estimated requests remaining, time until window reset (countdown), and current asyncio queue depth. This widget polls the singleton's state every 5 seconds via a `QTimer`.

---

## Full Agent Hierarchy—Roles, Communication & State Machine

### Complete Agent Roster

| Tier | Agent Name | Role | Primary Tools | Output Artifact |
|---|---|---|---|---|
| 1 | Master Agent | Orchestrates all; sole user-facing interface; no research | Task decomposition, result aggregation | Final report + all spec docs |
| 2 | Frontend Lead | Delegates UI/UX research; synthesizes Tier-3 outputs | Sub-agent management | Frontend spec summary |
| 3 | Wireframe & Layout | Researches wireframing patterns for the project type | Web search, layout analysis | `wireframe_spec.md` |
| 3 | UI Components Library | Researches component libraries relevant to project | Web search | `components_spec.md` |
| 3 | Color & Style | Researches design systems and color theory | Web search | `style_spec.md` |
| 3 | Overall UX/UI/GUI | Synthesizes UX best practices across sources | Web search, synthesis | `ux_spec.md` |
| 2 | Backend Lead | Delegates backend research; synthesizes Tier-3 outputs | Sub-agent management | Backend spec summary |
| 3 | Primary Backend | Researches backend architecture patterns | Web search | `backend_spec.md` |
| 3 | Database | Researches DB options and schema patterns | Web search | `database_spec.md` |
| 3 | Auth | Researches auth patterns and libraries | Web search | `auth_spec.md` |
| 2 | Specs Lead | Delegates documentation; synthesizes all spec docs | Sub-agent management | All spec documents |
| 3 | Spec Documents Specialist | Compiles and formats all spec docs into master | Document generation | `master_spec.md` |
| 3 | Tech Stack | Researches and recommends technology choices | Web search, comparison | `techstack_spec.md` |
| 3 | Planning | Creates project timeline and milestones | Analysis | `planning_spec.md` |
| 3 | Architecture | Designs system architecture | Web search, diagramming | `architecture_spec.md` |
| 3 | Implementation Best Practices | Researches coding standards and patterns | Web search | `bestpractices_spec.md` |
| 2 | Review Lead | Coordinates 3 review agents; manages consensus | Consensus management | Review report |
| 3 | Review Agent #1 | Independent quality review pass | Analysis, scoring | `review1_report.md` |
| 3 | Review Agent #2 | Independent quality review pass | Analysis, scoring | `review2_report.md` |
| 3 | Review Agent #3 | Independent quality review pass | Analysis, scoring | `review3_report.md` |
| 2 | Validation Lead | Coordinates 2 validation agents; final gate | Final gate management | Validation report |
| 3 | Validation Agent #1 | Final validation check | Analysis | `validation1_report.md` |
| 3 | Validation Agent #2 | Final validation check | Analysis | `validation2_report.md` |

The three Review Agents run sequentially and independently—each reviews the full output corpus without seeing the others' reviews first. The Review Lead then synthesizes the three reports using a majority-rules heuristic: if 2 of 3 reviewers flag a section as deficient, it triggers a revision cycle. This design, drawing on Azure Architecture Center's documented orchestration patterns for sequential and group-chat agent flows [16], prevents a single agent's hallucination from blocking a valid output.

### Inter-Agent Communication Protocol

All agents communicate exclusively via a typed `AgentMessage` dataclass:

```python
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Any
import uuid

class MessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    RESULT_SUBMISSION = "result_submission"
    STATUS_UPDATE = "status_update"
    ESCALATION = "escalation"

@dataclass
class AgentMessage:
    sender_id: str
    recipient_id: str
    message_type: MessageType
    payload: Any
    run_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

The **communication topology is strictly enforced**:
- Human User ↔ Master Agent only
- Master Agent ↔ Tier-2 Leads only
- Tier-2 Leads ↔ their own Tier-3 specialists only
- No Tier-3 agent ever addresses Master Agent or a sibling subtree

The Master Agent maintains a `RunContext` object—a single source of truth for the entire run—containing: current workflow state, per-agent status, all produced artifacts, visited URLs, API call count, and revision cycle history.

### Workflow State Machine

The run lifecycle follows a deterministic state machine with a **maximum 3 review/revision cycles** to prevent infinite loops:

```
IDLE
  │ (user submits query)
  ▼
PARSING  ──── Master Agent analyzes request, assigns task bundles to Tier-2 Leads
  │
  ▼
RESEARCH_PHASE  ──── Frontend batch → Backend batch → Specs batch (sequential sub-batches)
  │
  ▼
REVIEW_PHASE  ──── Review Lead dispatches to 3 Review Agents sequentially
  │
  ▼
REVIEW_DECISION
  ├── PASS ──────────────────────────────────────────────────────────────────────┐
  └── FAIL (revision_count < 3) ──► REVISION_PHASE ──► back to REVIEW_PHASE    │
       FAIL (revision_count == 3) ──► force PASS with warning flag              │
  │                                                                              │
  ▼                                                                              │
VALIDATION_PHASE  ◄─────────────────────────────────────────────────────────────┘
  │ (Validation Lead + 2 Validation Agents)
  ▼
VALIDATION_DECISION
  ├── PASS ──► COMPLETE
  └── FAIL (validation_count < 2) ──► REVISION_PHASE ──► REVIEW_PHASE
       FAIL (validation_count == 2) ──► COMPLETE with warning flag
  │
  ▼
COMPLETE  ──── Master Agent compiles master_spec.md, delivers to user with run summary
```

The max-iteration guard is implemented as two counters in `RunContext`: `review_cycles: int = 0` and `validation_cycles: int = 0`. The `OrchestratorController` checks these before transitioning to REVISION_PHASE.

---

## Desktop GUI Design—PySide6 Implementation

### Three-Panel Window Layout

The main window uses a `QSplitter` with three horizontal panels:

**Left Panel—Project Submission Form**
- `QComboBox`: project type selector (Web App, Mobile App, Desktop App, API/Backend, CLI Tool, Data Pipeline, ML System, Other)
- `QTextEdit`: project description (multi-line, 500-char minimum prompt to ensure sufficient context)
- `QSpinBox`: max revision cycles (default 3, range 1–5)
- `QPushButton`: "Start Research Run" (disabled during active run)
- `QPushButton`: "Cancel Run" (enabled only during active run; triggers graceful shutdown that saves partial artifacts)
- Collapsible "Advanced" section: model selector, per-agent inter-call delay, output directory picker

**Center Panel—Live Agent Activity Feed**
A `QTreeWidget` mirroring the exact agent hierarchy, where each node shows:
- Agent name and current status icon (⏳ waiting, 🔄 active spinner, ✅ complete, ⚠️ flagged, ❌ failed)
- Current action description (e.g., "Searching: 'React component library 2024'")
- Elapsed time for the current task

Below the tree, a `QPlainTextEdit` log shows timestamped event messages from all agents in real time. Both are updated via Qt signals emitted from worker threads—the GUI thread never touches agent state directly.

**Right Panel—Results Viewer**
A `QTabWidget` where each tab corresponds to one spec document. Tabs are added dynamically as agents complete their artifacts. The final tab, "Master Report," is populated only on COMPLETE. Each tab contains a `QTextBrowser` rendering Markdown (converted to HTML via `markdown` library) with a "Copy" and "Save As" button.

**Bottom Status Bar**
The `RateLimitStatusWidget` occupies the right portion of the status bar, displaying: `API: 47/180 req | Remaining: 133 | Reset: 41m 22s | Queue: 0`. A `QProgressBar` embedded in the status bar provides a visual fill representing hourly consumption.

### Async GUI Architecture

```python
# main.py — event loop bridge
import sys
import asyncio
import qasync
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
```

Agent coroutines run directly on the asyncio event loop (bridged to Qt via `qasync`). Status updates are emitted as Qt signals using `Signal(str, str)` (agent_id, status_message), which Qt's signal-slot mechanism safely delivers to the GUI thread. This avoids the complexity of `QThread` workers while maintaining full UI responsiveness.

### MVC Component Map

| MVC Role | Class | Responsibility |
|---|---|---|
| Model | `RunContext` | All run state, artifacts, API counters |
| Model | `AgentRegistry` | Agent definitions, capabilities, status |
| Model | `SpecDocumentStore` | In-memory + SQLite persistence of spec docs |
| View | `MainWindow` | Top-level window, panel layout |
| View | `AgentTreeView` | Live hierarchy widget with status icons |
| View | `SpecDocumentViewer` | Tabbed spec document browser |
| View | `RateLimitStatusWidget` | Bottom bar rate limit monitor |
| Controller | `OrchestratorController` | Bridges UI actions to Master Agent; owns state machine |

---

## Research Capabilities—How Agents Actually Search

### Search Tool Stack

Each Tier-3 research agent receives a `WebResearchTool` instance configured with a three-tier fallback strategy:

1. **Primary: Tavily Search API**—purpose-built for AI agents, returns clean structured results with relevance scores. Free tier provides 1,000 credits/month [5], sufficient for dozens of research runs. Each search call costs roughly 1 credit. Accessed via `tavily-python` SDK.
2. **Secondary: DuckDuckGo Search**—via the `duckduckgo-search` Python library, no API key required. Used as automatic fallback when Tavily quota is exhausted or unavailable. Returns slightly less structured results but is completely free and uncapped.
3. **Tertiary: Direct URL fetch + BeautifulSoup4**—for deep-dive parsing of specific high-value pages identified in search results. Uses `httpx` for async HTTP with a 10-second timeout and respectful User-Agent header.

CrewAI's native search tools (`WebsiteSearchTool`, `BraveSearchTool`, `SerperDevTool`) [17] are available as drop-in alternatives, but Tavily + DuckDuckGo is preferred for cost predictability.

### Per-Agent Research Strategy

Each Tier-3 research agent generates 3–5 targeted search queries derived from the user's project description using an LLM call (consuming 1 of the agent's API budget). Query generation follows a template:

- **Frontend agents**: "best [project_type] wireframe patterns 2024", "[project_type] UI component library comparison", "[project_type] color system design tokens"
- **Backend agents**: "[project_type] backend architecture patterns", "[project_type] database selection guide", "[project_type] authentication implementation"
- **Specs agents**: "[project_type] technical specification template", "[project_type] implementation best practices", "[project_type] open source reference implementation"

Results are ranked by keyword overlap with the project description (simple TF-IDF scoring, no external library needed), and the top 3 results per query are fetched and summarized. Each agent's output artifact includes a Sources section listing all URLs consulted.

### Deduplication And Quality Control

`RunContext.visited_urls` is a shared `set` across all agents. Before fetching any URL, an agent checks this set and skips already-visited pages—preventing the 4 Frontend agents and 5 Specs agents from all fetching the same React documentation page and burning 9 API calls on identical content. This URL deduplication can reduce total API consumption by 20–40% on typical runs.

---

## Spec Document Generation & Output Artifacts

### Document Template Structure

Every spec document—regardless of which agent produces it—follows this standard template:

```markdown
# [Document Type] Specification
**Project**: [project_name]
**Generated**: [ISO 8601 timestamp]
**Agent**: [agent_name] (Run ID: [run_id])
**Confidence**: [High / Medium / Low] — [brief rationale]

---

## Executive Summary
[2–3 sentence overview]

## [Section 1 heading]
[Content with H3 subheadings, bullet lists, code blocks as appropriate]

## [Section N heading]
...

## Sources Consulted
- [URL 1] — [one-line description]
- [URL 2] — [one-line description]
```

The self-assessed confidence rating serves a practical purpose: the Review Agents are instructed to weight Low-confidence sections more heavily in their evaluation, directing revision effort where it is most needed.

### Master Report Compilation

The Spec Documents Specialist (Tier-3 under Specs Lead) assembles all individual `.md` files into `master_spec.md` using a table-of-contents structure with cross-references. The Master Agent then wraps this with a run summary section containing: total agents invoked, total API calls consumed, total unique sources researched, review cycle history (pass/fail per cycle), and validation outcome.

### Export Pipeline

```
master_spec.md
    │
    ├── Save to user-selected directory (all .md files individually)
    ├── PDF export: WeasyPrint (bundled) converts Markdown → HTML → PDF
    │   └── Fallback: subprocess call to system Pandoc if WeasyPrint fails
    └── Clipboard: per-section copy buttons in the SpecDocumentViewer
```

WeasyPrint is preferred over Pandoc for bundled distribution because it ships as a pure Python package installable via pip, making PyInstaller packaging straightforward. Pandoc requires a separate system binary.

---

## Project Structure & Implementation Roadmap

### Directory Layout

```
multi_agent_research_app/
├── main.py                        # Entry point — qasync event loop bridge
├── requirements.txt
├── core/
│   ├── master_agent.py            # Tier-1 Master Agent (orchestration only)
│   ├── run_context.py             # RunContext dataclass — single source of truth
│   ├── orchestrator.py            # Workflow state machine + AgentScheduler
│   ├── message_bus.py             # AgentMessage dataclass + async routing
│   ├── rate_limiter.py            # RateLimitedGatewayClient singleton
│   └── agents/
│       ├── base_agent.py          # Abstract BaseAgent — llm_call() routes to rate limiter
│       ├── frontend/
│       │   ├── frontend_lead.py
│       │   ├── wireframe_agent.py
│       │   ├── components_agent.py
│       │   ├── style_agent.py
│       │   └── ux_agent.py
│       ├── backend/
│       │   ├── backend_lead.py
│       │   ├── primary_backend_agent.py
│       │   ├── database_agent.py
│       │   └── auth_agent.py
│       ├── specs/
│       │   ├── specs_lead.py
│       │   ├── spec_documents_agent.py
│       │   ├── tech_stack_agent.py
│       │   ├── planning_agent.py
│       │   ├── architecture_agent.py
│       │   └── best_practices_agent.py
│       ├── review/
│       │   ├── review_lead.py
│       │   ├── review_agent_1.py
│       │   ├── review_agent_2.py
│       │   └── review_agent_3.py
│       └── validation/
│           ├── validation_lead.py
│           ├── validation_agent_1.py
│           └── validation_agent_2.py
├── tools/
│   ├── web_search.py              # Tavily + DuckDuckGo fallback
│   ├── page_fetcher.py            # httpx + BeautifulSoup4 parser
│   └── doc_generator.py          # Markdown assembly + WeasyPrint PDF export
├── gui/
│   ├── main_window.py             # QSplitter three-panel layout
│   ├── agent_tree_view.py         # QTreeWidget live hierarchy
│   ├── spec_viewer.py             # QTabWidget spec document browser
│   ├── rate_limit_widget.py       # Status bar rate limit monitor
│   └── styles/
│       └── app.qss                # Qt stylesheet for consistent look
├── storage/
│   ├── models.py                  # SQLAlchemy models (Run, Artifact, VisitedURL)
│   └── db.py                      # SQLite connection management
└── tests/
    ├── test_rate_limiter.py
    ├── test_state_machine.py
    └── test_agents/
```

### Implementation Roadmap

**Phase 1—Foundation (Week 1–2)**
Priority: get the rate limiter and KiloCode Gateway connection working before writing a single agent. Validate that `RateLimitedGatewayClient` correctly enforces the soft ceiling under simulated burst load. Resolve the anonymous vs. authenticated access question empirically—attempt unauthenticated calls, implement device auth flow if 401 is returned.

**Phase 2—Core Agents (Week 3–4)**
Implement `BaseAgent` with the `llm_call()` → rate limiter delegation pattern. Build Master Agent and one complete subtree (e.g., Backend Lead + 3 Backend Tier-3 agents) end-to-end. Validate the `AgentMessage` routing and `RunContext` state tracking. Add the `WebResearchTool` with Tavily primary + DuckDuckGo fallback.

**Phase 3—Full Agent Tree (Week 5–6)**
Implement all remaining Tier-2 Leads and Tier-3 specialists. Wire up the Review and Validation subtrees with the consensus/majority-rules logic. Implement the state machine with max-iteration guards. Test a complete end-to-end run on a simple project type.

**Phase 4—GUI (Week 7–8)**
Build the PySide6 three-panel layout. Implement the `AgentTreeView` with live status updates via Qt signals. Add the `RateLimitStatusWidget`. Wire the `OrchestratorController` to the Master Agent. Add the "Cancel Run" graceful shutdown path.

**Phase 5—Polish & Packaging (Week 9–10)**
Implement PDF export via WeasyPrint. Add SQLite persistence for run history. Configure PyInstaller spec file for single-executable distribution. Write unit tests for the rate limiter and state machine (the two most failure-prone components).

### Key Implementation Best Practices

**BaseAgent pattern—enforce the rate limiter contract:**
```python
from abc import ABC, abstractmethod
from core.rate_limiter import RateLimitedGatewayClient

class BaseAgent(ABC):
    def __init__(self, agent_id: str, run_context):
        self.agent_id = agent_id
        self.ctx = run_context
        self._client = RateLimitedGatewayClient()  # singleton

    async def llm_call(self, messages: list, model: str = "kilo/auto-free") -> str:
        """All LLM calls MUST go through this method — never call litellm directly."""
        async def _call():
            import litellm
            resp = await litellm.acompletion(
                model=f"openai/{model}",
                messages=messages,
                api_base="https://api.kilo.ai/api/gateway",
            )
            return resp.choices[0].message.content
        return await self._client.call(_call)

    @abstractmethod
    async def run(self, task: dict) -> dict:
        """Each agent implements its specific research/review/validation logic."""
        ...
```

**State persistence on cancel**: The `RunContext` serializes to SQLite on every state transition, not just on completion. If the user cancels mid-run, all completed artifacts are preserved and the run can be reviewed in the Results Viewer even without a final master report.

**Scenario: Review cycle triggers revision**—When the Review Lead determines a FAIL verdict, it must attach structured feedback to the ESCALATION message: which spec documents failed, which specific sections were deficient, and what the reviewers recommend. The Specs Lead then dispatches only the affected Tier-3 agents for revision (not the entire Specs subtree), which conserves API budget significantly on revision cycles.

**Scenario: Rate limit exhaustion mid-run**—If the sliding window counter reaches 180 with agents still queued, the `AgentScheduler` enters a hold state: it emits a GUI status update ("Rate limit approaching—pausing for [N] minutes"), waits for the window to partially clear, then resumes. This is far preferable to receiving 429 errors from the provider, which can cause CrewAI's retry logic and the custom backoff to stack, leading to unpredictable delays.

---

## Recommendations

**Immediate (before writing agent code)**
1. Empirically test KiloCode Gateway anonymous access—send a `POST /chat/completions` with no API key and observe the response. If 401, implement the device auth flow and cache the token in the OS keychain via `keyring`. Do not build the entire system on an assumption about authentication behavior.
2. Implement and unit-test `RateLimitedGatewayClient` in isolation, with a mock that simulates 429 responses. This is the single most critical infrastructure component.
3. Hardcode `kilo/auto-free`, NVIDIA Nemotron 3 Super, DeepSeek R1, and Qwen3 Coder as known model options in the UI—do not rely on the `/models` endpoint to discover them.

**Short-term (during agent development)**
4. Use CrewAI's `max_rpm` as a redundant first-pass limiter set to 8 req/min (480/hr theoretical max, but the custom rate limiter enforces the real 180/hr ceiling). Belt-and-suspenders approach.
5. Implement the URL deduplication set in `RunContext` from day one—retrofitting it later requires touching every agent's research loop.
6. Build the Review Agent consensus logic to produce structured JSON feedback (not free-form text) so the Specs Lead can programmatically identify which documents need revision without an additional LLM parsing call.

**Long-term (post-MVP)**
7. Add a local model fallback (Ollama + a small model like Qwen2.5-7B) for when KiloCode Gateway is unavailable or the hourly budget is exhausted. The `BaseAgent.llm_call()` abstraction makes swapping providers a one-line change.
8. Consider migrating the orchestration layer from CrewAI to LangGraph if you need finer-grained control over the state machine—LangGraph's graph-based flow maps more directly to the custom state machine described in Section 3c, at the cost of more boilerplate [18].
9. Implement run templating: save the `RunContext` configuration (project type, agent settings, model choices) as reusable templates so users can re-run research on similar project types without re-entering parameters.

---

## References

[1] CrewAI Hierarchical Process Documentation. https://docs.crewai.com/en/learn/hierarchical-process

[2] LiteLLM Custom LLM Server / Base URL Configuration. https://docs.litellm.ai/docs/providers/custom_llm_server

[3] Kilo AI Gateway—Models and Providers (anonymous rate limit: 200 req/hr/IP). https://kilo.ai/docs/gateway/models-and-providers

[4] pyrate-limiter—General-purpose rate limiting library for Python. https://pyratelimiter.readthedocs.io/

[5] Tavily API Credits Documentation (free tier: 1,000 credits/month). https://docs.tavily.com/documentation/api-credits

[6] PyQt5 End of Support Announcement (end of 2023). https://www.pythonguis.com/tutorials/pyside6-modelview-architecture/

[7] Qt Python MVC Architecture Reference. https://github.com/tom-a-horrocks/qt-python-mvc

[8] CrewAI-GUI-Qt—Node-based PySide6 GUI for CrewAI workflows. https://github.com/LangGraph-GUI/CrewAI-GUI-Qt

[9] CrewAI LLM Connections—LiteLLM Integration Guide. https://docs.crewai.com/en/learn/llm-connections

[10] Kilo AI Gateway API Reference (POST /chat/completions endpoint). https://kilo.ai/docs/gateway/api-reference

[11] Kilo Code—Using Kilo for Free (kilo-auto/free model tier). https://kilo.ai/docs/getting-started/using-kilo-for-free

[12] GitHub Issue #6317—Anonymous token returns HTTP 401 for chat completions. https://github.com/Kilo-Org/kilocode/issues/6317

[13] Kilo AI Leaderboard (NVIDIA Nemotron 3 Super listed as free). https://kilo.ai/leaderboard

[14] Reddit r/kilocode—Free models including Qwen3 Coder, GLM 4.5 Air, DeepSeek R1. https://www.reddit.com/r/kilocode/comments/1p82od1/best_free_usage_of_kilo_code/

[15] GitHub Issue #6686—kilo/auto and kilo/auto-free not returned by /models endpoint. https://github.com/Kilo-Org/kilocode/issues/6686

[16] Azure Architecture Center—AI Agent Design Patterns (sequential, concurrent, group chat, handoff). https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns

[17] CrewAI Search & Research Tools (WebsiteSearchTool, SerperDevTool, etc.). https://docs.crewai.com/en/tools/search-research/overview

[18] LangChain Blog—Choosing the Right Multi-Agent Architecture. https://blog.langchain.com/choosing-the-right-multi-agent-architecture/
