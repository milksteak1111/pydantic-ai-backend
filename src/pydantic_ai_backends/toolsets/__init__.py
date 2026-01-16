"""Toolsets for pydantic-ai agents."""

from pydantic_ai_backends.toolsets.console import (
    CONSOLE_SYSTEM_PROMPT,
    ConsoleDeps,
    ConsoleToolset,
    create_console_toolset,
    get_console_system_prompt,
)

__all__ = [
    "CONSOLE_SYSTEM_PROMPT",
    "ConsoleDeps",
    "ConsoleToolset",
    "create_console_toolset",
    "get_console_system_prompt",
]
