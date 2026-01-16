# Docker Sandbox Example

Build a pydantic-ai agent that safely executes code in Docker containers.

!!! warning "Requires Docker"
    ```bash
    pip install pydantic-ai-backend[docker]
    docker pull python:3.12-slim
    ```

## Quick Start

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import DockerSandbox, create_console_toolset

@dataclass
class Deps:
    backend: DockerSandbox

# Create sandbox with data science packages
sandbox = DockerSandbox(runtime="python-datascience")

try:
    # Add file tools to your agent
    toolset = create_console_toolset()
    agent = Agent("openai:gpt-4o", deps_type=Deps)
    agent = agent.with_toolset(toolset)

    # Agent can safely execute arbitrary code
    result = agent.run_sync(
        "Create a script that generates random data with numpy, "
        "analyzes it with pandas, and shows statistics",
        deps=Deps(backend=sandbox),
    )
    print(result.output)
finally:
    sandbox.stop()
```

## Data Science Agent

Build a code interpreter for data analysis:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import (
    DockerSandbox, create_console_toolset, get_console_system_prompt
)

@dataclass
class Deps:
    backend: DockerSandbox

sandbox = DockerSandbox(runtime="python-datascience")

try:
    toolset = create_console_toolset()
    agent = Agent(
        "openai:gpt-4o",
        system_prompt=f"""You are a data science assistant.
You can write and execute Python code to analyze data.
Available packages: pandas, numpy, matplotlib, scikit-learn, seaborn.

{get_console_system_prompt()}
""",
        deps_type=Deps,
    )
    agent = agent.with_toolset(toolset)

    # Complex data analysis task
    result = agent.run_sync(
        "Load the iris dataset from sklearn, "
        "create a classification model, "
        "and visualize the results",
        deps=Deps(backend=sandbox),
    )
    print(result.output)
finally:
    sandbox.stop()
```

## Pre-configured Runtimes

| Runtime | Packages | Use Case |
|---------|----------|----------|
| `python-minimal` | Clean Python 3.12 | General scripting |
| `python-datascience` | pandas, numpy, matplotlib, scikit-learn, seaborn | Data analysis |
| `python-web` | FastAPI, SQLAlchemy, httpx | Web development |
| `node-minimal` | Clean Node.js 20 | JavaScript |
| `node-react` | TypeScript, Vite, React | Frontend |

## Custom Runtime

```python
from pydantic_ai_backends import DockerSandbox, RuntimeConfig

runtime = RuntimeConfig(
    name="ml-env",
    base_image="python:3.12-slim",
    packages=["torch", "transformers", "datasets"],
    env_vars={"PYTHONUNBUFFERED": "1"},
)

sandbox = DockerSandbox(runtime=runtime)
```

## Persistent Storage

Save results between sessions:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import DockerSandbox, create_console_toolset

@dataclass
class Deps:
    backend: DockerSandbox

# Mount host directory for persistence
sandbox = DockerSandbox(
    runtime="python-datascience",
    volumes={
        "/host/results": "/workspace/results",
    },
)

try:
    toolset = create_console_toolset()
    agent = Agent("openai:gpt-4o", deps_type=Deps).with_toolset(toolset)

    result = agent.run_sync(
        "Analyze data and save results to /workspace/results/analysis.csv",
        deps=Deps(backend=sandbox),
    )
    # Results persist in /host/results/ after container stops
finally:
    sandbox.stop()
```

## Error Handling

The agent receives execution errors and can fix them:

```python
result = agent.run_sync(
    "Try to import a non-existent package, then fix the error",
    deps=Deps(backend=sandbox),
)
# Agent will see the ImportError and adapt
```

## Container Lifecycle

```python
sandbox = DockerSandbox(runtime="python-datascience")

# Container starts lazily on first operation
sandbox.write("/workspace/test.py", "print('hello')")

# Check if running
print(sandbox.is_alive())  # True

# Pre-warm container (useful before user requests)
sandbox.start()

# Clean up when done
sandbox.stop()
print(sandbox.is_alive())  # False
```
