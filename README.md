# pydantic-ai-backend

> **Looking for a complete agent framework?** Check out [pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents) - a full-featured deep agent framework with planning, subagents, and skills system built on pydantic-ai.

> **Need task planning?** Check out [pydantic-ai-todo](https://github.com/vstorm-co/pydantic-ai-todo) - standalone task planning toolset that works with any pydantic-ai agent.

> **Want a full-stack template?** Check out [fastapi-fullstack](https://github.com/vstorm-co/full-stack-fastapi-nextjs-llm-template) - production-ready AI/LLM application template with FastAPI, Next.js, and pydantic-deep integration.

[![PyPI version](https://img.shields.io/pypi/v/pydantic-ai-backend.svg)](https://pypi.org/project/pydantic-ai-backend/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/vstorm-co/pydantic-ai-backend)

File storage and sandbox backends for AI agents. Works seamlessly with [pydantic-ai](https://github.com/pydantic/pydantic-ai).

**This library was extracted from [pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents)** to provide standalone, reusable backends for any pydantic-ai agent without requiring the full framework.

## Features

- **BackendProtocol** - Unified interface for file operations (read, write, edit, glob, grep)
- **StateBackend** - In-memory storage (perfect for testing and ephemeral sessions)
- **FilesystemBackend** - Real filesystem with path sandboxing for security
- **CompositeBackend** - Route operations to different backends by path prefix
- **DockerSandbox** - Isolated Docker containers with command execution
- **SessionManager** - Multi-user session management for Docker sandboxes
- **RuntimeConfig** - Pre-configured Docker environments with packages

## Installation

```bash
pip install pydantic-ai-backend
```

With Docker sandbox support:

```bash
pip install pydantic-ai-backend[docker]
```

## Usage with pydantic-ai

### Basic File Operations Tool

```python
from pydantic_ai import Agent
from pydantic_ai_backends import StateBackend

# Create a backend for file storage
backend = StateBackend()

# Define your agent with file operation tools
agent = Agent("openai:gpt-4o")

@agent.tool
def read_file(ctx, path: str) -> str:
    """Read a file and return its contents."""
    return backend.read(path)

@agent.tool
def write_file(ctx, path: str, content: str) -> str:
    """Write content to a file."""
    result = backend.write(path, content)
    if result.error:
        return f"Error: {result.error}"
    return f"File written to {result.path}"

@agent.tool
def search_files(ctx, pattern: str) -> str:
    """Search for files matching a glob pattern."""
    files = backend.glob_info(pattern)
    return "\n".join(f["path"] for f in files)

# Pre-populate some files
backend.write("/src/app.py", "def main():\n    print('Hello')")
backend.write("/src/utils.py", "def helper(): pass")

# Run the agent
result = agent.run_sync("List all Python files and read app.py")
print(result.output)
```

### Docker Sandbox for Code Execution

```python
from pydantic_ai import Agent
from pydantic_ai_backends import DockerSandbox

agent = Agent("openai:gpt-4o")

# Create sandbox (starts Docker container)
sandbox = DockerSandbox(image="python:3.12-slim")

@agent.tool
def execute_python(ctx, code: str) -> str:
    """Execute Python code in a sandboxed environment."""
    # Write code to file
    sandbox.write("/workspace/script.py", code)
    # Execute and return output
    result = sandbox.execute("python /workspace/script.py", timeout=30)
    if result.exit_code != 0:
        return f"Error (exit {result.exit_code}): {result.output}"
    return result.output

try:
    result = agent.run_sync("Calculate the first 10 Fibonacci numbers")
    print(result.output)
finally:
    sandbox.stop()
```

### Pre-configured Runtime Environments

```python
from pydantic_ai import Agent
from pydantic_ai_backends import DockerSandbox, RuntimeConfig

# Custom runtime with data science packages
runtime = RuntimeConfig(
    name="datascience",
    base_image="python:3.12-slim",
    packages=["pandas", "numpy", "matplotlib", "scikit-learn"],
)

sandbox = DockerSandbox(runtime=runtime)

# Or use a built-in runtime
sandbox = DockerSandbox(runtime="python-datascience")

# Available built-in runtimes:
# - python-minimal: Clean Python 3.12
# - python-datascience: pandas, numpy, matplotlib, scikit-learn, seaborn
# - python-web: FastAPI, SQLAlchemy, httpx
# - node-minimal: Clean Node.js 20
# - node-react: TypeScript, Vite, React
```

### Multi-User Sessions with Session Manager

```python
from pydantic_ai import Agent
from pydantic_ai_backends import SessionManager

# Create session manager for multi-user scenarios
manager = SessionManager(
    default_runtime="python-datascience",
    default_idle_timeout=3600,  # 1 hour
)

async def handle_user_request(user_id: str, code: str):
    # Get or create sandbox for this user
    sandbox = await manager.get_or_create(user_id)

    # Execute user's code
    sandbox.write("/workspace/script.py", code)
    result = sandbox.execute("python /workspace/script.py")

    return result.output

# Cleanup idle sessions periodically
async def cleanup_task():
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        cleaned = await manager.cleanup_idle()
        print(f"Cleaned up {cleaned} idle sessions")

# Shutdown all sessions on app exit
async def shutdown():
    await manager.shutdown()
```

### Persistent Storage with Volumes

By default, files in DockerSandbox are ephemeral - they're lost when the container stops. Use volumes to persist files:

#### Manual Volume Mapping (DockerSandbox)

```python
from pydantic_ai_backends import DockerSandbox

# Mount a host directory to persist files
sandbox = DockerSandbox(
    image="python:3.12-slim",
    volumes={"/local/workspace": "/workspace"}  # host:container
)

# Files saved to /workspace in container persist on host
sandbox.write("/workspace/output.csv", "data...")
sandbox.stop()  # File remains at /local/workspace/output.csv
```

#### Automatic Per-Session Storage (SessionManager)

```python
from pydantic_ai_backends import SessionManager

# Automatically create persistent storage for each session
manager = SessionManager(
    workspace_root="/app/sessions",  # Root directory for all sessions
    default_runtime="python-datascience",
)

# Creates /app/sessions/{session_id}/workspace automatically
sandbox = await manager.get_or_create("user-123")

# Files persist even after container stops or app restarts
sandbox.write("/workspace/results.csv", "analysis results...")

# Later: user returns, same files are available
sandbox = await manager.get_or_create("user-123")  # Files still there!
```

### Composite Backend for Complex Routing

```python
from pydantic_ai_backends import CompositeBackend, StateBackend, FilesystemBackend

# Route different paths to different backends
backend = CompositeBackend(
    default=StateBackend(),  # In-memory for temp files
    routes={
        "/project/": FilesystemBackend("/home/user/myproject"),
        "/data/": FilesystemBackend("/shared/datasets"),
    },
)

# Routes to FilesystemBackend at /home/user/myproject
backend.write("/project/src/main.py", "print('hello')")

# Routes to FilesystemBackend at /shared/datasets
data = backend.read("/data/sales.csv")

# Routes to StateBackend (in-memory)
backend.write("/temp/scratch.txt", "temporary data")
```

## Backend Protocol

All backends implement `BackendProtocol`:

```python
from typing import Protocol

class BackendProtocol(Protocol):
    def ls_info(self, path: str) -> list[FileInfo]:
        """List directory contents."""
        ...

    def read(self, path: str, offset: int = 0, limit: int = 2000) -> str:
        """Read file with line numbers (offset/limit in lines)."""
        ...

    def write(self, path: str, content: str | bytes) -> WriteResult:
        """Write content to file."""
        ...

    def edit(self, path: str, old: str, new: str, replace_all: bool = False) -> EditResult:
        """Replace text in file."""
        ...

    def glob_info(self, pattern: str, path: str = "/") -> list[FileInfo]:
        """Find files matching glob pattern."""
        ...

    def grep_raw(self, pattern: str, path: str | None = None, glob: str | None = None) -> list[GrepMatch] | str:
        """Search file contents with regex."""
        ...
```

`SandboxProtocol` extends this with command execution:

```python
class SandboxProtocol(BackendProtocol, Protocol):
    def execute(self, command: str, timeout: int | None = None) -> ExecuteResponse:
        """Execute shell command."""
        ...

    @property
    def id(self) -> str:
        """Unique sandbox identifier."""
        ...
```

## Quick Reference

### In-Memory Backend (Testing)

```python
from pydantic_ai_backends import StateBackend

backend = StateBackend()
backend.write("/app.py", "print('hello')")
content = backend.read("/app.py")  # Returns with line numbers
matches = backend.grep_raw("print")  # Search content
```

### Filesystem Backend

```python
from pydantic_ai_backends import FilesystemBackend

backend = FilesystemBackend("/path/to/workspace")
backend.write("/data/file.txt", "content")  # Sandboxed to workspace
files = backend.glob_info("**/*.py")
```

### Docker Sandbox

```python
from pydantic_ai_backends import DockerSandbox

sandbox = DockerSandbox(image="python:3.12-slim")
sandbox.write("/workspace/script.py", "print(1+1)")
result = sandbox.execute("python /workspace/script.py")
print(result.output)  # "2"
sandbox.stop()
```

## Development

```bash
# Clone and install
git clone https://github.com/vstorm-co/pydantic-ai-backend.git
cd pydantic-ai-backend
make install

# Run tests
make test

# Run all checks
make all
```

## Related Projects

- **[pydantic-ai](https://github.com/pydantic/pydantic-ai)** - The foundation: Agent framework by Pydantic
- **[pydantic-deep](https://github.com/vstorm-co/pydantic-deepagents)** - Full agent framework (uses this library)
- **[pydantic-ai-todo](https://github.com/vstorm-co/pydantic-ai-todo)** - Task planning toolset
- **[fastapi-fullstack](https://github.com/vstorm-co/full-stack-fastapi-nextjs-llm-template)** - Full-stack AI app template

## License

MIT License - see [LICENSE](LICENSE) for details.
