# Permissions

The permission system provides fine-grained access control for file operations and shell commands. It uses pattern-based rules to allow, deny, or require approval for specific operations.

## Quick Start

```python
from pydantic_ai_backends import LocalBackend
from pydantic_ai_backends.permissions import DEFAULT_RULESET

# Use the default safe ruleset
backend = LocalBackend(
    root_dir="/workspace",
    permissions=DEFAULT_RULESET,
)

# Reads are allowed (except secrets)
content = backend.read("app.py")  # Works

# Writes require approval (in sync context, denied by default)
result = backend.write("output.txt", "data")  # Denied without callback
```

## Permission Actions

Each operation can result in one of three actions:

| Action | Behavior |
|--------|----------|
| `allow` | Operation proceeds immediately |
| `deny` | Operation is blocked with an error |
| `ask` | Requires user approval via callback |

## Pre-configured Presets

### DEFAULT_RULESET

Safe defaults for development environments:

- **Read**: Allowed, except for secrets (`.env`, `.pem`, `credentials`, etc.)
- **Write/Edit**: Requires approval
- **Execute**: Requires approval, dangerous commands blocked
- **Glob/Grep/Ls**: Allowed

```python
from pydantic_ai_backends.permissions import DEFAULT_RULESET

backend = LocalBackend(root_dir="/workspace", permissions=DEFAULT_RULESET)
```

### PERMISSIVE_RULESET

For trusted environments where most operations should succeed:

- **Read**: Allowed, except secrets
- **Write/Edit**: Allowed, except secrets and system files
- **Execute**: Allowed, dangerous commands blocked
- **Glob/Grep/Ls**: Allowed

```python
from pydantic_ai_backends.permissions import PERMISSIVE_RULESET

backend = LocalBackend(root_dir="/workspace", permissions=PERMISSIVE_RULESET)
```

### READONLY_RULESET

For read-only access:

- **Read**: Allowed, except secrets
- **Write/Edit/Execute**: Denied
- **Glob/Grep/Ls**: Allowed

```python
from pydantic_ai_backends.permissions import READONLY_RULESET

backend = LocalBackend(root_dir="/workspace", permissions=READONLY_RULESET)
```

### STRICT_RULESET

Everything requires explicit approval:

- **All operations**: Require approval
- **Secrets**: Denied

```python
from pydantic_ai_backends.permissions import STRICT_RULESET

backend = LocalBackend(root_dir="/workspace", permissions=STRICT_RULESET)
```

## Custom Rulesets

### Using create_ruleset()

Quick factory for common configurations:

```python
from pydantic_ai_backends.permissions import create_ruleset

# Allow reads and writes, but ask for execute
ruleset = create_ruleset(
    allow_read=True,
    allow_write=True,
    allow_execute=False,  # Will require approval
    deny_secrets=True,     # Block access to sensitive files
)
```

### Full Custom Configuration

For complete control, build a `PermissionRuleset`:

```python
from pydantic_ai_backends.permissions import (
    PermissionRuleset,
    OperationPermissions,
    PermissionRule,
)

custom_permissions = PermissionRuleset(
    default="deny",  # Global default for unconfigured operations

    read=OperationPermissions(
        default="allow",
        rules=[
            # Deny access to secrets
            PermissionRule(
                pattern="**/.env*",
                action="deny",
                description="Protect environment files",
            ),
            PermissionRule(
                pattern="**/secrets/**",
                action="deny",
                description="Protect secrets directory",
            ),
        ],
    ),

    write=OperationPermissions(
        default="ask",
        rules=[
            # Auto-allow Python files
            PermissionRule(pattern="**/*.py", action="allow"),
            # Auto-allow markdown
            PermissionRule(pattern="**/*.md", action="allow"),
        ],
    ),

    execute=OperationPermissions(
        default="deny",
        rules=[
            # Allow safe git commands
            PermissionRule(pattern="git status", action="allow"),
            PermissionRule(pattern="git diff*", action="allow"),
            PermissionRule(pattern="git log*", action="allow"),
            # Allow Python execution
            PermissionRule(pattern="python *", action="allow"),
            PermissionRule(pattern="pytest *", action="allow"),
        ],
    ),

    # Allow all search operations
    glob=OperationPermissions(default="allow"),
    grep=OperationPermissions(default="allow"),
    ls=OperationPermissions(default="allow"),
)
```

## Pattern Syntax

Patterns use glob-style matching:

| Pattern | Matches |
|---------|---------|
| `*` | Any characters except `/` |
| `**` | Any characters including `/` (recursive) |
| `?` | Any single character |
| `[abc]` | Any character in the set |
| `[!abc]` | Any character not in the set |

### Examples

```python
# Match .env files anywhere
PermissionRule(pattern="**/.env", action="deny")

# Match all .env* files (including .env.local, .env.production)
PermissionRule(pattern="**/.env*", action="deny")

# Match files in secrets directory
PermissionRule(pattern="**/secrets/**", action="deny")

# Match specific command
PermissionRule(pattern="rm -rf *", action="deny")

# Match command prefix
PermissionRule(pattern="git *", action="allow")
```

## Ask Callback

For interactive approval, provide an `ask_callback`:

```python
async def my_approval_callback(
    operation: str,  # "read", "write", "edit", "execute", etc.
    target: str,     # Path or command
    reason: str,     # Why approval is needed
) -> bool:
    # Your approval logic here
    response = input(f"Allow {operation} on {target}? [y/N] ")
    return response.lower() == "y"

backend = LocalBackend(
    root_dir="/workspace",
    permissions=DEFAULT_RULESET,
    ask_callback=my_approval_callback,
)
```

### Ask Fallback

When no callback is provided, `ask_fallback` controls behavior:

```python
# Deny operations that need approval (default behavior)
backend = LocalBackend(
    permissions=DEFAULT_RULESET,
    ask_fallback="deny",
)

# Raise PermissionError for operations that need approval
backend = LocalBackend(
    permissions=DEFAULT_RULESET,
    ask_fallback="error",
)
```

## Integration with LocalBackend

Permissions are checked after `allowed_directories`:

```python
backend = LocalBackend(
    root_dir="/workspace",
    allowed_directories=["/workspace", "/data"],  # Checked first
    permissions=DEFAULT_RULESET,                   # Checked second
)

# Path must pass BOTH checks:
# 1. Is the path within allowed_directories?
# 2. Does the permission ruleset allow this operation?
```

## Integration with Console Toolset

Pass permissions to the toolset:

```python
from pydantic_ai_backends import create_console_toolset
from pydantic_ai_backends.permissions import DEFAULT_RULESET

# Toolset uses permissions to determine approval requirements
toolset = create_console_toolset(permissions=DEFAULT_RULESET)
```

When `permissions` is provided, the legacy `require_write_approval` and `require_execute_approval` flags are ignored.

## PermissionChecker

For programmatic permission checking:

```python
from pydantic_ai_backends.permissions import PermissionChecker, DEFAULT_RULESET

checker = PermissionChecker(ruleset=DEFAULT_RULESET)

# Synchronous check (returns action without asking)
action = checker.check_sync("read", "/path/to/file.txt")
# Returns: "allow", "deny", or "ask"

# Convenience methods
if checker.is_allowed("read", "/path/to/file.txt"):
    print("Read is allowed")

if checker.is_denied("write", "/etc/passwd"):
    print("Write is denied")

if checker.requires_approval("execute", "rm -rf /tmp/*"):
    print("Execute requires approval")
```

## Built-in Patterns

The presets use these common patterns:

### SECRETS_PATTERNS

```python
SECRETS_PATTERNS = [
    "**/.env",
    "**/.env.*",
    "**/*.pem",
    "**/*.key",
    "**/*.crt",
    "**/credentials*",
    "**/secrets*",
    "**/*secret*",
    "**/*password*",
    "**/.aws/**",
    "**/.ssh/**",
    "**/.gnupg/**",
]
```

### SYSTEM_PATTERNS

```python
SYSTEM_PATTERNS = [
    "/etc/**",
    "/var/**",
    "/usr/**",
    "/bin/**",
    "/sbin/**",
    "/boot/**",
    "/sys/**",
    "/proc/**",
]
```

## Next Steps

- [Backends](backends.md) - Backend configuration
- [Console Toolset](console-toolset.md) - Tool configuration
- [API Reference](../api/permissions.md) - Complete API
