# Docker Sandbox

`DockerSandbox` provides isolated code execution in Docker containers.

!!! warning "Requires Docker"
    Install Docker and ensure the daemon is running.

## Basic Usage

```python
from pydantic_ai_backends import DockerSandbox

sandbox = DockerSandbox(image="python:3.12-slim")

try:
    # Write and execute code
    sandbox.write("/workspace/hello.py", "print('Hello from Docker!')")
    result = sandbox.execute("python /workspace/hello.py")
    print(result.output)  # "Hello from Docker!"
finally:
    sandbox.stop()  # Clean up container
```

## Runtime Configurations

Pre-configured environments with packages pre-installed:

```python
from pydantic_ai_backends import DockerSandbox, RuntimeConfig

# Use built-in runtime
sandbox = DockerSandbox(runtime="python-datascience")

# Or define custom runtime
runtime = RuntimeConfig(
    name="ml-env",
    base_image="python:3.12-slim",
    packages=["torch", "transformers", "pandas"],
)
sandbox = DockerSandbox(runtime=runtime)
```

### Built-in Runtimes

| Runtime | Description |
|---------|-------------|
| `python-minimal` | Clean Python 3.12 |
| `python-datascience` | pandas, numpy, matplotlib, scikit-learn, seaborn |
| `python-web` | FastAPI, SQLAlchemy, httpx |
| `node-minimal` | Clean Node.js 20 |
| `node-react` | TypeScript, Vite, React |

## Persistent Storage

By default, files are lost when container stops. Use volumes for persistence:

```python
sandbox = DockerSandbox(
    image="python:3.12-slim",
    volumes={"/host/data": "/workspace/data"},  # Mount host directory
)
```

## SessionManager

For multi-user applications, `SessionManager` handles multiple isolated sandboxes:

```python
from pydantic_ai_backends import SessionManager

manager = SessionManager(
    image="python:3.12-slim",
    workspace_root="/app/workspaces",  # Persistent storage per user
)

# Create session for user
session_id = manager.create_session(user_id="alice")
sandbox = manager.get_session(session_id)

# User's files are isolated
sandbox.write("/workspace/secret.txt", "Alice's data")

# End session
manager.end_session(session_id)
```

### Architecture

```
                    ┌─────────────────┐
                    │ SessionManager  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│ DockerSandbox │   │ DockerSandbox │   │ DockerSandbox │
│   (User A)    │   │   (User B)    │   │   (User C)    │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Execution

```python
# Execute with timeout
result = sandbox.execute("python script.py", timeout=30)

print(result.output)      # stdout + stderr
print(result.exit_code)   # 0 = success
print(result.truncated)   # True if output was truncated
```

## File Operations

DockerSandbox implements the full `BackendProtocol`:

```python
# List files
files = sandbox.ls_info("/workspace")

# Read file
content = sandbox.read("/workspace/app.py")

# Write file
sandbox.write("/workspace/app.py", "print('hello')")

# Edit file
sandbox.edit("/workspace/app.py", "hello", "world")

# Search
matches = sandbox.grep_raw("def.*:", path="/workspace")
files = sandbox.glob_info("*.py", path="/workspace")
```

## Security

- Each user gets a separate Docker container
- Users cannot access each other's files
- Containers can have resource limits (CPU, memory)
- Network isolation available via Docker networking

## Next Steps

- [Multi-User Example](../examples/multi-user.md) - Web app with SessionManager
- [Docker Sandbox Example](../examples/docker-sandbox.md) - Full example
- [API Reference](../api/docker.md) - Complete API
