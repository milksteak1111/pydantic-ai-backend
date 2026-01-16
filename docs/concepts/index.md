# Core Concepts

pydantic-ai-backend provides three main components for building AI agents that work with files and execute code.

## Backends

Backends provide file storage and operations. All backends implement the same `BackendProtocol`:

```python
from pydantic_ai_backends import LocalBackend, StateBackend

# Local filesystem
backend = LocalBackend(root_dir="/workspace")

# In-memory (for testing)
backend = StateBackend()

# Common operations
backend.write("file.py", "print('hello')")
content = backend.read("file.py")
files = backend.glob_info("**/*.py")
matches = backend.grep_raw("hello")
```

[Learn more about Backends →](backends.md)

## Docker Sandbox

For safe code execution, `DockerSandbox` runs commands in isolated Docker containers:

```python
from pydantic_ai_backends import DockerSandbox

sandbox = DockerSandbox(image="python:3.12-slim")
sandbox.write("/workspace/app.py", "print(1+1)")
result = sandbox.execute("python /workspace/app.py")
print(result.output)  # "2"
sandbox.stop()
```

[Learn more about Docker →](docker.md)

## Console Toolset

The console toolset provides ready-to-use pydantic-ai tools for file operations:

```python
from pydantic_ai_backends import create_console_toolset, LocalBackend
from pydantic_ai import Agent
from dataclasses import dataclass

@dataclass
class Deps:
    backend: LocalBackend

toolset = create_console_toolset()
agent = Agent("openai:gpt-4o", deps_type=Deps).with_toolset(toolset)
```

Available tools: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute`

[Learn more about Console Toolset →](console-toolset.md)

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Your pydantic-ai Agent              │
├─────────────────────────────────────────────────┤
│              Console Toolset                     │
│   (ls, read, write, edit, glob, grep, execute)  │
├─────────────────────────────────────────────────┤
│                   Backend                        │
│  ┌─────────────┬──────────────┬──────────────┐  │
│  │ LocalBackend│ StateBackend │DockerSandbox │  │
│  │ (filesystem)│  (in-memory) │   (docker)   │  │
│  └─────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────┘
```

## Choosing a Backend

| Use Case | Backend |
|----------|---------|
| CLI tools, local dev | `LocalBackend` |
| Unit tests | `StateBackend` |
| Safe code execution | `DockerSandbox` |
| Multi-user web apps | `DockerSandbox` + `SessionManager` |
| Mixed (project + temp) | `CompositeBackend` |
