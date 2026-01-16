# Docker API

## DockerSandbox

::: pydantic_ai_backends.backends.docker.sandbox.DockerSandbox
    options:
      show_root_heading: true
      members:
        - __init__
        - runtime
        - session_id
        - execute
        - read
        - write
        - ls_info
        - glob_info
        - grep_raw
        - start
        - stop
        - is_alive

## BaseSandbox

::: pydantic_ai_backends.backends.docker.sandbox.BaseSandbox
    options:
      show_root_heading: true
      members:
        - __init__
        - id
        - execute
        - ls_info
        - read
        - write
        - edit
        - glob_info
        - grep_raw

## SessionManager

::: pydantic_ai_backends.backends.docker.session.SessionManager
    options:
      show_root_heading: true
      members:
        - __init__
        - create_session
        - get_session
        - end_session

## RuntimeConfig

::: pydantic_ai_backends.types.RuntimeConfig
    options:
      show_root_heading: true

## Built-in Runtimes

```python
from pydantic_ai_backends import BUILTIN_RUNTIMES

# Available runtimes
print(BUILTIN_RUNTIMES.keys())
# dict_keys(['python-minimal', 'python-datascience', 'python-web', 'node-minimal', 'node-react'])

# Use a runtime
from pydantic_ai_backends import DockerSandbox
sandbox = DockerSandbox(runtime="python-datascience")
```

| Runtime | Base Image | Packages |
|---------|------------|----------|
| `python-minimal` | python:3.12-slim | (none) |
| `python-datascience` | python:3.12-slim | pandas, numpy, matplotlib, scikit-learn, seaborn |
| `python-web` | python:3.12-slim | fastapi, uvicorn, sqlalchemy, httpx |
| `node-minimal` | node:20-slim | (none) |
| `node-react` | node:20-slim | typescript, vite, react, react-dom, @types/react |
