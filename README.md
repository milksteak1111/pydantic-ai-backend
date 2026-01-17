# pydantic-ai-backend

[![PyPI version](https://img.shields.io/pypi/v/pydantic-ai-backend.svg)](https://pypi.org/project/pydantic-ai-backend/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage Status](https://coveralls.io/repos/github/vstorm-co/pydantic-ai-backend/badge.svg?branch=main)](https://coveralls.io/github/vstorm-co/pydantic-ai-backend?branch=main)

File storage, sandbox backends, and console toolset for [pydantic-ai](https://github.com/pydantic/pydantic-ai) agents.

> **Looking for a complete agent framework?** Check out [pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents) - a full-featured deep agent framework with planning, subagents, and skills system.

> **Need task planning?** Check out [pydantic-ai-todo](https://github.com/vstorm-co/pydantic-ai-todo) - standalone task planning toolset for any pydantic-ai agent.

## Documentation

**[Full Documentation](https://vstorm-co.github.io/pydantic-ai-backend/)** - Installation, concepts, examples, and API reference.

## Architecture

![Architecture](assets/architecture.png)

## Installation

```bash
# Core library
pip install pydantic-ai-backend

# With console toolset (requires pydantic-ai)
pip install pydantic-ai-backend[console]

# With Docker sandbox support
pip install pydantic-ai-backend[docker]

# Everything
pip install pydantic-ai-backend[console,docker]
```

## Quick Start

### Console Toolset with pydantic-ai

The easiest way to add file operations to your agent:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import LocalBackend, create_console_toolset

@dataclass
class Deps:
    backend: LocalBackend

# Create agent with console tools
agent = Agent(
    "openai:gpt-4o",
    deps_type=Deps,
    toolsets=[create_console_toolset()],
    system_prompt="You are a coding assistant. Use the tools to read, write, and execute code.",
)

# Run agent
backend = LocalBackend(root_dir="./workspace")
result = agent.run_sync(
    "Create a Python script that calculates fibonacci numbers and run it",
    deps=Deps(backend=backend),
)
print(result.output)
```

### Docker Sandbox for Safe Execution

For untrusted code or multi-user applications:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import DockerSandbox, create_console_toolset

@dataclass
class Deps:
    backend: DockerSandbox

# Create isolated sandbox
sandbox = DockerSandbox(runtime="python-datascience")
sandbox.start()

# Create agent
agent = Agent(
    "openai:gpt-4o",
    deps_type=Deps,
    toolsets=[create_console_toolset()],
    system_prompt="You are a data analysis assistant.",
)

result = agent.run_sync(
    "Write a script that generates random data and plots a histogram",
    deps=Deps(backend=sandbox),
)

sandbox.stop()
```

### In-Memory Backend for Testing

Perfect for unit tests and ephemeral sessions:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import StateBackend, create_console_toolset

@dataclass
class Deps:
    backend: StateBackend

# In-memory storage - no files on disk
backend = StateBackend()

agent = Agent(
    "openai:gpt-4o",
    deps_type=Deps,
    toolsets=[create_console_toolset(include_execute=False)],  # No shell in StateBackend
)

result = agent.run_sync(
    "Create a config.json file with database settings",
    deps=Deps(backend=backend),
)

# Access files programmatically
print(backend.files)  # {'/config.json': {...}}
```

### Multi-User Web Application

Session manager for web apps with isolated user environments:

```python
from dataclasses import dataclass
from fastapi import FastAPI
from pydantic_ai import Agent
from pydantic_ai_backends import SessionManager, DockerSandbox, create_console_toolset

app = FastAPI()

# Session manager with persistent storage
manager = SessionManager(
    default_runtime="python-datascience",
    workspace_root="/app/user_workspaces",  # Files persist here
)

@dataclass
class Deps:
    backend: DockerSandbox

agent = Agent(
    "openai:gpt-4o",
    deps_type=Deps,
    toolsets=[create_console_toolset()],
)

@app.post("/run/{user_id}")
async def run_code(user_id: str, prompt: str):
    # Each user gets their own isolated sandbox
    sandbox = await manager.get_or_create(user_id)

    result = await agent.run(prompt, deps=Deps(backend=sandbox))
    return {"output": result.output}

@app.on_event("shutdown")
async def shutdown():
    await manager.shutdown()
```

### Composite Backend for Complex Routing

Route different paths to different backends:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import (
    CompositeBackend,
    LocalBackend,
    StateBackend,
    create_console_toolset,
)

@dataclass
class Deps:
    backend: CompositeBackend

# Different backends for different purposes
backend = CompositeBackend(
    default=StateBackend(),  # Temp files in memory
    routes={
        "/project/": LocalBackend("/home/user/myproject"),
        "/data/": LocalBackend("/shared/datasets", enable_execute=False),
    },
)

agent = Agent(
    "openai:gpt-4o",
    deps_type=Deps,
    toolsets=[create_console_toolset()],
)

result = agent.run_sync(
    "Read the CSV from /data/sales.csv, analyze it, and save results to /project/report.md",
    deps=Deps(backend=backend),
)
```

## Console Toolset Configuration

```python
from pydantic_ai_backends import create_console_toolset

# Default: all tools, execute requires approval
toolset = create_console_toolset()

# Without shell execution
toolset = create_console_toolset(include_execute=False)

# Require approval for write operations
toolset = create_console_toolset(
    require_write_approval=True,
    require_execute_approval=True,
)

# Custom toolset ID
toolset = create_console_toolset(id="file-tools")
```

**Available tools:** `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute`

## Built-in Docker Runtimes

```python
from pydantic_ai_backends import DockerSandbox

# Pre-configured environments
sandbox = DockerSandbox(runtime="python-datascience")
```

| Runtime | Base Image | Packages |
|---------|------------|----------|
| `python-minimal` | python:3.12-slim | (none) |
| `python-datascience` | python:3.12-slim | pandas, numpy, matplotlib, scikit-learn, seaborn |
| `python-web` | python:3.12-slim | fastapi, uvicorn, sqlalchemy, httpx |
| `node-minimal` | node:20-slim | (none) |
| `node-react` | node:20-slim | typescript, vite, react, react-dom |

Custom runtime:

```python
from pydantic_ai_backends import DockerSandbox, RuntimeConfig

runtime = RuntimeConfig(
    name="ml-env",
    base_image="python:3.12-slim",
    packages=["torch", "transformers", "accelerate"],
    env_vars={"PYTHONUNBUFFERED": "1"},
)

sandbox = DockerSandbox(runtime=runtime)
```

## Backend Protocol

All backends implement `BackendProtocol`:

```python
class BackendProtocol(Protocol):
    def ls_info(self, path: str) -> list[FileInfo]: ...
    def read(self, path: str, offset: int = 0, limit: int = 2000) -> str: ...
    def write(self, path: str, content: str | bytes) -> WriteResult: ...
    def edit(self, path: str, old: str, new: str, replace_all: bool = False) -> EditResult: ...
    def glob_info(self, pattern: str, path: str = "/") -> list[FileInfo]: ...
    def grep_raw(self, pattern: str, path: str | None = None, glob: str | None = None) -> list[GrepMatch] | str: ...
```

`LocalBackend` and `DockerSandbox` also provide shell execution:

```python
def execute(self, command: str, timeout: int | None = None) -> ExecuteResponse: ...
```

## Examples

Full working examples in [`examples/`](examples/):

| Example | Description | Backend |
|---------|-------------|---------|
| [**local_cli**](examples/local_cli/) | CLI coding assistant | `LocalBackend` |
| [**web_production**](examples/web_production/) | Multi-user web app with UI | `DockerSandbox` + `SessionManager` |

## Development

```bash
git clone https://github.com/vstorm-co/pydantic-ai-backend.git
cd pydantic-ai-backend
make install
make test
```

## Related Projects

- **[pydantic-ai](https://github.com/pydantic/pydantic-ai)** - Agent framework by Pydantic
- **[pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents)** - Full agent framework (uses this library)
- **[pydantic-ai-todo](https://github.com/vstorm-co/pydantic-ai-todo)** - Task planning toolset

## License

MIT License - see [LICENSE](LICENSE) for details.
