# Examples

Working examples for different use cases.

## Getting Started

| Example | Description |
|---------|-------------|
| [Local Backend](local-backend.md) | File operations with LocalBackend |
| [Docker Sandbox](docker-sandbox.md) | Isolated execution with Docker |

## Applications

| Example | Description |
|---------|-------------|
| [CLI Agent](cli-agent.md) | Interactive CLI coding assistant |
| [Multi-User Web App](multi-user.md) | FastAPI server with user isolation |

## Full Examples

Complete working examples are available in the [`examples/`](https://github.com/vstorm-co/pydantic-ai-backend/tree/main/examples) directory:

| Directory | Description |
|-----------|-------------|
| `local_cli/` | CLI agent with LocalBackend |
| `web_production/` | Multi-user web app with Docker |

## Quick Reference

### LocalBackend (CLI)

```python
from pydantic_ai_backends import LocalBackend

backend = LocalBackend(root_dir="/workspace")
backend.write("hello.py", "print('hello')")
result = backend.execute("python hello.py")
```

### DockerSandbox (Isolated)

```python
from pydantic_ai_backends import DockerSandbox

sandbox = DockerSandbox(image="python:3.12-slim")
sandbox.write("/workspace/app.py", "print(1+1)")
result = sandbox.execute("python /workspace/app.py")
sandbox.stop()
```

### Console Toolset (pydantic-ai)

```python
from pydantic_ai_backends import LocalBackend, create_console_toolset
from pydantic_ai import Agent
from dataclasses import dataclass

@dataclass
class Deps:
    backend: LocalBackend

toolset = create_console_toolset()
agent = Agent("openai:gpt-4o", deps_type=Deps).with_toolset(toolset)
```

### Multi-User (SessionManager)

```python
from pydantic_ai_backends import SessionManager

manager = SessionManager(image="python:3.12-slim")
session_id = manager.create_session(user_id="alice")
sandbox = manager.get_session(session_id)
# Each user gets isolated container
```
