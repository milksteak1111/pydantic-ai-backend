"""Tests for DockerSandbox initialization (without running Docker)."""

import pytest


class TestDockerSandboxInit:
    """Tests for DockerSandbox initialization parameters."""

    def test_init_default_values(self):
        """Test default initialization values."""
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox.__new__(DockerSandbox)
        # Call __init__ manually to test parameter defaults
        sandbox.__init__()

        assert sandbox._image == "python:3.12-slim"
        assert sandbox._work_dir == "/workspace"
        assert sandbox._auto_remove is True
        assert sandbox._idle_timeout == 3600
        assert sandbox._volumes == {}
        assert sandbox._runtime is None

    def test_init_with_volumes(self):
        """Test initialization with volumes parameter."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {"/host/path": "/container/path"}
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes=volumes)

        assert sandbox._volumes == volumes

    def test_init_with_empty_volumes(self):
        """Test initialization with empty volumes dict."""
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes={})

        assert sandbox._volumes == {}

    def test_init_with_none_volumes(self):
        """Test initialization with None volumes (default)."""
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes=None)

        assert sandbox._volumes == {}

    def test_init_with_multiple_volumes(self):
        """Test initialization with multiple volume mappings."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {
            "/host/workspace": "/workspace",
            "/host/data": "/data",
            "/host/config": "/config",
        }
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes=volumes)

        assert sandbox._volumes == volumes
        assert len(sandbox._volumes) == 3

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters including volumes."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {"/host/path": "/workspace"}
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(
            image="python:3.11",
            sandbox_id="test-sandbox",
            work_dir="/app",
            auto_remove=False,
            idle_timeout=7200,
            volumes=volumes,
        )

        assert sandbox._image == "python:3.11"
        assert sandbox._id == "test-sandbox"
        assert sandbox._work_dir == "/app"
        assert sandbox._auto_remove is False
        assert sandbox._idle_timeout == 7200
        assert sandbox._volumes == volumes

    def test_init_with_session_id_alias(self):
        """Test that session_id works as alias for sandbox_id."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {"/host": "/container"}
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(session_id="my-session", volumes=volumes)

        assert sandbox._id == "my-session"
        assert sandbox._volumes == volumes


class TestDockerTimeoutEscaping:
    """Tests for timeout command escaping (fixes command!r bug).

    These tests verify that commands with quotes, variables, and pipes work
    correctly when timeout is specified. Previously failed due to command!r bug.
    """

    @pytest.mark.docker
    def test_execute_timeout_with_quotes(self):
        """Test execute with timeout handles quoted strings correctly.

        Previously failed because command!r added extra quotes:
        command = "echo 'hello world'"
        command!r = "'echo \\'hello world\\''"  # BAD - extra quotes
        """
        pytest.importorskip("docker")
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox()
        try:
            # Command with double quotes
            result = sandbox.execute('echo "hello world"', timeout=5)
            assert result.exit_code == 0
            assert "hello world" in result.output

            # Command with single quotes
            result = sandbox.execute("echo 'goodbye world'", timeout=5)
            assert result.exit_code == 0
            assert "goodbye world" in result.output
        finally:
            sandbox.stop()

    @pytest.mark.docker
    def test_execute_timeout_with_variables(self):
        """Test execute with timeout handles shell variables correctly.

        Previously failed because command!r escaped $ incorrectly:
        command = "echo $HOME"
        command!r = "'echo $HOME'"  # $ gets escaped/not expanded
        """
        pytest.importorskip("docker")
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox()
        try:
            # Shell variable expansion
            result = sandbox.execute("echo $HOME", timeout=5)
            assert result.exit_code == 0
            # HOME should be expanded (not literal "$HOME")
            assert "$HOME" not in result.output or result.output.strip() != "$HOME"

            # Command substitution
            result = sandbox.execute("echo $(pwd)", timeout=5)
            assert result.exit_code == 0
            assert result.output.strip()  # Should output the working directory
        finally:
            sandbox.stop()

    @pytest.mark.docker
    def test_execute_timeout_with_pipes(self):
        """Test execute with timeout handles pipes and redirects correctly.

        Previously failed because command!r broke shell piping:
        command = "echo test | grep test"
        command!r = "'echo test | grep test'"  # Pipe becomes literal string
        """
        pytest.importorskip("docker")
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox()
        try:
            # Pipe command
            result = sandbox.execute("echo 'test line' | grep test", timeout=5)
            assert result.exit_code == 0
            assert "test line" in result.output

            # Multiple pipes
            result = sandbox.execute("echo 'hello world' | tr a-z A-Z | grep HELLO", timeout=5)
            assert result.exit_code == 0
            assert "HELLO WORLD" in result.output
        finally:
            sandbox.stop()
