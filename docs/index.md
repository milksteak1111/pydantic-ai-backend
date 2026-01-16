# pydantic-ai-backend

<p style="font-size: 1.3em; color: #888; margin-top: -0.5em;">
File storage and sandbox backends for pydantic-ai agents
</p>

[![PyPI version](https://img.shields.io/pypi/v/pydantic-ai-backend.svg)](https://pypi.org/project/pydantic-ai-backend/)
[![CI](https://github.com/vstorm-co/pydantic-ai-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/vstorm-co/pydantic-ai-backend/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/vstorm-co/pydantic-ai-backend/badge.svg?branch=main)](https://coveralls.io/github/vstorm-co/pydantic-ai-backend?branch=main)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

---

**pydantic-ai-backend** provides file storage, sandbox execution, and a ready-to-use console toolset for [pydantic-ai](https://ai.pydantic.dev/) agents. Give your AI agents the ability to read, write, and execute code safely.

## Why use pydantic-ai-backend?

When building [pydantic-ai](https://ai.pydantic.dev/) agents that work with files and execute code, you need storage, isolation, and security. **pydantic-ai-backend** provides:

<div class="feature-grid">
<div class="feature-card">
<h3>🔌 Plug & Play Toolset</h3>
<p>Ready-to-use pydantic-ai toolset with ls, read, write, edit, glob, grep, execute. Just add to your agent.</p>
</div>

<div class="feature-card">
<h3>🐳 Docker Isolation</h3>
<p>Execute code safely in Docker containers. Pre-configured runtimes for Python, Node.js, and more.</p>
</div>

<div class="feature-card">
<h3>📁 Multiple Backends</h3>
<p>In-memory (testing), local filesystem (CLI), Docker (production). Same interface, swap backends.</p>
</div>

<div class="feature-card">
<h3>👥 Multi-User Ready</h3>
<p>SessionManager for multi-user apps. Each user gets isolated storage and execution environment.</p>
</div>
</div>

## Quick Start

Add file and execution capabilities to any pydantic-ai agent:

```python
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_ai_backends import LocalBackend, create_console_toolset

@dataclass
class Deps:
    backend: LocalBackend

# Create backend and toolset
backend = LocalBackend(root_dir="/workspace")
toolset = create_console_toolset()

# Add toolset to your pydantic-ai agent
agent = Agent("openai:gpt-4o", deps_type=Deps)
agent = agent.with_toolset(toolset)

# Your agent can now read, write, and execute code!
result = agent.run_sync(
    "Create a fibonacci.py script and run it to show first 10 numbers",
    deps=Deps(backend=backend),
)
print(result.output)
```

## Choose Your Backend

Same toolset, different backends - swap based on your use case:

=== "Local Development"

    ```python
    from pydantic_ai_backends import LocalBackend

    # For CLI tools and local development
    backend = LocalBackend(root_dir="./workspace")
    ```

=== "Testing"

    ```python
    from pydantic_ai_backends import StateBackend

    # In-memory, no side effects
    backend = StateBackend()
    ```

=== "Production (Docker)"

    ```python
    from pydantic_ai_backends import DockerSandbox

    # Isolated execution in Docker
    backend = DockerSandbox(runtime="python-datascience")
    ```

=== "Multi-User"

    ```python
    from pydantic_ai_backends import SessionManager

    # Each user gets isolated sandbox
    manager = SessionManager(workspace_root="/app/workspaces")
    backend = await manager.get_or_create(user_id="alice")
    ```

## Available Tools

Your pydantic-ai agent gets these tools automatically:

| Tool | Description |
|------|-------------|
| `ls` | List files in a directory |
| `read_file` | Read file content with line numbers |
| `write_file` | Create or overwrite a file |
| `edit_file` | Replace strings in a file |
| `glob` | Find files matching a pattern |
| `grep` | Search for patterns in files |
| `execute` | Run shell commands (optional) |

## Backend Comparison

| Backend | Persistence | Execution | Best For |
|---------|-------------|-----------|----------|
| `LocalBackend` | Persistent | Yes | CLI tools, local dev |
| `StateBackend` | Ephemeral | No | Testing, mocking |
| `DockerSandbox` | Ephemeral* | Yes | Safe execution, multi-user |
| `CompositeBackend` | Mixed | Depends | Route by path prefix |

*DockerSandbox supports persistent volumes via `workspace_root` parameter.

## Related Projects

- **[pydantic-ai](https://github.com/pydantic/pydantic-ai)** - The foundation: Agent framework by Pydantic
- **[pydantic-deep](https://github.com/vstorm-co/pydantic-deep)** - Full deep agent framework (uses this library)
- **[pydantic-ai-todo](https://github.com/vstorm-co/pydantic-ai-todo)** - Task planning toolset

## Next Steps

<div class="feature-grid">
<div class="feature-card">
<h3>📖 Installation</h3>
<p>Get started in minutes.</p>
<a href="installation/">Installation Guide →</a>
</div>

<div class="feature-card">
<h3>🎓 Core Concepts</h3>
<p>Learn about backends and toolsets.</p>
<a href="concepts/">Core Concepts →</a>
</div>

<div class="feature-card">
<h3>📝 Examples</h3>
<p>See real-world examples.</p>
<a href="examples/">Examples →</a>
</div>

<div class="feature-card">
<h3>📚 API Reference</h3>
<p>Complete API documentation.</p>
<a href="api/">API Reference →</a>
</div>
</div>
