# Backends

Backends provide file storage and operations for AI agents. All backends implement `BackendProtocol`.

## Available Backends

| Backend | Persistence | Execution | Use Case |
|---------|-------------|-----------|----------|
| `LocalBackend` | Persistent | Yes | CLI tools, local development |
| `StateBackend` | Ephemeral | No | Testing, temporary files |
| `DockerSandbox` | Ephemeral* | Yes | Safe code execution |
| `CompositeBackend` | Mixed | Depends | Route by path prefix |

## LocalBackend

Local filesystem operations with optional shell execution. Python-native, cross-platform.

```python
from pydantic_ai_backends import LocalBackend

# Full access with shell
backend = LocalBackend(root_dir="/workspace")
backend.write("app.py", "print('hello')")
result = backend.execute("python app.py")
print(result.output)  # "hello"

# Restricted directories
backend = LocalBackend(
    allowed_directories=["/home/user/project", "/home/user/data"],
    enable_execute=True,
)

# Read-only mode (no shell)
backend = LocalBackend(
    root_dir="/workspace",
    enable_execute=False,
)
```

### Features

- ✅ Python-native file operations (cross-platform)
- ✅ Optional shell execution via subprocess
- ✅ Directory restrictions with `allowed_directories`
- ✅ Fast grep using ripgrep (with Python fallback)
- ❌ No isolation - runs with your permissions

## StateBackend

In-memory storage, ideal for testing.

```python
from pydantic_ai_backends import StateBackend

backend = StateBackend()
backend.write("/src/app.py", "print('hello')")
print(backend.read("/src/app.py"))

# Access all files
print(backend.files.keys())
```

### Features

- ✅ Fast - no disk I/O
- ✅ Isolated - no side effects
- ✅ Perfect for testing
- ❌ Data lost when process ends
- ❌ No command execution

## CompositeBackend

Route operations to different backends based on path prefix.

```python
from pydantic_ai_backends import CompositeBackend, StateBackend, LocalBackend

backend = CompositeBackend(
    default=StateBackend(),  # Default for unmatched paths
    routes={
        "/project/": LocalBackend("/my/project"),
        "/data/": LocalBackend("/shared/data", enable_execute=False),
    },
)

# Routes to LocalBackend
backend.write("/project/app.py", "...")

# Routes to StateBackend (default)
backend.write("/temp/scratch.txt", "...")
```

### Use Cases

- Persistent project files + ephemeral scratch space
- Multiple project directories
- Read-only data + writable outputs

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
        self, pattern: str, path: str | None = None, glob: str | None = None
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

- [Docker Sandbox](docker.md) - Isolated execution
- [Console Toolset](console-toolset.md) - Ready-to-use tools
- [API Reference](../api/backends.md) - Complete API
