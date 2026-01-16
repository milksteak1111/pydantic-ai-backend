# Local Backend Example

`LocalBackend` provides local filesystem operations with optional shell execution.

## Basic Usage

```python
from pydantic_ai_backends import LocalBackend

# Create backend
backend = LocalBackend(root_dir="/workspace")

# Write a file
backend.write("hello.py", "print('Hello, World!')")

# Read it back
content = backend.read("hello.py")
print(content)
#      1	print('Hello, World!')

# Execute it
result = backend.execute("python hello.py")
print(result.output)  # Hello, World!
```

## File Operations

### List Files

```python
files = backend.ls_info(".")
for f in files:
    if f["is_dir"]:
        print(f"[DIR]  {f['name']}")
    else:
        print(f"[FILE] {f['name']} ({f['size']} bytes)")
```

### Read with Pagination

```python
# Read first 50 lines
content = backend.read("large_file.py", offset=0, limit=50)

# Read lines 100-150
content = backend.read("large_file.py", offset=100, limit=50)
```

### Edit File

```python
# Replace single occurrence (must be unique)
result = backend.edit("app.py", "old_text", "new_text")

# Replace all occurrences
result = backend.edit("app.py", "old_text", "new_text", replace_all=True)

if result.error:
    print(f"Error: {result.error}")
else:
    print(f"Replaced {result.occurrences} occurrence(s)")
```

### Search Files

```python
# Find Python files
py_files = backend.glob_info("**/*.py", ".")
for f in py_files:
    print(f["path"])

# Search for pattern
matches = backend.grep_raw(r"def \w+\(", path=".")
for m in matches:
    print(f"{m['path']}:{m['line_number']}: {m['line']}")
```

## Security Options

### Restricted Directories

```python
# Only allow access to specific directories
backend = LocalBackend(
    allowed_directories=[
        "/home/user/project",
        "/home/user/data",
    ],
)

# This works
backend.read("/home/user/project/app.py")

# This fails
backend.read("/etc/passwd")  # Error: path not allowed
```

### Disable Execution

```python
# Read-only mode - no shell access
backend = LocalBackend(
    root_dir="/workspace",
    enable_execute=False,
)

backend.read("file.py")      # OK
backend.execute("ls")        # Error: execution disabled
```

## With pydantic-ai

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import LocalBackend, create_console_toolset

@dataclass
class Deps:
    backend: LocalBackend

# Create backend with restrictions
backend = LocalBackend(
    root_dir="/workspace",
    allowed_directories=["/workspace"],
    enable_execute=True,
)

# Create toolset and agent
toolset = create_console_toolset()
agent = Agent(
    "openai:gpt-4o",
    deps_type=Deps,
    system_prompt="You are a helpful coding assistant.",
)
agent = agent.with_toolset(toolset)

# Run
result = agent.run_sync(
    "Create a fibonacci function in Python and test it",
    deps=Deps(backend=backend),
)
print(result.output)
```

## Full CLI Example

See [`examples/local_cli/`](https://github.com/vstorm-co/pydantic-ai-backend/tree/main/examples/local_cli) for a complete interactive CLI agent.

```bash
cd examples/local_cli
pip install pydantic-ai-backend[console]
python cli_agent.py --dir ~/myproject
```
