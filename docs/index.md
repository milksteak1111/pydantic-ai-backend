# pydantic-ai-backend

<p style="font-size: 1.3em; color: #888; margin-top: -0.5em;">
File storage and sandbox backends for AI agents
</p>

[![PyPI version](https://img.shields.io/pypi/v/pydantic-ai-backend.svg)](https://pypi.org/project/pydantic-ai-backend/)
[![CI](https://github.com/vstorm-co/pydantic-ai-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/vstorm-co/pydantic-ai-backend/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/vstorm-co/pydantic-ai-backend/badge.svg?branch=main)](https://coveralls.io/github/vstorm-co/pydantic-ai-backend?branch=main)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

---

**pydantic-ai-backend** provides file storage, sandbox execution, and a ready-to-use console toolset for [Pydantic AI](https://ai.pydantic.dev/) agents.

## Why use pydantic-ai-backend?

Building AI agents that work with files and execute code requires careful handling of storage, isolation, and security. pydantic-ai-backend provides:

<div class="feature-grid">
<div class="feature-card">
<h3>📁 File Storage</h3>
<p>Multiple backends: in-memory, local filesystem, Docker. Read, write, edit with glob and grep support.</p>
</div>

<div class="feature-card">
<h3>🐳 Docker Isolation</h3>
<p>Execute code safely in Docker containers. Pre-configured runtimes for Python, Node.js, and more.</p>
</div>

<div class="feature-card">
<h3>🛠️ Console Toolset</h3>
<p>Ready-to-use pydantic-ai tools: ls, read, write, edit, glob, grep, execute. Just plug and play.</p>
</div>

<div class="feature-card">
<h3>👥 Multi-User</h3>
<p>SessionManager for multi-user apps. Each user gets isolated storage and execution environment.</p>
</div>
</div>

## Quick Start

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

# Create agent with console tools
agent = Agent("openai:gpt-4o", deps_type=Deps)
agent = agent.with_toolset(toolset)

# Run agent
result = agent.run_sync(
    "Create a hello.py script and run it",
    deps=Deps(backend=backend),
)
print(result.output)
```

## Key Features

| Feature | Description |
|---------|-------------|
| **LocalBackend** | Local filesystem + shell execution |
| **StateBackend** | In-memory storage for testing |
| **DockerSandbox** | Isolated Docker container execution |
| **CompositeBackend** | Route operations by path prefix |
| **Console Toolset** | Ready-to-use pydantic-ai tools |
| **SessionManager** | Multi-user session management |
| **RuntimeConfig** | Pre-configured Docker environments |

## Available Backends

| Backend | Persistence | Execution | Use Case |
|---------|-------------|-----------|----------|
| `LocalBackend` | Persistent | Yes | CLI tools, local development |
| `StateBackend` | Ephemeral | No | Testing, temporary files |
| `DockerSandbox` | Ephemeral* | Yes | Safe code execution, multi-user |
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
