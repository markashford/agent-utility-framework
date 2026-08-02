# Agent Utility Framework with Local Tools, MCP Integration, and Streamlit UI

Production-minded educational framework for building Claude-powered agents with local tools, MCP integration, and a Streamlit demo UI.

This repository is intentionally compact, but it is structured like a maintainable real-world project:

- modular tool architecture
- typed model config and history management
- offline unit tests for core logic
- runnable interactive UI
- Dockerized demo deployment

## Why this project

Many agent examples are either too toy-like or too large to understand quickly. This project sits in the middle:

- small enough to learn in one sitting
- clean enough to extend
- practical enough to run as a local demo

## Features

- Claude agent loop with configurable model parameters
- local tools (`think`, file read/write)
- optional MCP tool loading via stdio or SSE
- message history with token tracking and truncation
- Streamlit app for interactive runs
- Docker and Docker Compose support
- fast, API-free unit test suite

## Repository layout

- `agent.py`: Core `Agent` and `ModelConfig`
- `tools/`: Built-in local and server tool wrappers
- `utils/`: MCP connection setup, history, and tool execution utilities
- `tests/`: Offline test suite for core behavior
- `streamlit_app.py`: Interactive demo UI

## Quickstart

### 1) Create environment and install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2) Set API key

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

### 3) Run tests

```bash
python3 -m pytest -q
```

### 4) Run the Streamlit UI

```bash
pip install .[ui]
streamlit run streamlit_app.py
```

The UI imports the installed `agents` package, so use an editable install (`pip install -e .[ui]`) during development.

## Minimal usage example

```python
from agents.agent import Agent
from agents.tools.think import ThinkTool

agent = Agent(
    name="StudioAgent",
    system="You are a practical AI engineering assistant.",
    tools=[ThinkTool()],
)

response = agent.run("Give me a 5-step production readiness checklist.")
print(response)
```

## Docker usage

Build and run with Docker Compose:

```bash
docker compose up --build
```

Then open `http://localhost:8501`.

You can pass your API key via environment variable:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
docker compose up --build
```

## Notes on MCP support

MCP integration is supported but optional. If you want to use MCP servers, install MCP extras:

```bash
pip install .[mcp]
```

Without MCP installed, core agent functionality and tests continue to work.

## Roadmap

- structured logging and request IDs
- async streaming responses
- policy guardrails for tool invocation
- benchmark prompts and evaluation artifacts

## License

MIT. See LICENSE.