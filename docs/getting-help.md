# Getting Help

## Documentation

This documentation is your primary resource. Use the search bar (press `/` or `s`) to find specific topics.

## GitHub Issues

For bugs, feature requests, or questions:

[:fontawesome-brands-github: Open an Issue](https://github.com/vstorm-co/pydantic-ai-backend/issues){ .md-button }

### Before Opening an Issue

1. **Search existing issues** - Your problem may already be reported
2. **Check the docs** - The answer might be here
3. **Prepare a minimal example** - Help us reproduce the issue

### Bug Report Template

```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. Create backend with...
2. Call method...
3. Observe error...

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- pydantic-ai-backend version: X.X.X
- pydantic-ai version: X.X.X
- Python version: 3.XX
- OS: [e.g., macOS 14.0, Ubuntu 22.04]
- Docker version (if using DockerSandbox): X.X.X
```

## Community Resources

### Pydantic AI

pydantic-ai-backend is designed for use with Pydantic AI. Their documentation is an excellent resource:

- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [Pydantic AI GitHub](https://github.com/pydantic/pydantic-ai)

### Related Projects

- [pydantic-deep](https://github.com/vstorm-co/pydantic-deep) - Full agent framework
- [pydantic-ai-todo](https://github.com/vstorm-co/pydantic-ai-todo) - Task planning toolset
- [subagents-pydantic-ai](https://github.com/vstorm-co/subagents-pydantic-ai) - Multi-agent orchestration
- [summarization-pydantic-ai](https://github.com/vstorm-co/summarization-pydantic-ai) - Context management

## FAQ

### Which backend should I use?

| Use Case | Backend |
|----------|---------|
| Unit tests | `StateBackend` (in-memory, fast) |
| Local CLI tools | `LocalBackend` (persistent files) |
| Multi-user web apps | `DockerSandbox` + `SessionManager` |
| Untrusted code | `DockerSandbox` (isolated) |
| Mixed sources | `CompositeBackend` (route by path) |

### How do I run without Docker?

Use `LocalBackend` for local filesystem operations:

```python
from pydantic_ai_backends import LocalBackend

backend = LocalBackend(root_dir="./workspace")
```

For testing, use `StateBackend`:

```python
from pydantic_ai_backends import StateBackend

backend = StateBackend()  # In-memory, no side effects
```

### How do I disable shell execution?

For `LocalBackend`:

```python
backend = LocalBackend(root_dir="./workspace", enable_execute=False)
```

For the console toolset:

```python
toolset = create_console_toolset(include_execute=False)
```

### How do I restrict file access?

Use the permission system:

```python
from pydantic_ai_backends import LocalBackend
from pydantic_ai_backends.permissions import READONLY_RULESET

backend = LocalBackend(root_dir="/workspace", permissions=READONLY_RULESET)
```

Or use `allowed_directories`:

```python
backend = LocalBackend(
    root_dir="/workspace",
    allowed_directories=["/workspace", "/shared"],
)
```

### Docker container won't start

1. Ensure Docker is running: `docker info`
2. Check image exists: `docker images`
3. Pull if needed: `docker pull python:3.12-slim`
4. On Linux, check permissions: `sudo usermod -aG docker $USER`

## Contributing

We welcome contributions! See our [Contributing Guide](https://github.com/vstorm-co/pydantic-ai-backend/blob/main/CONTRIBUTING.md) for details.
