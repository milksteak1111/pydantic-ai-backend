# Backends

Backends provide file storage for your pydantic-ai agents. All backends implement `BackendProtocol`, so you can swap them without changing your agent code.

## Quick Comparison

| Backend | Persistence | Execution | Best For |
|---------|-------------|-----------|----------|
| `LocalBackend` | Persistent | Yes | CLI tools, local development |
| `StateBackend` | Ephemeral | No | Unit testing, mocking |
| `DockerSandbox` | Ephemeral* | Yes | Safe execution, multi-user |
| `CompositeBackend` | Mixed | Depends | Route by path prefix |

## LocalBackend

Local filesystem with optional shell execution. Use for CLI tools and local development.

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import LocalBackend, create_console_toolset

@dataclass
class Deps:
    backend: LocalBackend

# Backend for local development
backend = LocalBackend(root_dir="./workspace")

# Create agent with file tools
toolset = create_console_toolset()
agent = Agent("openai:gpt-4o", deps_type=Deps).with_toolset(toolset)

# Agent can now work with local files
result = agent.run_sync(
    "Create a todo.py CLI app and test it",
    deps=Deps(backend=backend),
)
```

### Security Options

```python
# Restrict to specific directories
backend = LocalBackend(
    allowed_directories=["/home/user/project", "/home/user/data"],
    enable_execute=True,
)

# Read-only mode (no shell execution)
backend = LocalBackend(
    root_dir="/workspace",
    enable_execute=False,
)

# Corresponding toolset without execute
toolset = create_console_toolset(include_execute=False)
```

### Permission System

For fine-grained access control, use the permission system:

```python
from pydantic_ai_backends import LocalBackend
from pydantic_ai_backends.permissions import (
    DEFAULT_RULESET,
    READONLY_RULESET,
    PermissionRuleset,
    OperationPermissions,
    PermissionRule,
)

# Use pre-configured presets
backend = LocalBackend(root_dir="/workspace", permissions=DEFAULT_RULESET)

# Read-only permissions
backend = LocalBackend(root_dir="/workspace", permissions=READONLY_RULESET)

# Custom permissions
custom = PermissionRuleset(
    read=OperationPermissions(
        default="allow",
        rules=[
            PermissionRule(pattern="**/.env*", action="deny"),
        ],
    ),
    write=OperationPermissions(default="ask"),
    execute=OperationPermissions(
        default="deny",
        rules=[
            PermissionRule(pattern="git *", action="allow"),
            PermissionRule(pattern="python *", action="allow"),
        ],
    ),
)
backend = LocalBackend(root_dir="/workspace", permissions=custom)
```

See [Permissions](permissions.md) for full documentation.

### Features

- ✅ Python-native file operations (cross-platform)
- ✅ Optional shell execution via subprocess
- ✅ Directory restrictions with `allowed_directories`
- ✅ Fast grep using ripgrep (with Python fallback)
- ❌ No isolation - runs with your permissions

## StateBackend

In-memory storage - perfect for testing your pydantic-ai agents.

```python
import pytest
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai_backends import StateBackend, create_console_toolset

@dataclass
class Deps:
    backend: StateBackend

def test_agent_creates_file():
    """Test that agent can create files."""
    backend = StateBackend()
    toolset = create_console_toolset(include_execute=False)

    # Use TestModel for deterministic testing
    agent = Agent(TestModel(), deps_type=Deps).with_toolset(toolset)

    # Pre-populate files if needed
    backend.write("/data/input.txt", "test data")

    # Run agent
    result = agent.run_sync("Read input.txt", deps=Deps(backend=backend))

    # Verify files
    assert "/data/input.txt" in backend.files
```

### Features

- ✅ Fast - no disk I/O
- ✅ Isolated - no side effects
- ✅ Perfect for unit testing
- ✅ Access files via `backend.files`
- ❌ Data lost when process ends
- ❌ No command execution

## CompositeBackend

Route operations to different backends based on path prefix.

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import (
    CompositeBackend, StateBackend, LocalBackend, create_console_toolset
)

@dataclass
class Deps:
    backend: CompositeBackend

# Combine backends with routing
backend = CompositeBackend(
    default=StateBackend(),  # Default for unmatched paths
    routes={
        "/project/": LocalBackend("/my/project"),
        "/data/": LocalBackend("/shared/data", enable_execute=False),
    },
)

toolset = create_console_toolset()
agent = Agent("openai:gpt-4o", deps_type=Deps).with_toolset(toolset)

# Agent writes to /project/ go to LocalBackend
# Agent writes to /temp/ go to StateBackend (ephemeral)
result = agent.run_sync(
    "Read /data/config.json and write results to /temp/output.json",
    deps=Deps(backend=backend),
)
```

### Use Cases

- Persistent project files + ephemeral scratch space
- Multiple project directories
- Read-only data sources + writable outputs

## Backend Protocol

All backends implement this interface:

```python
class BackendProtocol(Protocol):
    def ls_info(self, path: str) -> list[FileInfo]:
        """List directory contents."""
        ...

    def read(self, path: str, offset: int = 0, limit: int = 2000) -> str:
        """Read file with line numbers."""
        ...

    def write(self, path: str, content: str | bytes) -> WriteResult:
        """Write file contents."""
        ...

    def edit(
        self, path: str, old_string: str, new_string: str, replace_all: bool = False
    ) -> EditResult:
        """Edit file by replacing strings."""
        ...

    def glob_info(self, pattern: str, path: str = ".") -> list[FileInfo]:
        """Find files matching glob pattern."""
        ...

    def grep_raw(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
        ignore_hidden: bool = True,
    ) -> list[GrepMatch] | str:
        """Search file contents with regex."""
        ...
```

### Execute (LocalBackend, DockerSandbox)

```python
def execute(self, command: str, timeout: int | None = None) -> ExecuteResponse:
    """Execute a shell command."""
    ...
```

## Path Security

All backends validate paths to prevent directory traversal:

```python
# These will fail:
backend.read("../etc/passwd")      # Parent directory
backend.read("~/secrets")          # Home expansion
backend.read("C:\\Windows\\...")   # Windows paths
```

## Next Steps

- [Permissions](permissions.md) - Fine-grained access control
- [Docker Sandbox](docker.md) - Isolated execution
- [Console Toolset](console-toolset.md) - Ready-to-use tools
- [API Reference](../api/backends.md) - Complete API
