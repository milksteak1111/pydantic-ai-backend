"""Tests for console toolset."""

import inspect
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai_backends import (
    LocalBackend,
    StateBackend,
    create_console_toolset,
    get_console_system_prompt,
)
from pydantic_ai_backends.toolsets.console import ConsoleDeps


@dataclass
class MockDeps:
    """Mock deps for testing."""

    backend: LocalBackend | StateBackend


class TestConsoleDeps:
    """Test ConsoleDeps protocol."""

    def test_mock_deps_implements_protocol(self, tmp_path: Path):
        """Test that MockDeps implements ConsoleDeps."""
        backend = LocalBackend(root_dir=tmp_path)
        deps = MockDeps(backend=backend)

        # Should be instance of ConsoleDeps (runtime checkable protocol)
        assert isinstance(deps, ConsoleDeps)

    def test_state_backend_implements_protocol(self):
        """Test that StateBackend works with ConsoleDeps."""
        backend = StateBackend()
        deps = MockDeps(backend=backend)
        assert isinstance(deps, ConsoleDeps)


class TestCreateConsoleToolset:
    """Test create_console_toolset function."""

    def test_create_default_toolset(self):
        """Test creating toolset with default settings."""
        toolset = create_console_toolset()

        # Should have all standard tools
        tool_names = list(toolset.tools.keys())
        assert "ls" in tool_names
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "edit_file" in tool_names
        assert "glob" in tool_names
        assert "grep" in tool_names
        assert "execute" in tool_names

    def test_create_toolset_without_execute(self):
        """Test creating toolset without execute tool."""
        toolset = create_console_toolset(include_execute=False)

        tool_names = list(toolset.tools.keys())
        assert "ls" in tool_names
        assert "read_file" in tool_names
        assert "execute" not in tool_names

    def test_create_toolset_with_custom_id(self):
        """Test creating toolset with custom ID."""
        toolset = create_console_toolset(id="my-console")
        assert toolset.id == "my-console"

    def test_tool_approval_settings(self):
        """Test tool approval settings."""
        # Default: write doesn't require approval, execute does
        toolset = create_console_toolset()

        # Verify toolset was created with expected tools
        assert "write_file" in toolset.tools
        assert "execute" in toolset.tools

        # Check requires_approval setting on execute tool
        assert toolset.tools["execute"].requires_approval is True

    def test_toolset_with_write_approval(self):
        """Test toolset with write approval required."""
        toolset = create_console_toolset(require_write_approval=True)

        assert "write_file" in toolset.tools
        assert "edit_file" in toolset.tools

        # Check requires_approval setting
        assert toolset.tools["write_file"].requires_approval is True
        assert toolset.tools["edit_file"].requires_approval is True

    def test_toolset_default_ignore_hidden_configurable(self):
        """Grep should respect default ignore hidden flag."""
        toolset = create_console_toolset(default_ignore_hidden=False)

        assert hasattr(toolset, "_console_default_ignore_hidden")
        assert toolset._console_default_ignore_hidden is False

        grep_impl = toolset._console_grep_impl
        params = inspect.signature(grep_impl).parameters
        assert params["ignore_hidden"].default is False


class TestGetConsoleSystemPrompt:
    """Test get_console_system_prompt function."""

    def test_returns_string(self):
        """Test that system prompt returns a string."""
        prompt = get_console_system_prompt()
        assert isinstance(prompt, str)

    def test_contains_tool_descriptions(self):
        """Test that system prompt contains tool descriptions."""
        prompt = get_console_system_prompt()

        # Should mention file operations
        assert "ls" in prompt.lower() or "list" in prompt.lower()
        assert "read" in prompt.lower()
        assert "write" in prompt.lower()
        assert "edit" in prompt.lower()

        # Should mention shell execution
        assert "execute" in prompt.lower() or "shell" in prompt.lower()


class TestConsoleToolsetAlias:
    """Test ConsoleToolset alias."""

    def test_alias_works(self):
        """Test that ConsoleToolset alias works."""
        from pydantic_ai_backends.toolsets.console import ConsoleToolset

        toolset = ConsoleToolset()
        assert len(toolset.tools) > 0
