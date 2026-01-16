# API Reference

Complete API documentation for pydantic-ai-backend.

## Modules

| Module | Description |
|--------|-------------|
| [Backends](backends.md) | LocalBackend, StateBackend, CompositeBackend |
| [Docker](docker.md) | DockerSandbox, SessionManager, RuntimeConfig |
| [Toolsets](toolsets.md) | Console toolset for pydantic-ai |
| [Types](types.md) | Type definitions |

## Quick Import Reference

```python
# Backends
from pydantic_ai_backends import (
    LocalBackend,
    StateBackend,
    CompositeBackend,
)

# Docker
from pydantic_ai_backends import (
    DockerSandbox,
    SessionManager,
    RuntimeConfig,
    BUILTIN_RUNTIMES,
)

# Toolsets (requires [console] extra)
from pydantic_ai_backends import (
    create_console_toolset,
    get_console_system_prompt,
    ConsoleDeps,
)

# Types
from pydantic_ai_backends import (
    FileInfo,
    WriteResult,
    EditResult,
    ExecuteResponse,
    GrepMatch,
)

# Protocols
from pydantic_ai_backends import (
    BackendProtocol,
    SandboxProtocol,
)
```

## Protocols

### BackendProtocol

All backends implement this interface:

```python
class BackendProtocol(Protocol):
    def ls_info(self, path: str) -> list[FileInfo]: ...
    def read(self, path: str, offset: int = 0, limit: int = 2000) -> str: ...
    def write(self, path: str, content: str | bytes) -> WriteResult: ...
    def edit(self, path: str, old: str, new: str, replace_all: bool = False) -> EditResult: ...
    def glob_info(self, pattern: str, path: str = ".") -> list[FileInfo]: ...
    def grep_raw(self, pattern: str, path: str | None = None, glob: str | None = None) -> list[GrepMatch] | str: ...
```

### SandboxProtocol

Extends BackendProtocol with execution:

```python
class SandboxProtocol(BackendProtocol, Protocol):
    def execute(self, command: str, timeout: int | None = None) -> ExecuteResponse: ...
    @property
    def id(self) -> str: ...
```
