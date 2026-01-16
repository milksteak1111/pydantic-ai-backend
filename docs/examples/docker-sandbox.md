# Docker Sandbox Example

`DockerSandbox` runs code in isolated Docker containers.

!!! warning "Requires Docker"
    ```bash
    pip install pydantic-ai-backend[docker]
    docker pull python:3.12-slim
    ```

## Basic Usage

```python
from pydantic_ai_backends import DockerSandbox

# Create sandbox
sandbox = DockerSandbox(image="python:3.12-slim")

try:
    # Write code
    sandbox.write("/workspace/app.py", """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(fibonacci(i), end=' ')
""")

    # Execute
    result = sandbox.execute("python /workspace/app.py")
    print(result.output)  # 0 1 1 2 3 5 8 13 21 34

finally:
    sandbox.stop()  # Clean up container
```

## Pre-configured Runtimes

```python
from pydantic_ai_backends import DockerSandbox

# Data science environment
sandbox = DockerSandbox(runtime="python-datascience")

sandbox.write("/workspace/analysis.py", """
import pandas as pd
import numpy as np

data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
})
print(data.describe())
""")

result = sandbox.execute("python /workspace/analysis.py")
print(result.output)
```

### Available Runtimes

| Runtime | Packages |
|---------|----------|
| `python-minimal` | Clean Python 3.12 |
| `python-datascience` | pandas, numpy, matplotlib, scikit-learn, seaborn |
| `python-web` | FastAPI, SQLAlchemy, httpx |
| `node-minimal` | Clean Node.js 20 |
| `node-react` | TypeScript, Vite, React |

## Custom Runtime

```python
from pydantic_ai_backends import DockerSandbox, RuntimeConfig

runtime = RuntimeConfig(
    name="ml-env",
    base_image="python:3.12-slim",
    packages=["torch", "transformers"],
    env_vars={"PYTHONUNBUFFERED": "1"},
)

sandbox = DockerSandbox(runtime=runtime)
```

## Persistent Storage

```python
# Mount host directory for persistence
sandbox = DockerSandbox(
    image="python:3.12-slim",
    volumes={
        "/host/data": "/workspace/data",
    },
)

# Files in /workspace/data persist after container stops
sandbox.write("/workspace/data/results.txt", "Important data")
sandbox.stop()

# Data still available in /host/data/results.txt
```

## With pydantic-ai

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import DockerSandbox, create_console_toolset

@dataclass
class Deps:
    backend: DockerSandbox

sandbox = DockerSandbox(runtime="python-datascience")

try:
    toolset = create_console_toolset()
    agent = Agent("openai:gpt-4o", deps_type=Deps)
    agent = agent.with_toolset(toolset)

    result = agent.run_sync(
        "Create a script that generates a random dataset and calculates statistics",
        deps=Deps(backend=sandbox),
    )
    print(result.output)
finally:
    sandbox.stop()
```

## Error Handling

```python
result = sandbox.execute("python nonexistent.py", timeout=10)

if result.exit_code != 0:
    print(f"Command failed (exit {result.exit_code})")
    print(result.output)

if result.truncated:
    print("Output was truncated (too long)")
```

## Container Lifecycle

```python
sandbox = DockerSandbox(image="python:3.12-slim")

# Container starts lazily on first operation
sandbox.write("/workspace/test.py", "print('hello')")

# Check if running
print(sandbox.is_alive())  # True

# Explicitly start (useful for pre-warming)
sandbox.start()

# Stop and remove
sandbox.stop()
print(sandbox.is_alive())  # False
```
