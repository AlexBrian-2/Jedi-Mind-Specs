# Research Orchestrator

A hierarchical multi-agent desktop application for exhaustive research and specification generation.

## Overview

Research Orchestrator is a desktop application that uses a 20-agent hierarchical system to research and analyze any project type you want to build. The system follows the "Jedi Mind Specs v2.0" architecture:

- **Tier 1**: Master Agent (orchestration only)
- **Tier 2**: 5 Lead Agents (Frontend, Backend, Specs, Review, Validation)
- **Tier 3**: 15 Specialist Agents (researchers, reviewers, validators)

## Features

- Intelligent rate limiting (180 requests/hour soft limit)
- KiloCode Gateway integration for free LLM access
- Real-time agent activity monitoring
- Spec document generation with Markdown output
- Desktop native GUI (PySide6/Qt)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

See [Instructions.md](Instructions.md) for detailed setup and usage guide.

## Project Structure

```
multi_agent_research_app/
├── main.py                    # Entry point
├── requirements.txt          # Dependencies
├── core/                     # Core orchestration
│   ├── rate_limiter.py       # Token bucket rate limiting
│   ├── run_context.py        # Run state management
│   ├── orchestrator.py      # Workflow state machine
│   └── agents/             # Agent implementations
├── tools/                    # Research tools
├── gui/                     # Desktop GUI
└── tests/                   # Unit tests
```

## Documentation

- [Instructions.md](Instructions.md) - Complete setup and usage guide
- `Jedi Mind Specs v2.0 (Input).md` - Original specification input
- `Jedi Mind Specs v2.0 (Agent Tree).md` - Agent hierarchy
- `Jedi Mind Specs v2.0 (Results).md` - Architecture blueprint

## Requirements

- Python 3.10+
- PySide6 6.9+
- See requirements.txt for full list

## License

This project was built from the Jedi Mind Specs v2.0 specification.